from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import gauth, openai







app = Flask(__name__)
app.config['SECRET_KEY'] = 'ecohaul'
app.app_context()

engine = create_engine("mssql+pyodbc://Hiren/ecohaul?driver=SQL+Server", echo=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://Hiren/ecohaul?driver=SQL+Server'


openai.api_key = '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'

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

db = SQLAlchemy(app)







class User(db.Model):
    __tablename__ = 'UserRegistrations'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_or_phone = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128))
    drivers_license = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    
class User2(db.Model):
    __tablename__ = 'CivilianComplaintReport'
    Co_id = db.Column(db.Integer, primary_key=True)
    Co_desc = db.Column(db.String(100), nullable=False)
    Co_date = db.Column(db.DateTime, nullable=False)
    M_id = db.Column(db.Integer, nullable=False)
    Co_address = db.Column(db.String(200), nullable=False)
    ##This is when you have vlid private key in database
    #user_id = db.Column(db.Integer, db.ForeignKey('UserRegistrations.user_id'), nullable=False)

class User3(db.Model):
    __tablename__ = 'Complaints'
    C_id = db.Column(db.Integer, primary_key=True)
    C_category = db.Column(db.String(100), nullable=False)
    C_desc = db.Column(db.String(100), nullable=False)
    C_date = db.Column(db.DateTime, nullable=False)
    ##This is when you have vlid private key in database
    #user_id = db.Column(db.Integer, db.ForeignKey('UserRegistrations.user_id'), nullable=False)

class User4(db.Model):
    __tablename__ = 'ProductDetails'
    PD_id = db.Column(db.Integer, primary_key=True)
    PD_price = db.Column(db.Integer, nullable=False)
    PD_desc = db.Column(db.String(100), nullable=False)


class User5(db.Model):
    __tablename__ = 'CartItems'
    CP_id = db.Column(db.String(100), primary_key=True)
    CP_desc = db.Column(db.Integer, nullable=False)
    CP_pirce = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.PD_id'),)




@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['emailOrPhone']
        password = request.form['password']
        
        user = User.query.filter_by(email_or_phone=username).first()
        if user and user.password == password:
            session['loggedin'] = True
            session['eml'] = user.email_or_phone
            session['id'] = user.user_id
            flash('Login successful!', 'success')
            return redirect(url_for('user'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')



#logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('eml', None)
    return redirect(url_for('home'))



#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['emailOrPhone']
        password = request.form['password']
        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        password = request.form.get('password')
        id = request.form.get('driversLicense')
        address = request.form.get('address')

        user = User(first_name=firstname, last_name=lastname, email_or_phone=username, password=password, drivers_license=id, address=address)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'loggedin' in session:
        return render_template('user.html', username=session['eml'], id=session['user_id'])
        ##return render_template('user.html', username=session['eml']) user this for actual user id in database
    else:
        return redirect(url_for('login'))

@app.route('/my_citations', methods=['GET', 'POST'])
def my_citations():
       
    if 'loggedin' in session:
        id = session['user_id']
        ##users_citations = User2.query.filter_by(user_id=id).all() #this would not show any data yet cause database keys are not linked yet

        #for checking if data is being pulled from database
        users_citations = User2.query.all()
        ##users_citations = User2.query.filter_by(M_id=id).all()
    
    return render_template('citations.html', title='My Citations', users_citations=users_citations)

@app.route('/my_notice', methods=['GET', 'POST'])
def my_notice():
       
    if 'loggedin' in session:
        ##this will pull specific user data from database
        ##id = session['user_id']
        ##users_notice = User3.query.filter_by(user_id=id).all()
    
        #for now this will pull all data from database
        users_notice = User3.query.all()

    return render_template('notice.html', title='My Notice', users_notice=users_notice)


#cart
@app.route('/my_cart', methods=['GET', 'POST'])
def my_cart():
    if 'loggedin' in session:
        return render_template('cart.html')
    
    return render_template('cart.html')



#shop
@app.route('/shop', methods=['GET', 'POST'])
def shop():
    if 'loggedin' in session:
        products = User4.query.all()
        return render_template('shop.html', products=products)



#add to cart
#add to cart
@app.route('/add_to_cart', methods=['GET','POST'])
def add_to_cart():
    if 'loggedin' in session and request.method == 'POST':
        pname = request.form.get('product_name')
        pprice = request.form.get('product_price')
        pitem = request.form.get('product_item')
    
        if pname and pprice and pitem:
            user = User5(item=pitem,price=pprice,Name=pname)
            db.session.add(user)
            db.session.commit()

        return redirect(url_for('shop'))
    return render_template('shop.html')


#remove cart
@app.route('/remove_cart', methods=['POST'])
def remove_cart():
    if 'loggedin' in session and request.method == 'POST':
        pname = request.form.get('productname')
        pprice = request.form.get('productprice')
        pitem = request.form.get('numberofitem')


        # Query the database to get the record
        product = User5.query.filter_by(item=pitem,Name=pname,price=pprice).first()

        # If the product exists, delete it from the database
        if product:
            db.session.delete(product)
            db.session.commit()

        return redirect(url_for('shop'))

    return render_template('cart.html')




#contact
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'loggedin' in session:
        return render_template('contact.html')
    
    return render_template('contact.html')


#google authentication
@app.route('/gmail', methods=['GET', 'POST'])
def gmail():
    request.method == 'POST'
    
    gauth.main()       
    
    return render_template('home.html')

    

#get bot response
@app.route("/chatbot")
def chatbot():    
    return render_template("chatbot.html")


@app.route("/api", methods=["POST"])
def api():
    # Get the message from the POST request
    message = request.json.get("message")
    # Send the message to OpenAI's API and receive the response
    
    
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": message}
    ]
    )
    if completion.choices[0].message!=None:
        return completion.choices[0].message

    else :
        return 'Failed to Generate response!'



if __name__ == '__main__':
    app.run(debug=True)