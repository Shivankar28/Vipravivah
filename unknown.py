from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import mysql.connector
from mysql.connector import Error
import pdfkit
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your actual secret key
app.config['UPLOAD_FOLDER'] = 'uploads/profile_pictures'

db_config = {
    'host': 'mysql-385e1d9b-shivankar-b189.b.aivencloud.com',
    'user': 'avnadmin',
    'password': 'AVNS_IWNnIqNtr9DjL3mVLgW',
    'database': 'shivankar',
    'port': '19861'
}

def insert_data(table, data):
    retries = 3
    for attempt in range(retries):
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            placeholders = ', '.join(['%s'] * len(data))
            columns = ', '.join(data.keys())
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, list(data.values()))
            connection.commit()
            cursor.close()
            connection.close()
            break  # Exit retry loop if operation is successful
        except Error as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                time.sleep(5)  # Wait before retrying
            else:
                flash("Failed to insert data after multiple attempts.", "danger")
                print(f"Final attempt failed with error: {e}")
                raise  # Raise exception after final attempt

def query_data(sql, params=None):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Error as e:
        print(f"Error querying data: {e}")
        return None

def get_user_by_username(username):
    sql = "SELECT * FROM users WHERE username = %s"
    result = query_data(sql, (username,))
    return result[0] if result else None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login_register')
def login_register():
    return render_template('login_register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    existing_user = get_user_by_username(username)
    if existing_user:
        flash("Username already taken. Please choose another one.", "danger")
        return redirect(url_for('login_register'))

    data = {
        'username': username,
        'password': password,  # In a real-world application, never store passwords as plain text
        'email': email
    }
    try:
        insert_data('users', data)
        flash("Registration successful. You can now log in.", "success")
    except Exception as e:
        flash("Registration failed. Please try again.", "danger")

    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = get_user_by_username(username)
    if user and user['password'] == password:
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash("Login successful.", "success")
        return redirect(url_for('explore'))
    else:
        flash("Login failed. Please check your credentials and try again.", "danger")
        return redirect(url_for('login_register'))

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/index_submit', methods=['POST'])
def index_submit():
    data = {
        'looking_for': request.form.get('looking_for'),
        'age_min': request.form.get('age_min'),
        'age_max': request.form.get('age_max'),
        'mother_tongue': request.form.get('mother_tongue'),
        'gotra': request.form.get('gotra')
    }
    session['profile_data'] = data
    try:
        insert_data('profiles', data)
        print("Data inserted successfully:", data)
    except Exception as e:
        print("Data insertion failed:", str(e))
        flash("Failed to insert data.", "danger")
        return redirect(url_for('index'))  # Redirect back to index if insertion fails
    
    return redirect(url_for('profile'))  # Redirect to the profile page after succes

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        data = {
            'looking_for': session['profile_data'].get('looking_for'),
            'gender': request.form.get('gender'),
            'name_first': request.form.get('first_name'),
            'name_middle': request.form.get('middle_name'),
            'name_last': request.form.get('last_name'),
            'dob': request.form.get('dob'),
            'religion': request.form.get('religion'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone')
        }
        session['profile'] = data  # Store in session
        insert_data('profile', data)
        print("Data inserted successfully:", data)
        return redirect(url_for('profile2'))
    return render_template('profile.html')

@app.route('/profile2', methods=['GET', 'POST'])
def profile2():
    if request.method == 'POST':
        data = {
            'temp_address': request.form.get('temp_address'),
            'temp_city': request.form.get('temp_city'),
            'temp_district': request.form.get('temp_district'),
            'temp_state': request.form.get('temp_state'),
            'temp_pincode': request.form.get('temp_pincode'),
            'perm_address': request.form.get('perm_address'),
            'perm_city': request.form.get('perm_city'),
            'perm_district': request.form.get('perm_district'),
            'perm_state': request.form.get('perm_state'),
            'perm_pincode': request.form.get('perm_pincode'),
            'lives_with_family': request.form.get('lives_with_family'),
            'marital_status': request.form.get('marital_status'),
            'diet': ','.join(request.form.getlist('diet'))  # Convert list to comma-separated string
        }
        session['profile2'] = data  # Store in session
        insert_data('profile2', data)
        print("Data inserted successfully:", data)
        return redirect(url_for('profile3'))
    return render_template('profile2.html')

@app.route('/profile3', methods=['GET', 'POST'])
def profile3():
    if request.method == 'POST':
        data = {
            'qualification': request.form.get('qualification'),
            'specialization': request.form.get('specialization'),
            'working_status': request.form.get('working_status'),
            'works_with': request.form.get('works_with'),
            'job_title': request.form.get('job_title'),
            'income': request.form.get('income')
        }
        session['profile3'] = data  # Store in session
        insert_data('profile3', data)
        print("Data inserted successfully:", data)
        return redirect(url_for('profile4'))
    return render_template('profile3.html')

@app.route('/profile4', methods=['GET', 'POST'])
def profile4():
    if request.method == 'POST':
        data = {
            'identity_type': request.form.get('identity_type'),
            'identity_number': request.form.get('identity_number')
        }
        session['profile4'] = data  # Store in session
        try:
            insert_data('profile4', data)
            print("Data inserted successfully:", data)
            flash('Profile created successfully!', 'success')
            return redirect(url_for('success'))  # Redirect to success page
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('profile4'))
    return render_template('profile4.html')

@app.route('/success')
def success():
    # Collect data from session
    profile_data = {
        'profiles': session.get('profile_data', {}),
        'profile': session.get('profile', {}),
        'profile2': session.get('profile2', {}),
        'profile3': session.get('profile3', {}),
        'profile4': session.get('profile4', {})
    }
    return render_template('success.html', profile_data=profile_data)

@app.route('/profile_success')
def profile_success():
    return render_template('profile_success.html')

@app.route('/explore')
def explore():
    if 'user_id' not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login_register'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT p.name_first, p.name_last, p.gender, p.dob, p.religion,
               pr.looking_for, pr.age_min, pr.age_max, pr.mother_tongue, pr.gotra,
               p2.temp_city, p2.temp_state, p3.qualification, p3.working_status, p4.identity_type
        FROM profile p
        JOIN profiles pr ON p.id = pr.id
        JOIN profile2 p2 ON p.id = p2.id
        JOIN profile3 p3 ON p.id = p3.id
        JOIN profile4 p4 ON p.id = p4.id
        """
        cursor.execute(query)
        profiles = cursor.fetchall()
        
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error fetching data: {e}")
        flash("Failed to load profiles.", "danger")
        return redirect(url_for('profile_success'))
    
    return render_template('explore.html', profiles=profiles)

if __name__ == '__main__':
    app.run(debug=True)