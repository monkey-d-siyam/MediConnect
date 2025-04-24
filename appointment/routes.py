from flask import render_template, request, redirect, url_for, flash, session
from . import appointment
from .forms import SearchDoctorForm
from extensions import mysql

@appointment.route('/appointments', methods=['GET'])
def appointments():
    if 'loggedin' in session:
        if session['role'] == 'doctor':
            return render_template('appointment/doctor_schedule.html')
        elif session['role'] == 'patient':
            return render_template('appointmenttemplates/patient_appointment_booking.html')
    return redirect(url_for('core.login'))

@appointment.route('/patient_appointment_booking', methods=['GET', 'POST'])
def patient_appointment_booking():
    form = SearchDoctorForm()
    doctors = []
    if form.validate_on_submit():
        query = f"%{form.search.data}%"
        cursor = mysql.connection.cursor()  # Use DictCursor to fetch results as dictionaries
        cursor.execute("""
            SELECT DISTINCT u.userid, u.name, dp.specialization
            FROM user u
            JOIN doctor_profile dp ON u.userid = dp.doctor_id
            WHERE u.role = 'doctor' AND (u.name LIKE %s OR dp.specialization LIKE %s)
        """, (query, query))
        doctors = cursor.fetchall()  # Fetch results as a list of dictionaries
    return render_template('appointment/patient_appointment_booking.html', form=form, doctors=doctors)
