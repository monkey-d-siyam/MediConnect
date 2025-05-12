from flask import Blueprint, render_template, redirect, url_for, session, current_app
import random
import string
from flask_mail import Message
from extensions import mail, socketio

consultation = Blueprint('consultation', __name__)

@consultation.route('/request_video_consultation', methods=['GET'])
def request_video_consultation():
    room_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    session['room_name'] = room_name
    consultation_link = url_for('consultation.video_consultation', room_name=room_name, _external=True)
    socketio.emit('new_consultation', {'link': consultation_link}, namespace='/')
    doctor_email = "Mahibi.islam@g.bracu.ac.bd"
    send_email_to_doctor(doctor_email, consultation_link)
    return redirect(url_for('consultation.video_consultation', room_name=room_name))

@consultation.route('/video_consultation/<room_name>', methods=['GET'])
def video_consultation(room_name):
    return render_template('video_consultation.html', room_name=room_name)

def send_email_to_doctor(doctor_email, consultation_link):
    msg = Message(
        subject="New Video Consultation Request",
        sender='contactmediconnect@gmail.com',
        recipients=[doctor_email]
    )
    msg.body = f"Hello I am under the water Please HELP ME!!. Join the call using the link below:\n\n{consultation_link}"
    mail.send(msg)