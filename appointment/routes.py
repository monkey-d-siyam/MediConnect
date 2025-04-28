from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from .forms import SearchDoctorForm
from extensions import mysql
from MySQLdb.cursors import DictCursor

appointment = Blueprint('appointment', __name__)

@appointment.route('/appointments', methods=['GET'])
def appointments():
    if 'loggedin' in session:
        if session['role'] == 'doctor':
            return redirect(url_for('appointment.doctor_schedule'))  # Redirect to doctor_schedule
        elif session['role'] == 'patient':
            return redirect(url_for('appointment.patient_appointment_booking'))  # Redirect to patient_appointment_booking
    return redirect(url_for('core.login'))

@appointment.route('/patient_appointment_booking', methods=['GET', 'POST'])
def patient_appointment_booking():
    if 'loggedin' in session and session['role'] == 'patient':
        form = SearchDoctorForm()
        doctors = []
        if form.validate_on_submit():
            query = f"%{form.search.data}%"
            cursor = mysql.connection.cursor(DictCursor)
            cursor.execute("""
                SELECT DISTINCT u.userid AS doctor_id, u.name, dp.specialization
                FROM user u
                JOIN doctor_profile dp ON u.userid = dp.doctor_id
                WHERE u.role = 'doctor' AND (u.name LIKE %s OR dp.specialization LIKE %s)
            """, (query, query))
            doctors = cursor.fetchall()

        if request.method == 'POST' and 'doctor_id' in request.form:
            doctor_id = request.form['doctor_id']
            appointment_date = request.form['appointment_date']
            status = 'Pending'

            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (session['id'], doctor_id, appointment_date, status))
            mysql.connection.commit()
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('appointment.patient_appointment_booking'))

        return render_template('appointment/patient_appointment_booking.html', form=form, doctors=doctors)
    return redirect(url_for('core.login'))

@appointment.route('/doctor_schedule', methods=['GET', 'POST'])
def doctor_schedule():
    if 'loggedin' in session and session['role'] == 'doctor':
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("""
            SELECT a.appointment_id, p.name AS patient_name, a.appointment_date, a.status
            FROM appointments a
            JOIN patient_profile p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s
        """, (session['id'],))
        appointments = cursor.fetchall()
        return render_template('appointment/doctor_schedule.html', appointments=appointments)
    return redirect(url_for('core.login'))
