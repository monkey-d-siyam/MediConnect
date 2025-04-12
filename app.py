from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
from datetime import timedelta
from flask_mail import Mail, Message

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'veryverysusthatyourareloolingformysecretkey'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mediConnect_db'
app.permanent_session_lifetime = timedelta(minutes=30)

#Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'

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



# Home Route
@app.route('/')
@app.route('/home')
def home():
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
            session['role'] = user['role']  # <-- Add this line
            flash('Logged in successfully!', 'success')
            return redirect(url_for('profile'))

        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)

# Profile Page (Simple)
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


@app.route('/setup_profile', methods=['GET', 'POST'])
def setup_profile():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    if not role:
        return redirect(url_for('login'))

    userid = session.get('userid')

    if role == 'doctor':
        form = DoctorProfileForm()
        if form.validate_on_submit():
            cursor = mysql.connection.cursor()
            # Check if a profile already exists
            cursor.execute('SELECT * FROM doctor_profile WHERE doctor_id = %s', (userid,))
            existing_profile = cursor.fetchone()
            if existing_profile:
                flash('Doctor profile already exists. Please edit your profile.', 'warning')
                return redirect(url_for('profile'))

            # Insert new profile
            cursor.execute('''INSERT INTO doctor_profile (doctor_id, gender, specialization, experience_years, qualifications, 
                            hospital_affiliation, bio, contact_number, available_timeslots) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                           (userid, form.gender.data, form.specialization.data, form.experience_years.data,
                            form.qualifications.data, form.hospital_affiliation.data, form.bio.data,
                            form.contact_number.data, form.available_timeslots.data))
            mysql.connection.commit()
            flash('Doctor profile created successfully!', 'success')
            return redirect(url_for('profile'))
        return render_template('setup_doctor_profile.html', form=form)

    elif role == 'patient':
        form = PatientProfileForm()
        if form.validate_on_submit():
            cursor = mysql.connection.cursor()
            # Check if a profile already exists
            cursor.execute('SELECT * FROM patient_profile WHERE patient_id = %s', (userid,))
            existing_profile = cursor.fetchone()
            if existing_profile:
                flash('Patient profile already exists. Please edit your profile.', 'warning')
                return redirect(url_for('profile'))

            # Insert new profile
            cursor.execute('''INSERT INTO patient_profile (patient_id, gender, blood_group, contact_number, address, 
                            medical_history, allergies, current_medications, emergency_contact) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                           (userid, form.gender.data, form.blood_group.data, form.contact_number.data, form.address.data,
                            form.medical_history.data, form.allergies.data, form.current_medications.data,
                            form.emergency_contact.data))
            mysql.connection.commit()
            flash('Patient profile created successfully!', 'success')
            return redirect(url_for('profile'))
        return render_template('setup_patient_profile.html', form=form)

    flash('Invalid role.', 'danger')
    return redirect(url_for('home'))


@app.route('/setup_doctor_profile', methods=['GET', 'POST'])
def setup_doctor_profile():
    if 'loggedin' not in session or session.get('role') != 'doctor':
        return redirect(url_for('login'))

    form = DoctorProfileForm()
    if form.validate_on_submit():
        userid = session.get('userid')
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO doctor_profile (doctor_id, gender, specialization, experience_years, qualifications, 
                        hospital_affiliation, bio, contact_number, available_timeslots) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                       (userid, form.gender.data, form.specialization.data, form.experience_years.data,
                        form.qualifications.data, form.hospital_affiliation.data, form.bio.data,
                        form.contact_number.data, form.available_timeslots.data))
        mysql.connection.commit()
        flash('Doctor profile created successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('setup_doctor_profile.html', form=form)

from wtforms.fields import DateTimeLocalField

class AppointmentForm(FlaskForm):
    doctor_id = SelectField('Select Doctor', coerce=int, validators=[DataRequired()])
    appointment_date = DateTimeLocalField('Appointment Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Book Appointment')


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

        # Fetch doctor's email
        doctor_email = next((doctor['email'] for doctor in doctors if doctor['userid'] == doctor_id), None)

        # Send email notification to the doctor
        if doctor_email:
            subject = "New Appointment Request"
            body = f"Dear Doctor,\n\nYou have a new appointment request from {session['name']} on {appointment_date}.\n\nPlease log in to your dashboard to manage this appointment."
            send_email(subject, doctor_email, body)

        flash('Appointment booked successfully! A notification has been sent to the doctor.', 'success')
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


@app.route('/doctor/appointments', methods=['GET'])
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

    return render_template('doctor_appointments.html', appointments=appointments)

@app.route('/appointment/<int:appointment_id>/update', methods=['POST'])
def update_appointment(appointment_id):
    if 'loggedin' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))

    status = request.form.get('status')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Update appointment status
    cursor.execute('''
        UPDATE appointments 
        SET status = %s 
        WHERE appointment_id = %s
    ''', (status, appointment_id))
    mysql.connection.commit()

    # Fetch patient email and appointment details
    cursor.execute('''
        SELECT a.appointment_date, u.email, u.name AS patient_name 
        FROM appointments a 
        JOIN user u ON a.patient_id = u.userid 
        WHERE a.appointment_id = %s
    ''', (appointment_id,))
    appointment = cursor.fetchone()

    if appointment:
        patient_email = appointment['email']
        appointment_date = appointment['appointment_date']
        patient_name = appointment['patient_name']

        # Send email notification to the patient
        subject = "Appointment Status Update"
        body = f"Dear {patient_name},\n\nYour appointment on {appointment_date} has been updated to '{status}'.\n\nPlease log in to your account for more details."
        send_email(subject, patient_email, body)

    flash('Appointment updated successfully! A notification has been sent to the patient.', 'success')
    return redirect(url_for('doctor_appointments'))

@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    role = session['role']
    userid = session['userid']

    if role == 'patient':
        # Patient booking an appointment
        if request.method == 'POST':
            doctor_id = request.form.get('doctor_id')
            appointment_date = request.form.get('appointment_date')
            appointment_time = request.form.get('appointment_time')
            reason = request.form.get('reason')

            cursor = mysql.connection.cursor()
            cursor.execute('''INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason) 
                              VALUES (%s, %s, %s, %s, %s)''',
                           (userid, doctor_id, appointment_date, appointment_time, reason))
            mysql.connection.commit()
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('appointments'))

        # Fetch list of doctors for the patient to choose from
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT dp.doctor_id, u.name, dp.specialization 
            FROM doctor_profile dp
            JOIN user u ON dp.doctor_id = u.userid
        ''')
        doctors = cursor.fetchall()
        return render_template('book_appointment.html', doctors=doctors)

    elif role == 'doctor':
        # Doctor viewing their appointments
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''SELECT a.appointment_date, a.appointment_time, a.reason, 
                          u.name AS patient_name, p.contact_number 
                          FROM appointments a 
                          JOIN patient_profile p ON a.patient_id = p.patient_id 
                          JOIN user u ON p.patient_id = u.userid 
                          WHERE a.doctor_id = %s''', (userid,))
        appointments = cursor.fetchall()
        return render_template('view_appointments.html', appointments=appointments)

    flash('Invalid role.', 'danger')
    return redirect(url_for('home'))


# Run App
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

