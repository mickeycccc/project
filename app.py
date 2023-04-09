from flask import Flask, render_template, request, redirect, session
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db = pymysql.connect(
    host='localhost',
    user='mc',
    password='Mc27274581',
    database='job_recruitment'
)


# Connect to the database

# Home page
@app.route('/')
def index():
  return render_template('index.html')

# base page
@app.route('/QaA')
def QaA():
  return render_template('QaA.html')

# Registration function
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (email, password, user_type) VALUES (%s, %s, %s)', (email, password, user_type))
        db.commit()
        
        return redirect('/login')
    
    return render_template('register.html')

# Login function
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user[0]
            session['user_type'] = user[3]
            
            # get the referring user_id from the request arguments (if it exists)
            referring_user_id = request.args.get('ref_user_id')
            
            # redirect to home page with referring user_id as a parameter
            if referring_user_id:
                return redirect(f'/home?ref_user_id={referring_user_id}')
            else:
                return redirect('/home')
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')




@app.route('/home')
def home():
    # check if user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    if 'user_id' in session:
        user_id = session['user_id']
        # get user profile from database
        user_profile = get_user_profile_by_user_id(user_id)
        # render home template with user profile
        return render_template('home.html', user_profile=user_profile, user_id=user_id)
    else:
        # user is not logged in, redirect to login page
        return redirect('/login')







def get_user_profile_by_user_id(user_id):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = %s', (user_id,))
    user_profile = cursor.fetchone()
    return user_profile

# User Profile page
@app.route('/userprofile', methods=['GET', 'POST'])
def userprofile():
    # check if user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    
    # check if user is a job seeker
    if session['user_type'] != 'employee':
        return redirect('/home')
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        location = request.form['location']
        education = request.form['education']
        user_id = session['user_id']
        
        cursor = db.cursor()
        cursor.execute('INSERT INTO user_profiles (user_id,first_name, last_name, email, phone_number, location, education) values(%s, %s, %s, %s, %s, %s, %s)', (user_id,first_name, last_name, email, phone_number, location, education));        
        db.commit()
        
        return redirect('/userprofile')
    
    
    return render_template('userprofile.html')





# Job Postings page
@app.route('/job_postings', methods=['GET', 'POST'])
def job_postings():
    # check if user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    
    # check if user is an employer
    if session['user_type'] != 'employer':
        return redirect('/home')
    
    if request.method == 'POST':
        job_title = request.form['job_title']
        qualifications = request.form['qualifications']
        salary_range = request.form['salary_range']
        location = request.form['location']
        user_id = session['user_id']
        
        cursor = db.cursor()
        cursor.execute('INSERT INTO job_postings (user_id, job_title, qualifications, salary_range, location) VALUES (%s, %s, %s, %s, %s)', (user_id, job_title, qualifications, salary_range, location))
        db.commit()
        
        return redirect('/job_postings')
    
    return render_template('job_postings.html')

# Route to display all job listings
@app.route('/job_listing')
def job_listing():
    if 'user_id' not in session:
        return redirect('/login')
        # check if user is an employer
    if session['user_type'] != 'employer':
        return redirect('/home')
    cursor = db.cursor()
    # Execute the query to retrieve all job listings
    query = "SELECT * FROM job_postings"
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Close the cursor and database connection

    cursor.close()
    db.close()
    # Render the job listings template and pass the rows as context
    return render_template('job_listing.html', rows=rows)

@app.route('/listingprofile')
def listingprofile():
    if 'user_id' not in session:
        return redirect('/login')

        # check if user is an employer
    if session['user_type'] != 'employee':
        return redirect('/home')
    # redirect to login page

        cursor = db.cursor()
        rows = []

        query = "SELECT * FROM user_profiles"

        cursor.execute(query)       

        for row in cursor:
            rows.append(row)

        cursor.close()
        db.close()

    return render_template('listingprofile.html', rows=rows)


@app.route('/logout')
def logout():
    # remove user id from session
    session.pop('user_id', None)
    # redirect to login page
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
