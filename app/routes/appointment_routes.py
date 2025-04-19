from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.forms.appointment_form import AppointmentForm
from app.extensions import mysql
import MySQLdb.cursors

appointment_bp = Blueprint('appointment', __name__, url_prefix='')

@appointment_bp.route('/appointments', methods=['GET', 'POST'])
def patient_appointments():
    if 'loggedin' not in session or session['role'] != 'patient':
        return redirect(url_for('auth.login'))

    form = AppointmentForm()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Populate doctor choices
    cursor.execute("SELECT userid, name FROM user WHERE role = 'doctor'")
    doctors = cursor.fetchall()
    form.doctor_id.choices = [(doctor['userid'], doctor['name']) for doctor in doctors]

    if form.validate_on_submit():
        patient_id = session['userid']
        doctor_id = form.doctor_id.data
        appointment_date = form.appointment_date.data

        cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, appointment_date)
            VALUES (%s, %s, %s)
        ''', (patient_id, doctor_id, appointment_date))
        mysql.connection.commit()

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointment.patient_appointments'))

    # Fetch patient appointments
    cursor.execute('''
        SELECT a.*, u.name AS doctor_name 
        FROM appointments a 
        JOIN user u ON a.doctor_id = u.userid 
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date
    ''', (session['userid'],))
    appointments = cursor.fetchall()

    return render_template('appointments.html', form=form, appointments=appointments)

@appointment_bp.route('/doctor/appointments', methods=['GET', 'POST'])
def doctor_appointments():
    if 'loggedin' not in session or session['role'] != 'doctor':
        flash('You must be logged in as a doctor to access this page.', 'danger')
        return redirect(url_for('auth.login'))

    doctor_id = session['userid']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

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

        status_map = {
            'approve': 'Approved',
            'decline': 'Declined',
            'reschedule': 'Rescheduled',
            'checked': 'Checked'
        }
        new_status = status_map.get(action)

        if new_status:
            cursor.execute('''
                UPDATE appointments
                SET status = %s
                WHERE appointment_id = %s
            ''', (new_status, appointment_id))
            mysql.connection.commit()
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('appointment.doctor_appointments'))

    return render_template('doctor_appointments.html', appointments=appointments)
