import os
from datetime import datetime
import pyodbc
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Database Connection Configuration
connection_string = 'DRIVER={SQL Server};SERVER=LAPTOP-9VI64K50\SQLEXPRESS;DATABASE=ecohaul;Trusted_Connection=yes;'
# conn = pyodbc.connect(connection_string)
# cursor = conn.cursor()

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16 MB



def create_connection():
    return pyodbc.connect(connection_string)

conn = create_connection()
cursor = conn.cursor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def index():
    return render_template('login.html')


@app.route('/api/login', methods=['POST'])
def login():
    conn = create_connection()
    cursor = conn.cursor()
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



@app.route("/admin_supervisor_reg", methods=['GET', 'POST'])
def admin_supervisor_reg():
    conn = create_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        # Extract form data
        first_name = request.form['s_first_name']
        last_name = request.form['s_last_name']
        gender = request.form['s_gender']
        date_of_birth = request.form['s_date_of_birth']
        assign_to = request.form['s_assign_to']
        address1 = request.form['s_address1']
        state = request.form['s_state']
        address2 = request.form['s_address2']
        postcode = request.form['s_postcode']
        city = request.form['s_city']
        driver_license = request.form['s_driver_license']

        # Insert data into the supervisors table
        query = """
            INSERT INTO supervisors (
                s_first_name, s_last_name, s_gender, s_date_of_birth,
                s_assign_to, s_address1, s_state, s_address2, s_postcode, s_city, s_driver_license
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            first_name, last_name, gender, date_of_birth, assign_to, address1, state, address2, postcode, city,
            driver_license
        ))
        conn.commit()

        return redirect(url_for('admin_supervisor_reg'))

    # If it's a GET request, render the form
    return render_template('admin_supervisor_reg.html')

@app.route("/display_supervisors")
def display_supervisors():
    # Execute the SQL query to fetch all supervisor details
    cursor.execute("""
        SELECT * FROM supervisors;
    """)

    # Fetch all the supervisor details
    supervisors_data = cursor.fetchall()

    return render_template('display_supervisors.html', supervisors_data=supervisors_data)


@app.route("/display_supervisors/delete_supervisor/<int:id>", methods=['GET', 'POST'])
def delete_supervisor(id):
    if request.method == 'POST':
        # Assuming you have a supervisors table in your database
        cursor.execute("DELETE FROM supervisors WHERE supervisor_id = ?", (id,))
        conn.commit()

        return redirect(url_for('display_supervisors'))
    else:
        # Fetch supervisor details for confirmation message
        cursor.execute("SELECT * FROM supervisors WHERE supervisor_id = ?", (id,))
        supervisor = cursor.fetchone()

        return render_template('delete_supervisor.html', supervisor_id=id, supervisor=supervisor)


@app.route("/display_supervisors/edit_supervisor/<int:id>", methods=['GET', 'POST'])
def edit_supervisor(id):
    if request.method == 'POST':
        # Assuming you have a supervisors table in your database
        new_first_name = request.form.get('s_first_name')
        new_last_name = request.form.get('s_last_name')
        new_gender = request.form.get('s_gender')
        new_date_of_birth = request.form.get('s_date_of_birth')
        new_assign_to = request.form.get('s_assign_to')
        new_address1 = request.form.get('s_address1')
        new_state = request.form.get('s_state')
        new_address2 = request.form.get('s_address2')
        new_postcode = request.form.get('s_postcode')
        new_city = request.form.get('s_city')
        new_driver_license = request.form.get('s_driver_license')
        # Add other form fields for editing

        cursor.execute("""
            UPDATE supervisors 
            SET s_first_name=?, s_last_name=?, s_gender=?, s_date_of_birth=?, 
                s_assign_to=?, s_address1=?, s_state=?, s_address2=?, 
                s_postcode=?, s_city=?, s_driver_license=?
            WHERE supervisor_id=?
        """, (new_first_name, new_last_name, new_gender, new_date_of_birth,
              new_assign_to, new_address1, new_state, new_address2,
              new_postcode, new_city, new_driver_license, id))
        conn.commit()

        return redirect(url_for('display_supervisors'))
    else:
        # Fetch supervisor details for pre-populating the form
        cursor.execute("SELECT supervisor_id, s_first_name, s_last_name, s_state, s_assign_to FROM supervisors")


        supervisor = cursor.fetchone()

        return render_template('edit_supervisor.html', supervisor_id=id, supervisor=supervisor)

@app.route("/admin_loader_reg", methods=['GET', 'POST'])
def admin_loader_reg():
    if request.method == 'POST':
        # Extract form data
        first_name = request.form['l_first_name']
        last_name = request.form['l_last_name']
        email = request.form['l_email']
        gender = request.form['l_gender']
        date_of_birth = request.form['l_date_of_birth']
        address = request.form['l_address']
        state = request.form['l_state']
        postcode = request.form['l_postcode']
        city = request.form['l_city']

        # Insert data into the loaders table
        query = """
            INSERT INTO Loader (
                l_first_name, l_last_name, l_email, l_gender, l_date_of_birth,
                l_address, l_state, l_postcode, l_city
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            first_name, last_name, email, gender, date_of_birth, address, state, postcode, city
        ))
        conn.commit()

        return redirect(url_for('admin_dashboard'))

    # If it's a GET request, render the form
    return render_template('admin_loader_reg.html')


@app.route("/display_loader")
def display_loader():
    # Execute the SQL query to fetch all supervisor details
    cursor.execute("""
        SELECT * FROM Loader;
    """)

    # Fetch all the supervisor details
    loaders_data = cursor.fetchall()

    return render_template('display_loader.html', loaders_data=loaders_data)


@app.route("/display_loader/delete_loader/<int:id>", methods=['GET', 'POST'])
def delete_loader(id):
    if request.method == 'POST':
        # Assuming you have a loaders table in your database
        cursor.execute("DELETE FROM Loader WHERE loader_id = ?", (id,))
        conn.commit()

        return redirect(url_for('display_loader'))
    else:
        # Fetch loader details for confirmation message
        cursor.execute("SELECT * FROM Loader WHERE loader_id = ?", (id,))
        loader = cursor.fetchone()

        return render_template('delete_loader.html', loader_id=id, loader=loader)


@app.route("/display_loader/edit_loader/<int:id>", methods=['GET', 'POST'])
def edit_loader(id):
    if request.method == 'POST':
        # Assuming you have a loaders table in your database
        new_first_name = request.form.get('l_first_name')
        new_last_name = request.form.get('l_last_name')
        new_email = request.form.get('l_email')
        new_gender = request.form.get('l_gender')
        new_date_of_birth = request.form.get('l_date_of_birth')
        new_address = request.form.get('l_address')
        new_state = request.form.get('l_state')
        new_postcode = request.form.get('l_postcode')
        new_city = request.form.get('l_city')
        # Add other form fields for editing

        cursor.execute("""
            UPDATE Loader 
            SET l_first_name=?, l_last_name=?, l_email=?, l_gender=?, l_date_of_birth=?, 
                l_address=?, l_state=?, l_postcode=?, l_city=?
            WHERE loader_id=?
        """, (new_first_name, new_last_name, new_email, new_gender, new_date_of_birth,
              new_address, new_state, new_postcode, new_city, id))
        conn.commit()

        return redirect(url_for('display_loader'))
    else:
        # Fetch loader details for pre-populating the form
        cursor.execute("SELECT loader_id, l_first_name, l_last_name, l_state, l_email, l_address FROM Loader")

        loader = cursor.fetchone()

        return render_template('edit_loader.html', loader_id=id, loader=loader)


@app.route("/admin_driver_reg", methods=['GET', 'POST'])
def admin_driver_reg():
    if request.method == 'POST':
        first_name = request.form['d_first_name']
        last_name = request.form['d_last_name']
        gender = request.form['d_gender']
        date_of_birth = request.form['d_date_of_birth']
        assign_to = request.form['d_assign_to']
        address1 = request.form['d_address1']
        state = request.form['d_state']
        address2 = request.form['d_address2']
        postcode = request.form['d_postcode']
        city = request.form['d_city']
        driver_license = request.form['d_driver_license']

        # Insert data into the Driver table
        query = f"INSERT INTO driver (d_first_name, d_last_name, d_gender, d_date_of_birth, d_assign_to, d_address1, d_state, d_address2, d_postcode, d_city, d_driver_license) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (
            first_name, last_name, gender, date_of_birth, assign_to, address1, state, address2, postcode, city,
            driver_license))
        conn.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('admin_driver_reg.html')


@app.route("/display_driver")
def display_driver():
    cursor.execute("SELECT driver_id, d_first_name, d_last_name, d_state, d_assign_to, d_driver_license FROM driver");

    # Fetch all the driver details
    drivers_data = cursor.fetchall()
    print(drivers_data)
    return render_template('display_driver.html', drivers_data=drivers_data)


@app.route("/display_driver/delete_driver/<int:id>", methods=['GET', 'POST'])
def delete_driver(id):
    if request.method == 'POST':
        # Assuming you have a driver table in your database
        cursor.execute("DELETE FROM driver WHERE driver_id = ?", (id,))
        conn.commit()

        return redirect(url_for('display_driver'))
    else:
        # Fetch driver details for confirmation message
        cursor.execute("SELECT * FROM driver WHERE driver_id = ?", (id,))
        driver = cursor.fetchone()

        return render_template('delete_driver.html', driver_id=id, driver=driver)


@app.route("/display_driver/edit_driver/<int:id>", methods=['GET', 'POST'])
def edit_driver(id):
    if request.method == 'POST':
        # Assuming you have a driver table in your database
        new_first_name = request.form.get('d_first_name')
        new_last_name = request.form.get('d_last_name')
        new_gender = request.form.get('d_gender')
        new_date_of_birth = request.form.get('d_date_of_birth')
        new_assign_to = request.form.get('d_assign_to')
        new_address1 = request.form.get('d_address1')
        new_state = request.form.get('d_state')
        new_address2 = request.form.get('d_address2')
        new_postcode = request.form.get('d_postcode')
        new_city = request.form.get('d_city')
        new_driver_license = request.form.get('d_driver_license')
        # Add other form fields for editing

        cursor.execute("""
            UPDATE driver 
            SET d_first_name=?, d_last_name=?, d_gender=?, d_date_of_birth=?, 
                d_assign_to=?, d_address1=?, d_state=?, d_address2=?, 
                d_postcode=?, d_city=?, d_driver_license=?
            WHERE driver_id=?
        """, (new_first_name, new_last_name, new_gender, new_date_of_birth,
              new_assign_to, new_address1, new_state, new_address2,
              new_postcode, new_city, new_driver_license, id))
        conn.commit()

        return redirect(url_for('display_driver'))
    else:
        # Fetch driver details for pre-populating the form
        cursor.execute("SELECT * FROM driver WHERE driver_id = ?", (id,))
        driver = cursor.fetchone()

        return render_template('edit_driver.html', driver_id=id, driver=driver)


@app.route("/add_products", methods=['GET', 'POST'])
def add_products():
    if request.method == 'POST':
        # Extract form data
        p_name = request.form['p_name']
        p_type = request.form['p_type']
        p_price = request.form['p_price']
        p_size_liters = request.form['p_size_liters']

        # Handle file upload
        if 'p_image' in request.files:
            file = request.files['p_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                p_image = filename
            else:
                p_image = None
        else:
            p_image = None

        # Insert data into the products table
        query = """
            INSERT INTO products_table (p_name, p_type, p_image, p_price, p_size_liters) VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (p_name, p_type, p_image, p_price, p_size_liters))
        conn.commit()

        return redirect(url_for('display_products'))

    # If it's a GET request, render the form
    return render_template('add_products.html')


@app.route("/display_products")
def display_products():
    # Assuming you have a 'products' table with appropriate columns
    query = "SELECT * FROM products_table"
    cursor.execute(query)
    products_data = cursor.fetchall()
    return render_template('display_products.html', products_data=products_data)


@app.route("/delete_product/<int:id>", methods=['GET'])
def delete_product(id):
    # Assuming you have a 'products_table' table with an 'id' column
    query = "DELETE FROM products_table WHERE p_id = ?"
    cursor.execute(query, (id,))
    conn.commit()
    return redirect(url_for('display_products'))


@app.route('/admin_map_reg', methods=['GET', 'POST'])
def admin_map_reg():
    if request.method == 'POST':
        # Get form data
        map_zone = request.form.get('map_zone')

        # Handle file upload
        map_picture = request.files['map_picture']
        if map_picture and allowed_file(map_picture.filename):
            # Save the file to a folder
            map_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(map_picture.filename))
            map_picture.save(map_picture_path)

            # Insert data into the MS SQL Server database
            try:
                with create_connection().cursor() as cursor:
                    cursor.execute("INSERT INTO Map (map_zone, map_picture) VALUES (?, ?)", map_zone, map_picture_path)
                    create_connection().commit()
            except Exception as e:
                # Handle the exception (log, display error message, etc.)
                print(f"Error inserting data into the database: {e}")

            # Redirect to the admin index or wherever appropriate
            return redirect(url_for('admin_dashboard'))

    # Render the form template
    return render_template('admin_map_reg.html')


@app.route("/admin_add_products")
def admin_add_products():
    return render_template('admin_add_products.html')


@app.route("/driver_index")
def driver_index():
    return render_template('driver_index.html')


@app.route("/driver_message", methods=['POST', 'GET'])
def driver_message():
    if request.method == 'POST':
        gm_message = request.form['gm_message']
        gm_date = datetime.now().strftime("%Y-%m-%d")

        query = "INSERT INTO globalmessage (gm_message, gm_date) VALUES (?, ?)"
        cursor.execute(query, (gm_message, gm_date))
        conn.commit()

        return redirect(url_for('driver_index'))

    return render_template('driver_message.html')


@app.route("/request_help", methods=['POST', 'GET'])
def request_help():
    if request.method == 'POST':
        h_message = request.form['h_message']
        h_date = request.form['h_date']

        query = "INSERT INTO helprequest (h_message, h_date) VALUES (?, ?)"
        cursor.execute(query, (h_message, datetime.strptime(h_date, "%Y-%m-%d")))
        conn.commit()

        return redirect(url_for('driver_index'))

    return render_template('request_help.html')


@app.route('/report_customer', methods=['POST', 'GET'])
def report_customer():
    if request.method == 'POST':
        house_no = request.form.get('co_house_no')
        street = request.form.get('co_street')
        city = request.form.get('co_city')
        action = request.form.get('co_action')
        date = request.form.get('co_date')
        desc = request.form.get('co_desc')

        try:
            with create_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO CivilianComplaintReports (co_house_no, co_street, co_city, co_action, co_date, co_desc) VALUES (?, ?, ?, ?, ?, ?)",
                    (house_no, street, city, action, date, desc))

                conn.commit()

                # Handle file upload
                if 'img' in request.files:
                    file = request.files['img']
                    if file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        # If you want to store the file path in the database, you can do it here

        except pyodbc.Error as e:
            print(f"Database error: {e}")
            return render_template('error.html', message='An error occurred while processing your request.')

        return redirect(url_for('driver_index'))

    return render_template('report_customer.html')


def get_driver_id(driver_name):
    sql_query = "SELECT driver_id FROM driver WHERE d_first_name = ? AND d_last_name = ?"
    try:
        with create_connection().cursor() as local_cursor:
            local_cursor.execute(sql_query, driver_name.split())
            result = local_cursor.fetchone()
            if result:
                return result[0]
    except Exception as e:
        print(f"Error fetching driver ID from the database: {e}")


def get_loader_id(loader_name):
    sql_query = "SELECT loader_id FROM Loader WHERE l_first_name = ? AND l_last_name = ?"
    try:
        with create_connection().cursor() as local_cursor:
            local_cursor.execute(sql_query, loader_name.split())
            result = local_cursor.fetchone()
            if result:
                return result[0]
    except Exception as e:
        print(f"Error fetching loader ID from the database: {e}")


def get_map_id(map_zone):
    sql_query = "SELECT map_id FROM Map WHERE map_zone = ?"
    with create_connection().cursor() as local_cursor:
        local_cursor.execute(sql_query, (map_zone,))
        result = local_cursor.fetchone()
        if result:
            return result[0]
        else:
            print("No result found for map_zone:", map_zone)


# Assuming you have a function to fetch maps from the database
def fetch_maps_from_database():
    try:
        with create_connection().cursor() as local_cursor:
            local_cursor.execute("SELECT map_id, map_zone FROM Map")
            maps = local_cursor.fetchall()
        return maps
    except Exception as e:
        print(f"Error fetching maps from the database: {e}")
        return []


@app.route('/supervisor_assign_map', methods=['POST', 'GET'])
def supervisor_assign_map():
    if request.method == 'POST':
        map_zone = request.form.get('map_id')
        driver_name = request.form.get('d_assign_to_driver')
        loader_name = request.form.get('d_assign_to_loader')
        assign_map_note = request.form.get('assign_map_note')

        # Fetch the IDs for the driver, loader, and map
        driver_id = get_driver_id(driver_name)
        loader_id = get_loader_id(loader_name)
        map_id = get_map_id(map_zone)

        # Insert data into the Assignment table
        try:
            with create_connection().cursor() as local_cursor:
                local_cursor.execute(
                    "INSERT INTO Assignment (map_id, driver_id, loader_id, assign_map_note) VALUES (?, ?, ?, ?)",
                    (map_id, driver_id, loader_id, assign_map_note))
            conn.commit()
        except Exception as e:
            # Handle the exception (log, display error message, etc.)
            print(f"Error inserting data into the database: {e}")

        # Redirect to the admin index or wherever appropriate
        return redirect(url_for('admin_dashboard'))

    # For GET requests, render the template for the supervisor_assign_map page
    maps = fetch_maps_from_database()
    return render_template('supervisor_assign_map.html', maps=maps)


@app.route("/sample_drop")
def display_maps():
    # Assuming you have a 'products' table with appropriate columns
    query = "SELECT * FROM Map"
    cursor.execute(query)
    maps = cursor.fetchall()
    return render_template('sample_drop.html', maps=maps)

@app.route('/view_complaints', methods=['GET'])
def view_complaints():
    with conn.cursor() as cursor:
        select_query = "SELECT c_desc FROM complaints"
        cursor.execute(select_query)
        complaints = cursor.fetchall()

    return render_template('view_complaints.html', complaints=complaints)

if __name__ == '__main__':
    app.run(debug=True)