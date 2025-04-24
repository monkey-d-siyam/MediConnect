from flask import Blueprint

appointment = Blueprint('appointment', __name__,template_folder='templates')

# Import routes after defining the blueprint
from . import routes
