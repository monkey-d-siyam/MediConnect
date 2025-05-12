from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from datetime import datetime, timedelta

from .forms import SearchDoctorForm
from extensions import mysql
from MySQLdb.cursors import DictCursor

appointment = Blueprint('appointment', __name__, template_folder='templates')

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
            try:
                cursor.execute("""
                    SELECT DISTINCT u.userid AS doctor_id, u.name, dp.specialization
                    FROM user u
                    JOIN doctor_profile dp ON u.userid = dp.doctor_id
                    WHERE u.role = 'doctor' AND (u.name LIKE %s OR dp.specialization LIKE %s)
                """, (query, query))
                doctors = cursor.fetchall()
            except Exception as e:
                flash('An error occurred while searching for doctors.', 'danger')
                print(e)

        # Fetch the patient's appointments
        cursor = mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("""
                SELECT a.appointment_id, a.appointment_date, a.status, u.name AS doctor_name
                FROM appointments a
                JOIN user u ON a.doctor_id = u.userid
                WHERE a.patient_id = %s
                ORDER BY a.appointment_date DESC
            """, (session['id'],))
            appointments = cursor.fetchall()
        except Exception as e:
            flash('An error occurred while fetching your appointments.', 'danger')
            print(e)

        return render_template('appointment/patient_appointment_booking.html', form=form, doctors=doctors, appointments=appointments)
    return redirect(url_for('core.login'))

@appointment.route('/doctor_schedule', methods=['GET', 'POST'])
def doctor_own_schedule():
    if 'loggedin' in session and session['role'] == 'doctor':
        cursor = mysql.connection.cursor(DictCursor)

        # Fetch pending appointments
        cursor.execute("""
            SELECT a.appointment_id, u.name AS patient_name, a.appointment_date, a.status
            FROM appointments a
            JOIN user u ON a.patient_id = u.userid
            WHERE a.doctor_id = %s AND a.status = 'pending'
        """, (session['id'],))
        pending_appointments = cursor.fetchall()

        # Fetch approved appointments
        cursor.execute("""
            SELECT a.appointment_id, u.name AS patient_name, a.appointment_date, a.status
            FROM appointments a
            JOIN user u ON a.patient_id = u.userid
            WHERE a.doctor_id = %s AND a.status = 'approved'
        """, (session['id'],))
        approved_appointments = cursor.fetchall()

        # Handle POST request for updating appointment status
        if request.method == 'POST':
            appointment_id = request.form['appointment_id']  # Get the specific appointment ID
            new_status = request.form['status']
            if new_status == 'rescheduled':
                new_date = request.form['new_date']
                new_time = request.form['new_time']
                new_datetime = f"{new_date} {new_time}:00"
                cursor.execute("""
                    UPDATE appointments
                    SET status = %s, appointment_date = %s
                    WHERE appointment_id = %s
                """, (new_status, new_datetime, appointment_id))
            else:
                cursor.execute("""
                    UPDATE appointments
                    SET status = %s
                    WHERE appointment_id = %s
                """, (new_status, appointment_id))
            mysql.connection.commit()
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('appointment.doctor_own_schedule'))

        return render_template('appointment/doctor_schedule.html', pending_appointments=pending_appointments, approved_appointments=approved_appointments)
    return redirect(url_for('core.login'))

@appointment.route('/doctor_schedule/<int:doctor_id>', methods=['GET', 'POST'])
def doctor_schedule(doctor_id):
    if 'loggedin' in session and session['role'] == 'patient':
        cursor = mysql.connection.cursor(DictCursor)

        # Fetch booked slots for the doctor
        cursor.execute("""
            SELECT TIME(appointment_date) AS time_slot
            FROM appointments
            WHERE doctor_id = %s AND DATE(appointment_date) = CURDATE()
        """, (doctor_id,))
        booked_slots = [slot['time_slot'].strftime("%H:%M") for slot in cursor.fetchall()]

        # Generate available time slots (20-minute intervals)
        start_time = datetime.strptime("09:00", "%H:%M")
        end_time = datetime.strptime("17:00", "%H:%M")
        time_slots = []
        while start_time < end_time:
            time_slots.append(start_time.strftime("%H:%M"))
            start_time += timedelta(minutes=20)

        # Remove already booked slots
        available_slots = [slot for slot in time_slots if slot not in booked_slots]

        if request.method == 'POST':
            appointment_date = request.form['appointment_date']
            appointment_time = request.form['appointment_time']
            status = 'pending'

            # Combine date and time into a single datetime object
            appointment_datetime = f"{appointment_date} {appointment_time}:00"

            cursor.execute("""
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (session['id'], doctor_id, appointment_datetime, status))
            mysql.connection.commit()
            flash('Appointment request sent successfully!', 'success')
            return redirect(url_for('appointment.patient_appointment_booking'))

        return render_template('appointment/doctor_schedule.html', doctor_id=doctor_id, available_slots=available_slots, booked_slots=booked_slots)
    return redirect(url_for('core.login'))

@appointment.route('/doctor_available_slot/<int:doctor_id>', methods=['GET', 'POST'])
def doctor_available_slot(doctor_id):
    if 'loggedin' in session and session['role'] == 'patient':
        cursor = mysql.connection.cursor(DictCursor)

        # Fetch booked slots for the doctor
        cursor.execute("""
            SELECT TIME(appointment_date) AS time_slot
            FROM appointments
            WHERE doctor_id = %s AND DATE(appointment_date) = CURDATE()
        """, (doctor_id,))
        booked_slots = [slot['time_slot'].strftime("%H:%M") for slot in cursor.fetchall()]

        # Generate available time slots (20-minute intervals)
        start_time = datetime.strptime("09:00", "%H:%M")
        end_time = datetime.strptime("17:00", "%H:%M")
        time_slots = []
        while start_time < end_time:
            time_slots.append(start_time.strftime("%H:%M"))
            start_time += timedelta(minutes=20)

        # Remove already booked slots
        available_slots = [slot for slot in time_slots if slot not in booked_slots]

        if request.method == 'POST':
            appointment_date = request.form['appointment_date']
            appointment_time = request.form['appointment_time']
            status = 'pending'

            # Combine date and time into a single datetime object
            appointment_datetime = f"{appointment_date} {appointment_time}:00"

            # Check if the slot is already booked
            cursor.execute("""
                SELECT COUNT(*) AS count
                FROM appointments
                WHERE doctor_id = %s AND appointment_date = %s
            """, (doctor_id, appointment_datetime))
            result = cursor.fetchone()

            if result['count'] == 0:  # Slot is not booked
                cursor.execute("""
                    INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (session['id'], doctor_id, appointment_datetime, status))
                mysql.connection.commit()
                flash('Appointment request sent successfully!', 'success')
                return redirect(url_for('appointment.patient_appointment_booking'))
            else:
                flash('The selected time slot is already booked. Please choose another slot.', 'danger')

        return render_template('appointment/doctor_available_slot.html', doctor_id=doctor_id, available_slots=available_slots)
    return redirect(url_for('core.login'))
