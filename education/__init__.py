from flask import Blueprint

# Initialize the education blueprint
education = Blueprint('education', __name__, template_folder="templates")

from . import routes  # Import routes to associate them with the blueprint