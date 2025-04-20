from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
from datetime import timedelta
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'veryverysusthatyourareloolingformysecretkey'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mediconnect_db'
app.permanent_session_lifetime = timedelta(minutes=30)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)
mysql = MySQL(app)

def send_email(subject, recipient, body):
    msg = Message(subject, sender='your-email@gmail.com', recipients=[recipient])
    msg.body = body
    mail.send(msg)

# Registration Form
class RegistrationForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=50)])
    age = IntegerField("Age", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('doctor', 'Doctor'), ('patient', 'Patient')], validators=[DataRequired()])
    submit = SubmitField('Register')

# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Doctor Profile Form
class DoctorProfileForm(FlaskForm):
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    specialization = StringField('Specialization')
    experience_years = IntegerField('Years of Experience')
    qualifications = StringField('Qualifications')
    hospital_affiliation = StringField('Hospital Affiliation')
    bio = StringField('Short Bio')
    contact_number = StringField('Contact Number')
    available_timeslots = StringField('Available Timeslots (e.g. Mon-Fri 9AM-1PM)')
    submit = SubmitField('Save Profile')

# Patient Profile Form
class PatientProfileForm(FlaskForm):
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    blood_group = StringField('Blood Group')
    contact_number = StringField('Contact Number')
    address = StringField('Address')
    medical_history = StringField('Medical History')
    allergies = StringField('Allergies')
    current_medications = StringField('Current Medications')
    emergency_contact = StringField('Emergency Contact')
    submit = SubmitField('Save Profile')
#Appointment Form
class AppointmentForm(FlaskForm):
    doctor_id = SelectField('Select Doctor', coerce=int, validators=[DataRequired()])
    appointment_date = StringField('Appointment Date (YYYY-MM-DD)', validators=[DataRequired()])
    submit = SubmitField('Book Appointment')

# Home Route
@app.route('/')
@app.route('/home')
def home():
    print("Rendering home.html")
    return render_template('home.html')

# About Route
@app.route('/about')
def about():
    return render_template('about.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        age = form.age.data
        email = form.email.data
        password = form.password.data
        role = form.role.data

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            form.email.errors.append('Email already registered.')
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO user (name, age, email, password, role) VALUES (%s, %s, %s, %s, %s)',
                (name, age, email, hashed_password, role)
            )
            mysql.connection.commit()
            userid = cursor.lastrowid
            cursor.close()

            session['loggedin'] = True
            session['userid'] = userid
            session['email'] = email
            session['role'] = role
            session['name'] = name

            return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session.permanent = True
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('profile'))

        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)

# Profile Page
@app.route('/profile')
def profile():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    role = session['role']
    userid = session['userid']
    profile_data = None

    if role == 'doctor':
        cursor.execute('SELECT * FROM doctor_profile WHERE doctor_id = %s', (userid,))
        profile_data = cursor.fetchone()
    elif role == 'patient':
        cursor.execute('SELECT * FROM patient_profile WHERE patient_id = %s', (userid,))
        profile_data = cursor.fetchone()

    return render_template('profile.html', name=session['name'], email=session['email'],
                           role=role, profile=profile_data)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Doctor Appointments Route
@app.route('/doctor/appointments', methods=['GET', 'POST'])
def doctor_appointments():
    if 'loggedin' not in session or session['role'] != 'doctor':
        flash('You must be logged in as a doctor to access this page.', 'danger')
        return redirect(url_for('login'))

    doctor_id = session['userid']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch all appointments for the logged-in doctor
    cursor.execute('''
        SELECT a.appointment_id, a.appointment_date, a.status, u.name AS patient_name
        FROM appointments a
        JOIN user u ON a.patient_id = u.userid
        WHERE a.doctor_id = %s
        ORDER BY a.appointment_date
    ''', (doctor_id,))
    appointments = cursor.fetchall()

    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        action = request.form.get('action')

        if action == 'approve':
            status = 'Approved'
        elif action == 'decline':
            status = 'Declined'
        elif action == 'reschedule':
            status = 'Rescheduled'
        elif action == 'checked':
            status = 'Checked'

        # Update the appointment status
        cursor.execute('''
            UPDATE appointments
            SET status = %s
            WHERE appointment_id = %s
        ''', (status, appointment_id))
        mysql.connection.commit()

        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('doctor_appointments'))

    return render_template('doctor_appointments.html', appointments=appointments)

# Patient Appointments Route
@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if 'loggedin' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))

    form = AppointmentForm()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch available doctors
    cursor.execute("SELECT userid, name, email FROM user WHERE role = 'doctor'")
    doctors = cursor.fetchall()
    form.doctor_id.choices = [(doctor['userid'], doctor['name']) for doctor in doctors]

    if form.validate_on_submit():
        patient_id = session['userid']
        doctor_id = form.doctor_id.data
        appointment_date = form.appointment_date.data

        # Insert appointment into the database
        cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, appointment_date)
            VALUES (%s, %s, %s)
        ''', (patient_id, doctor_id, appointment_date))
        mysql.connection.commit()

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointments'))

    # Fetch patient's appointments
    cursor.execute('''
        SELECT a.*, u.name AS doctor_name 
        FROM appointments a 
        JOIN user u ON a.doctor_id = u.userid 
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date
    ''', (session['userid'],))
    appointments = cursor.fetchall()

    return render_template('appointments.html', form=form, appointments=appointments)


@app.route('/health_tips')
def health_tips():
    # Sample data for health tips and articles
    articles = [
        {"title": "10 Tips for a Healthy Lifestyle", "content": "Eat healthy, exercise regularly, and sleep well."},
        {"title": "The Importance of Hydration", "content": "Drinking enough water is essential for your body."},
        {"title": "Managing Stress Effectively", "content": "Practice mindfulness and relaxation techniques."}
    ]
    videos = [
        {"title": "Yoga for Beginners", "url": "https://www.youtube.com/embed/v7AYKMP6rOE"},
        {"title": "Healthy Eating Habits", "url": "https://www.youtube.com/embed/dBnniua6-oM"}
    ]
    return render_template('health_tips.html', articles=articles, videos=videos)
@app.route('/symptom_checker', methods=['GET', 'POST'])
def symptom_checker():
    suggestion = None
    if request.method == 'POST':
        symptoms = request.form.get('symptoms').lower()
        if "fever" in symptoms or "cough" in symptoms:
            suggestion = "You may have a viral infection. Please consult a doctor if symptoms persist."
        elif "chest pain" in symptoms or "shortness of breath" in symptoms:
            suggestion = "This could be a serious condition. Seek immediate medical attention."
        else:
            suggestion = "Your symptoms are not recognized. Please consult a doctor for a proper diagnosis."
    return render_template('symptom_checker.html', suggestion=suggestion)

@app.route('/emergency_contacts', methods=['GET', 'POST'])
def emergency_contacts():
    if request.method == 'POST':
        contact_name = request.form.get('contact_name')
        contact_number = request.form.get('contact_number')
        # Here you can save the contact to the database or session
        flash(f'Contact {contact_name} added successfully!', 'success')
    return render_template('emergency_contacts.html')

@app.route('/first_aid')
def first_aid():
    return render_template('first_aid.html')

@app.route('/forum', methods=['GET', 'POST'])
def forum():
    return render_template('forum.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)