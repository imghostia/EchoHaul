# app.py

from flask import Flask, request, render_template, jsonify, redirect, url_for
import pyodbc

app = Flask(__name__)

# Database Connection Configuration
db_connection_string = 'DRIVER={SQL Server};SERVER=LAPTOP-9VI64K50\SQLEXPRESS;DATABASE=ecohaul;Trusted_Connection=yes;'
conn = pyodbc.connect(db_connection_string)
cursor = conn.cursor()


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Check if the username and password match in the database
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            return jsonify({"success": True, "message": "Login successful!"})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        cursor.close()



@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')



# Add a route to render the add_records page
@app.route('/add_records', methods=['GET'])
def add_records():
    return render_template('add_records.html')

# Add a route to handle form submission
@app.route('/submit_records', methods=['POST'])
def submit_records():
    try:

        with conn.cursor() as cursor:
            record_text = request.form.get('record_text')
            insert_query = "INSERT INTO records (record_text) VALUES (?)"
            cursor.execute(insert_query, (record_text))
            conn.commit()
        # Here you can insert the record_text into the database

        # For now, let's just print it
        print(f"Record Text: {record_text}")

        return redirect(url_for('add_records'))
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})



@app.route('/view_complaints', methods=['GET'])
def view_complaints():
    with conn.cursor() as cursor:
        select_query = "SELECT c_desc FROM complaints"
        cursor.execute(select_query)
        complaints = cursor.fetchall()

    return render_template('view_complaints.html', complaints=complaints)

@app.route('/manage_employees')
def manage_employees():
    # Fetch the list of employees from the database
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()

    return render_template('manage_employees.html', employees=employees)


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            position = request.form.get('position')
            salary = request.form.get('salary')

            # Insert the new employee into the database
            with conn.cursor() as cursor:
                insert_query = "INSERT INTO employees (name, position, salary) VALUES (?, ?, ?)"
                cursor.execute(insert_query, (name, position, salary))
                conn.commit()

            return redirect(url_for('admin_dashboard'))

        except Exception as e:
            return jsonify({"success": False, "message": str(e)})

    else:
        return render_template('add_employee.html')


@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    # Fetch the employee data from the database
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM employees WHERE id=?", (employee_id,))
        employee = cursor.fetchone()

    if request.method == 'POST':
        # Update the employee in the database
        name = request.form.get('name')
        position = request.form.get('position')
        salary = request.form.get('salary')

        with conn.cursor() as cursor:
            update_query = "UPDATE employees SET name=?, position=?, salary=? WHERE id=?"
            cursor.execute(update_query, (name, position, salary, employee_id))
            conn.commit()

        return redirect(url_for('manage_employees'))

    return render_template('edit_employee.html', employee=employee)

@app.route('/delete_employee/<int:employee_id>')
def delete_employee(employee_id):
    # Delete the employee from the database
    with conn.cursor() as cursor:
        delete_query = "DELETE FROM employees WHERE id=?"
        cursor.execute(delete_query, (employee_id,))
        conn.commit()

    return redirect(url_for('manage_employees'))

if __name__ == '__main__':
    app.run(debug=True)
