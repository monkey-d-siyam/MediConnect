from flask import Flask
from extensions import mysql, mail, cache  # Import cache from extensions
from core import core
from appointment.routes import appointment
from dotenv import load_dotenv
import os
from education.routes import education
from pharmacy.routes import pharmacy
from hospitals.routes import hospitals
from doctors.routes import doctors_bp
from consultation import consultation
from forum.routes import forum

# Load environment variables from .env file
load_dotenv()

# Create the Flask app
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# MySQL config
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')  # MySQL username
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')  # MySQL password (empty string)
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'mediconnect_db')  # Database name
mysql.init_app(app)

# Mail config
mail.init_app(app)

# Cache config
cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})  # Initialize Cache with app

# YouTube API config
app.config['YOUTUBE_API_KEY'] = os.getenv('YOUTUBE_API_KEY')

# PubMed API config
app.config['PUBMED_API_KEY'] = os.getenv('PUBMED_API_KEY')

# Register the blueprints
app.register_blueprint(core)
app.register_blueprint(appointment, url_prefix='/appointment')
app.register_blueprint(education, url_prefix='/education')
app.register_blueprint(pharmacy, url_prefix='/pharmacy')
app.register_blueprint(hospitals, url_prefix='/hospitals')
app.register_blueprint(doctors_bp)
app.register_blueprint(consultation, url_prefix='/consultation')
app.register_blueprint(forum)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)