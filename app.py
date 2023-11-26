from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import pyodbc
from sqlalchemy import create_engine
from werkzeug.security import check_password_hash, generate_password_hash



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

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['emailOrPhone']
        password = request.form['password']
        
        query = "SELECT * FROM UserRegistrations WHERE email_or_phone=? AND password=?"

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
        email = request.form.get('emailOrPhone')
        password = request.form.get('password')
        id = request.form.get('driversLicense')
        address = request.form.get('address')

        query = "INSERT INTO UserRegistrations(first_name, last_name, email_or_phone, password, drivers_license, address) VALUES (?, ?, ?, ?, ?, ?)"
        user = User(first_name=firstname, last_name=lastname, email_or_phone=email, password=password, drivers_license=id, address=address)
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

if __name__ == '__main__':
    app.run(debug=True)
    
