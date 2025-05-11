from flask import Blueprint, render_template
from .models import get_all_doctors

doctors_bp = Blueprint(
    'doctors',
    __name__,
    template_folder='templates'
)

@doctors_bp.route('/doctors')
def doctor_network():
    doctors = get_all_doctors()
    return render_template('doctors/doctor_network.html', doctors=doctors)