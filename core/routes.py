from flask import render_template, redirect, url_for, session, request, flash
from . import core
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import check_password_hash, generate_password_hash
from MySQLdb.cursors import DictCursor
from .forms import LoginForm, RegistrationForm, DoctorProfileForm, PatientProfileForm
from extensions import mysql 
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/'  # Define the upload folder


@core.route('/')
def home():
    user = session.get('user')  # Assuming 'user' is stored in the session
    return render_template('core/home.html', title='Home', user=user)

@core.route('/about')
def about():
    return render_template('core/about.html', title='About')

@core.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM user WHERE email = %s", (form.email.data,))
        account = cursor.fetchone()
        if account and check_password_hash(account['password'], form.password.data):
            session['loggedin'] = True
            session['id'] = account['userid']
            session['name'] = account['name']
            session['role'] = account['role']
            session['email'] = account['email']

            if session['role'] == 'doctor':
                return redirect(url_for('core.doctor_dashboard'))
            elif session['role'] == 'patient':
                return redirect(url_for('core.patient_dashboard'))
            else:
                return redirect(url_for('core.home'))

        flash('Invalid email or password', 'danger')
    return render_template('core/login.html', title='Login', form=form)

@core.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user (name, email, password, role) VALUES (%s, %s, %s, %s)",
                       (form.name.data, form.email.data, hashed_password, form.role.data))
        mysql.connection.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('core.login'))
    return render_template('core/register.html', title='Register', form=form)

@core.route('/doctor_profile_setup', methods=['GET', 'POST'])
def doctor_profile_setup():
    if 'loggedin' in session and session['role'] == 'doctor':
        cursor = mysql.connection.cursor(DictCursor)

        # Check if the doctor profile already exists
        cursor.execute("SELECT * FROM doctor_profile WHERE doctor_id = %s", (session['id'],))
        doctor_profile = cursor.fetchone()

        if request.method == 'POST':
            gender = request.form['gender']
            specialization = request.form['specialization']
            experience_years = request.form['experience_years']
            qualifications = request.form['qualifications']
            hospital_affiliation = request.form['hospital_affiliation']
            bio = request.form['bio']
            contact_number = request.form['contact_number']
            available_timeslots = request.form['available_timeslots']

            if doctor_profile:
                # Update the existing profile
                cursor.execute("""
                    UPDATE doctor_profile
                    SET gender = %s, specialization = %s, experience_years = %s,
                        qualifications = %s, hospital_affiliation = %s, bio = %s,
                        contact_number = %s, available_timeslots = %s
                    WHERE doctor_id = %s
                """, (gender, specialization, experience_years, qualifications,
                      hospital_affiliation, bio, contact_number, available_timeslots, session['id']))
                flash('Profile updated successfully!', 'success')
            else:
                # Insert a new profile if it doesn't exist
                cursor.execute("""
                    INSERT INTO doctor_profile (doctor_id, gender, specialization, experience_years,
                                                qualifications, hospital_affiliation, bio, contact_number, available_timeslots)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (session['id'], gender, specialization, experience_years, qualifications,
                      hospital_affiliation, bio, contact_number, available_timeslots))
                flash('Profile created successfully!', 'success')

            mysql.connection.commit()
            return redirect(url_for('core.doctor_profile_setup'))

        # Pre-fill the form with existing data if available
        return render_template('core/doctor_profile_setup.html', form=DoctorProfileForm(data=doctor_profile), title='Doctor Profile Setup')
    return redirect(url_for('core.login'))

@core.route('/patient_profile_setup', methods=['GET', 'POST'])
def patient_profile_setup():
    if 'loggedin' in session and session['role'] == 'patient':
        cursor = mysql.connection.cursor(DictCursor)
        #Data fetch
        cursor.execute("SELECT * FROM patient_profile WHERE patient_id = %s", (session['id'],))
        profile = cursor.fetchone()

        #Prefilling the form
        form = PatientProfileForm(data=profile)

        if form.validate_on_submit():
            # File upload
            prescriptions_path = profile['prescriptions'] if profile else None
            medical_reports_path = profile['medical_reports'] if profile else None

            if form.prescriptions.data:
                prescriptions_file = form.prescriptions.data
                prescriptions_filename = secure_filename(prescriptions_file.filename)
                prescriptions_path = os.path.join(UPLOAD_FOLDER, prescriptions_filename)
                prescriptions_file.save(prescriptions_path)

            if form.medical_reports.data:
                medical_reports_file = form.medical_reports.data
                medical_reports_filename = secure_filename(medical_reports_file.filename)
                medical_reports_path = os.path.join(UPLOAD_FOLDER, medical_reports_filename)
                medical_reports_file.save(medical_reports_path)
            cursor.execute("""
                INSERT INTO patient_profile (patient_id, gender, blood_group, contact_number, address, medical_history, allergies, current_medications, emergency_contact, prescriptions, medical_reports)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                gender = VALUES(gender),
                blood_group = VALUES(blood_group),
                contact_number = VALUES(contact_number),
                address = VALUES(address),
                medical_history = VALUES(medical_history),
                allergies = VALUES(allergies),
                current_medications = VALUES(current_medications),
                emergency_contact = VALUES(emergency_contact),
                prescriptions = VALUES(prescriptions),
                medical_reports = VALUES(medical_reports)
            """, (
                session['id'], form.gender.data, form.blood_group.data, form.contact_number.data, form.address.data,
                form.medical_history.data, form.allergies.data, form.current_medications.data, form.emergency_contact.data,
                prescriptions_path, medical_reports_path
            ))
            mysql.connection.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('core.patient_dashboard'))

        return render_template('core/patient_profile_setup.html', title='Patient Profile Setup', form=form)
    return redirect(url_for('core.login'))

@core.route('/doctor_dashboard')
def doctor_dashboard():
    if 'loggedin' in session and session['role'] == 'doctor':
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("""
            SELECT dp.*, u.email 
            FROM doctor_profile dp 
            JOIN user u ON dp.doctor_id = u.userid 
            WHERE dp.doctor_id = %s
        """, (session['id'],))
        profile = cursor.fetchone()
        if profile:
            session['email'] = profile['email']
        return render_template('core/doctor_dashboard.html', profile=profile)
    return redirect(url_for('core.login'))

@core.route('/patient_dashboard')
def patient_dashboard():
    if 'loggedin' in session and session['role'] == 'patient':
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("""
            SELECT pp.*, u.email 
            FROM patient_profile pp 
            JOIN user u ON pp.patient_id = u.userid 
            WHERE pp.patient_id = %s
        """, (session['id'],))
        profile = cursor.fetchone()
        if profile:
            session['email'] = profile['email']

        return render_template('core/patient_dashboard.html', profile=profile)
    return redirect(url_for('core.login'))

@core.route('/doctor/appointments')
def doctor_appointments():
    if 'loggedin' in session and session['role'] == 'doctor':
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("""
            SELECT * FROM appointments
            WHERE doctor_id = %s
        """, (session['id'],))
        appointments = cursor.fetchall()
        return render_template('appointment/doctor_schedule.html', appointments=appointments)
    return redirect(url_for('core.login'))

@core.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('core.login'))