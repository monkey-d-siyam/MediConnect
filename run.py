from flask import Flask
from dotenv import load_dotenv
import os
from consultation.routes import consultation  
from core import core
from appointment.routes import appointment
from education.routes import education
from pharmacy.routes import pharmacy
from hospitals.routes import hospitals
from doctors.routes import doctors_bp
from consultation import consultation
from extensions import mysql, mail, cache, socketio
from forum.routes import forum

# Load environment variables
load_dotenv()

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# MySQL config
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
mysql.init_app(app)

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')
mail.init_app(app)

# Cache config
cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})

# Initialize SocketIO
socketio.init_app(app)

# Register blueprints
app.register_blueprint(core)
app.register_blueprint(appointment, url_prefix='/appointment')
app.register_blueprint(education, url_prefix='/education')
app.register_blueprint(pharmacy, url_prefix='/pharmacy')
app.register_blueprint(hospitals, url_prefix='/hospitals')
app.register_blueprint(doctors_bp)
app.register_blueprint(consultation, url_prefix='/consultation')
app.register_blueprint(forum)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)