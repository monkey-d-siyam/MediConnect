from flask import Blueprint

consultation = Blueprint('consultation', __name__, template_folder='templates')

from . import routes


