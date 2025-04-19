from flask import Blueprint, render_template, session, redirect, url_for
from app.extensions import mysql
import MySQLdb.cursors

profile_bp = Blueprint('profile', __name__, url_prefix='')

@profile_bp.route('/profile')
def profile():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

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
