from flask import Blueprint, render_template, request, flash

# Define the pharmacy blueprint
pharmacy = Blueprint('pharmacy', __name__, template_folder='templates')

@pharmacy.route('/search_pharmacy', methods=['GET', 'POST'])  # Corrected decorator
def search_pharmacy():
    pharmacies = []
    searched = False

    if request.method == 'POST':
        location = request.form.get('location')

        # Hardcoded pharmacy data
        all_pharmacies = [
            {"name": "Pharmacy A", "address": "Dhaka, Bangladesh", "latitude": 23.8103, "longitude": 90.4125},
            {"name": "Pharmacy B", "address": "Chittagong, Bangladesh", "latitude": 22.3569, "longitude": 91.7832},
            {"name": "Pharmacy C", "address": "Rajshahi, Bangladesh", "latitude": 24.3636, "longitude": 88.6241},
        ]

        # Filter pharmacies based on location or name
        pharmacies = [
            pharmacy for pharmacy in all_pharmacies
            if location.lower() in pharmacy["address"].lower() or location.lower() in pharmacy["name"].lower()
        ]
        searched = True

        if not pharmacies:
            flash('No pharmacies found for the given criteria.', 'danger')

    return render_template('search_pharmacy.html', pharmacies=pharmacies, searched=searched)