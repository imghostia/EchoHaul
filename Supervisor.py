from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
import pyodbc

app = Flask(__name__)
app.secret_key = 'ecohaul'

def db_connection():
    conn = pyodbc.connect("Driver={SQL Server};"
                         "SERVER=pree;"
                         "DATABASE=ecohaul;"
                         "Trusted_Connection=yes;")
    cursor = conn.cursor()
    return conn, cursor

@app.route('/')
def index():
    return render_template('Supervisor_index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn, cursor = db_connection()
        email = request.form.get('email')
        password = request.form.get('password')
        cursor.execute('SELECT * FROM Supervisor_Logon WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        if user:
            return f'Login successful! Welcome, {user.username}.'
        else:
            return 'Invalid email or password. Please try again.'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn, cursor = db_connection()
        userid = request.form.get('userid')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        address = request.form.get('address')
        phone = request.form.get('phone')
        cursor.execute('INSERT INTO Supervisor_detail_registration (sid, s_f_name, s_l_name, s_email, s_address, s_phone) VALUES (?, ?, ?, ?, ?, ?)',
                   (userid,firstname,lastname, email, address, phone))
        conn.commit()
        cursor.close()
        conn.close()
    return render_template('Supervisor_register.html')

@app.route('/timecard', methods=['GET', 'POST'])
def timecard():
    if request.method == 'POST':
        conn, cursor = db_connection()

        userid = request.form.get('userid_timecard')
        starttime = request.form.get('starttime')
        endtime = request.form.get('endtime')

        # Update the user's timecard in the Users table
        cursor.execute('UPDATE Supervisor_punch_in_timecard SET starttime = ?, endtime = ? WHERE userid = ?', (starttime, endtime, userid))
        conn.commit()

    return render_template('Supervisor_timecard.html')
