from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import mysql.connector
from mysql.connector import Error
from werkzeug.utils import secure_filename

import time
import os


import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Configuration       
cloudinary.config( 
    cloud_name = "dud9elfag", 
    api_key = "566776174283142", 
    api_secret = "yc2tiq-RNmTW2ul0TiQLOlTbNHA", # Click 'View API Keys' above to copy your API secret
    secure=True
)

# Upload an image
upload_result = cloudinary.uploader.upload("https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
                                           public_id="shoes")
print(upload_result["secure_url"])

def upload_file(file):
    try:
        # first assign folder and resource-type based on filetype:
        result = cloudinary.uploader.upload(
            file,
            resource_type='image'
        )
        return {"success": True, "secure_url": result['secure_url'], "public_id": result['public_id']}
    except Exception as e:
        return {"success": False, "error": str(e)}


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your actual secret key
app.config['UPLOAD_FOLDER'] = '/static/uploads/profile_pictures'
print(app.config['UPLOAD_FOLDER'])

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
            'age': request.form.get('age'),  # Directly capture age from the form
            'religion': request.form.get('religion'),
            'gotra': request.form.get('gotra'),  # Capture gotra from the form
            'mother_tongue': request.form.get('mother_tongue'),  # Capture mother tongue from the form
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
@app.route('/profile3', methods=['GET', 'POST'])
def profile3():
    if request.method == 'POST':
        data = {
            'qualification': request.form.get('qualification'),
            'specialization': request.form.get('specialization'),
            'working_status': request.form.get('working_status'),
            'works_with': request.form.get('works_with'),
            'job_title': request.form.get('job_title'),
            'income': request.form.get('income'),
            'instagram': request.form.get('instagram'),  # Get Instagram profile link
            'facebook': request.form.get('facebook'),    # Get Facebook profile link
            'linkedin': request.form.get('linkedin')     # Get LinkedIn profile link
        }
        session['profile3'] = data  # Store in session
        insert_data('profile3', data)
        print("Data inserted successfully:", data)
        return redirect(url_for('profile4'))
    return render_template('profile3.html')


# app.config['UPLOAD_FOLDER'] = 'static/uploads/profile_pictures'

@app.route('/profile4', methods=['GET', 'POST'])
def profile4():
    if request.method == 'POST':
        # Retrieve form data
        data = {
            'identity_type': request.form.get('identity_type'),
            'identity_number': request.form.get('identity_number')
        }
        
        # Handle profile picture upload
        profile_picture = request.files.get('profile_picture')
        if profile_picture:
            # Secure the filename and save the file
            file_meta_data = upload_file(profile_picture)
            if file_meta_data['success'] == False:
                print('FUCK, error uploading file')            
            # Store the relative path in the data dictionary
            data['profile_picture'] = file_meta_data['secure_url']  # Store only the filename

        # Save data in session and database
        session['profile4'] = data  # Store in session
        try:
            # Adjust `insert_data` to handle profile_picture insertion correctly
            insert_data('profile4', data)  # This should save data, including profile_picture, to your database
            print("Data inserted successfully:", data)
            flash('Profile created successfully!', 'success')
            return redirect(url_for('success'))  # Redirect to success page
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('success'))
    return render_template('profile4.html')

@app.route('/success')
def success():
    # Collect data from session, including profile picture path
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

@app.route('/explore', methods=['GET'])
def explore():
    if 'user_id' not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login_register'))

    # Retrieve filter values from the request
    looking_for = request.args.get('looking_for')
    mother_tongue = request.args.get('mother_tongue')
    gotra_to_avoid = request.args.get('gotra')
    city = request.args.get('city')  # New filter for city

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Base query
        query = """
        SELECT p.id, p.name_first, p.name_last, p.gender, p.dob, p.religion, 
               pr.looking_for, pr.age_min, pr.age_max, pr.mother_tongue, pr.gotra,
               p2.temp_city, p2.perm_city, p3.qualification, p3.working_status, 
               p4.identity_type, p4.profile_picture
        FROM profile p
        LEFT JOIN profiles pr ON p.id = pr.id
        LEFT JOIN profile2 p2 ON p.id = p2.id
        LEFT JOIN profile3 p3 ON p.id = p3.id
        LEFT JOIN profile4 p4 ON p.id = p4.id
        WHERE 1=1
        """

        # Add filter conditions dynamically if provided
        if looking_for and looking_for.lower() != 'none':
            query += f" AND pr.looking_for = '{looking_for}'"
        if mother_tongue and mother_tongue.lower() != 'none':
            query += f" AND pr.mother_tongue = '{mother_tongue}'"
        if gotra_to_avoid and gotra_to_avoid.lower() != 'none':
            query += f" AND p.gotra != '{gotra_to_avoid}'"
        if city and city.lower() != 'none':
            query += f" AND (p2.temp_city = '{city}' OR p2.perm_city = '{city}')"

        cursor.execute(query)
        profiles = cursor.fetchall()

        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error fetching data: {e}")
        flash("Failed to load profiles.", "danger")
        return redirect(url_for('profile_success'))

    return render_template('explore.html', profiles=profiles)

@app.route('/profile/<int:profile_id>')
def profile_detail(profile_id):
    if 'user_id' not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('login_register'))

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Updated query with LEFT JOIN to include all details if available
        query = """
        SELECT p.name_first, p.name_last, p.gender, p.dob, p.religion, p.phone,
               pr.looking_for, pr.age_min, pr.age_max, pr.mother_tongue, pr.gotra,
               p2.temp_city, p2.temp_state, p2.temp_address, p2.perm_address,
               p2.lives_with_family, p2.marital_status, p2.diet,
               p3.qualification, p3.specialization, p3.working_status, p3.works_with,
               p3.job_title, p3.income, p3.instagram, p3.facebook, p3.linkedin, -- Include social media links
               p4.identity_type, p4.identity_number
        FROM profile p
        LEFT JOIN profiles pr ON p.id = pr.id
        LEFT JOIN profile2 p2 ON p.id = p2.id
        LEFT JOIN profile3 p3 ON p.id = p3.id
        LEFT JOIN profile4 p4 ON p.id = p4.id
        WHERE p.id = %s
        """
        cursor.execute(query, (profile_id,))
        profile = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not profile:
            flash("Profile not found.", "danger")
            return redirect(url_for('explore'))
    except Error as e:
        print(f"Error fetching data: {e}")
        flash("Failed to load profile details.", "danger")
        return redirect(url_for('explore'))
    
    return render_template('profile_detail.html', profile=profile)


@app.route('/myprofile')
def myprofile():
    if 'user_id' not in session:
        flash("Please log in to access your profile.", "warning")
        return redirect(url_for('login_register'))
    
    user_id = session['user_id']

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT 
            u.username, u.email AS user_email,
            p.name_first, p.name_middle, p.name_last, p.gender, p.dob, p.religion, p.email, p.phone,
            pr.looking_for, pr.age_min, pr.age_max, pr.mother_tongue, pr.gotra,
            p2.temp_address, p2.temp_city, p2.temp_district, p2.temp_state, p2.temp_pincode,
            p2.perm_address, p2.perm_city, p2.perm_district, p2.perm_state, p2.perm_pincode,
            p2.lives_with_family, p2.marital_status, p2.diet,
            p3.qualification, p3.specialization, p3.working_status, p3.works_with, p3.job_title, p3.income,
            p3.instagram, p3.facebook, p3.linkedin,
            p4.identity_type, p4.identity_number,
            p4.profile_picture -- Profile picture column from users table
        FROM users u
        LEFT JOIN profile p ON u.id = p.id
        LEFT JOIN profiles pr ON u.id = pr.id
        LEFT JOIN profile2 p2 ON u.id = p2.id
        LEFT JOIN profile3 p3 ON u.id = p3.id
        LEFT JOIN profile4 p4 ON u.id = p4.id
        WHERE u.id = %s
        """
        cursor.execute(query, (user_id,))
        profile = cursor.fetchone()
        cursor.close()
        connection.close()

        if not profile:
            flash("No profile found for your account.", "danger")
            return redirect(url_for('explore'))
    
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        flash("An error occurred while fetching your profile.", "danger")
        return redirect(url_for('explore'))
    
    print(profile)
    
    return render_template('myprofile.html', profile=profile)
@app.route('/contact')
def contact():
    return render_template('contactus.html')

@app.route('/logout')
def logout():
    session.clear()  # Clears the session
    flash("You have been logged out.", "info")
    return redirect(url_for('login_register'))
