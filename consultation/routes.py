from flask import Blueprint, render_template, redirect, url_for, session, current_app
import random
import string
from flask_mail import Message
from extensions import mail, socketio  # Import mail and socketio objects

consultation = Blueprint('consultation', __name__)

# Route for requesting a video consultation
@consultation.route('/request_video_consultation', methods=['GET'])
def request_video_consultation():
    # Generate a unique room name for the video call
    room_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    # Store the room name in the session
    session['room_name'] = room_name

    # Notify the doctor in real-time
    consultation_link = url_for('consultation.video_consultation', room_name=room_name, _external=True)
    socketio.emit('new_consultation', {'link': consultation_link}, namespace='/')

    # Send an email to the doctor
    doctor_email = "Mahibi.islam@g.bracu.ac.bd"  # Doctor's email
    send_email_to_doctor(doctor_email, consultation_link)

    # Redirect to the video consultation page
    return redirect(url_for('consultation.video_consultation', room_name=room_name))

# Route for joining the video consultation
@consultation.route('/video_consultation/<room_name>', methods=['GET'])
def video_consultation(room_name):
    return render_template('consultation/video_consultation.html', room_name=room_name)

def send_email_to_doctor(doctor_email, consultation_link):
    """Send an email to the doctor with the video consultation link."""
    msg = Message(
        subject="New Video Consultation Request",
        sender="contactmediconnect@gmail.com",  # Sender email
        recipients=[doctor_email]
    )
    msg.body = f"Hello I am under the water please help me!!!. Join the call using the link below:\n\n{consultation_link}"
    mail.send(msg)