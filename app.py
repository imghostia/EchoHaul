import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash



app = Flask(__name__)
app.secret_key = 'ecohaul'


def db_connection():
    conn = pyodbc.connect("Driver={SQL Server};"
                         "SERVER=Hiren;"
                         "DATABASE=ecohaul;"
                         "Trusted_Connection=yes;")
    cursor = conn.cursor()
    return conn, cursor

db = db_connection()

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn, cursor = db_connection()
        
        fn = request.form.get('firstName')
        ln = request.form.get('lastName')
        eml = request.form.get('emailOrPhone')
        psw = request.form.get('password')
        id = request.form.get('driversLicense')
        add = request.form.get('address')
                  
        query = "INSERT INTO UserRegistrations(first_name, last_name, email_or_phone, password, drivers_license, address) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (fn, ln, eml, psw, id, add))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn, cursor = db_connection()

        eml = request.form.get('emailOrPhone')
        psw = request.form.get('password')

        # Query the database for the user
        cursor.execute("SELECT * FROM UserRegistrations WHERE email_or_phone=? AND password=?", (eml, psw))
        user = cursor.fetchone()
        # If no user is found, return an error message
        if check_password_hash(user[4], psw):
            session['loggedin'] = True
            session['eml'] = user[3]
            session['psw'] = user[4]

            return redirect(url_for('user'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')


@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'loggedin' in session:
        return render_template('user.html', username=session['eml'])
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    print("Logout function called")  # Debug print
    session.pop('user_id', None)
    
    return redirect(url_for('login'))


@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.cache_control.proxy_revalidate = True
    response.expires = 0
    return response

if __name__ == '__main__':
    app.run(debug=True)
