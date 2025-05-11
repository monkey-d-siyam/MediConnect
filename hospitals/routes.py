from flask import Blueprint, render_template, request, flash

hospitals = Blueprint('hospitals', __name__, template_folder='templates')

@hospitals.route('/search_hospital', methods=['GET', 'POST'])
def search_hospital():
    hospitals_list = []
    searched = False

    if request.method == 'POST':
        location = request.form.get('query')

        # Hardcoded hospital data for demo
        all_hospitals = [
            {"name": "Apollo Hospital", "address": "Dhaka, Bangladesh", "latitude": 23.8103, "longitude": 90.4125},
            {"name": "Square Hospital", "address": "Dhaka, Bangladesh", "latitude": 23.7508, "longitude": 90.3906},
            {"name": "United Hospital", "address": "Dhaka, Bangladesh", "latitude": 23.7925, "longitude": 90.4145},
        ]

        # Filter hospitals based on location
        hospitals_list = [
            hospital for hospital in all_hospitals
            if "dhaka" in hospital["address"].lower() and location.lower() in hospital["address"].lower()
        ]
        searched = True

        if not hospitals_list:
            flash('No hospitals found for the given criteria.', 'danger')

    return render_template('search_hospitals.html', hospitals=hospitals_list, searched=searched)