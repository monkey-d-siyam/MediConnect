from flask import Flask
from app.extensions import mysql, mail
from app.config import Config

# Blueprint imports
from app.routes.auth_routes import auth_bp
from app.routes.profile_routes import profile_bp
from app.routes.appointment_routes import appointment_bp
from app.routes.general_routes import general_bp

import os

def create_app():
    # Tell Flask where to find your templates (if outside /app)
    template_dir = os.path.abspath("templates")  # or adjust path if needed
    app = Flask(__name__, template_folder=template_dir)

    app.config.from_object(Config)

    # Initialize extensions
    mysql.init_app(app)
    mail.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(general_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
