from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import pyodbc
from sqlalchemy import create_engine


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ecohaul'
app.app_context()

engine = create_engine("mssql+pyodbc://Hiren/ecohaul?driver=SQL+Server", echo=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://Hiren/ecohaul?driver=SQL+Server'

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
            flash('Login successful!', 'success')
            return redirect(url_for('user'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

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
        return render_template('user.html', username=session['eml'])
    else:
        return redirect(url_for('login'))

@app.route('/my_citations', methods=['GET', 'POST'])
def my_citations():
       
    if 'loggedin' in session:
        users = User2.query
    
    return render_template('my_citations.html', title='Citations', users=users)


if __name__ == '__main__':
    app.run(debug=True)

    


    
