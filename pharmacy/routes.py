from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from core.forms import InventoryForm
from extensions import mysql

pharmacy = Blueprint('pharmacy', __name__, template_folder='templates')

@pharmacy.route('/search_pharmacy', methods=['GET', 'POST'])
def search_pharmacy():
    pharmacies = []
    searched = False

    if request.method == 'POST':
        location = request.form.get('query')
        all_pharmacies = [
            {"name": "Pharmacy A", "address": "Dhaka, Bangladesh", "latitude": 23.8103, "longitude": 90.4125},
            {"name": "Pharmacy B", "address": "Chittagong, Bangladesh", "latitude": 22.3569, "longitude": 91.7832},
            {"name": "Pharmacy C", "address": "Rajshahi, Bangladesh", "latitude": 24.3636, "longitude": 88.6241},
        ]
        pharmacies = [
            pharmacy for pharmacy in all_pharmacies
            if "dhaka" in pharmacy["address"].lower() and location.lower() in pharmacy["address"].lower()
        ]
        searched = True

        if not pharmacies:
            flash('No pharmacies found for the given criteria.', 'danger')

    return render_template('search_pharmacy.html', pharmacies=pharmacies, searched=searched)

@pharmacy.route('/manage_inventory', methods=['GET', 'POST'])
def manage_inventory():
    if 'loggedin' not in session or session['role'] != 'pharmacy':
        return redirect(url_for('core.login'))

    form = InventoryForm()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT pharmacy_id FROM pharmacy_profile WHERE user_id = %s", (session['id'],))
    pharmacy_row = cursor.fetchone()
    if not pharmacy_row:
        flash("Pharmacy profile not found.", "danger")
        return redirect(url_for('core.pharmacy_dashboard'))
    pharmacy_id = pharmacy_row[0]

    if form.validate_on_submit():
        medicine_name = form.medicine_name.data
        stock = form.stock.data
        price = form.price.data

        cursor.execute("SELECT inventory_id FROM pharmacy_inventory WHERE pharmacy_id=%s AND medicine_name=%s", (pharmacy_id, medicine_name))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("UPDATE pharmacy_inventory SET stock=%s, price=%s WHERE inventory_id=%s", (stock, price, existing[0]))
            flash("Medicine updated.", "success")
        else:
            cursor.execute("INSERT INTO pharmacy_inventory (pharmacy_id, medicine_name, stock, price) VALUES (%s, %s, %s, %s)", (pharmacy_id, medicine_name, stock, price))
            flash("Medicine added.", "success")
        mysql.connection.commit()
        return redirect(url_for('pharmacy.manage_inventory'))

    cursor.execute("SELECT inventory_id, medicine_name, stock, price FROM pharmacy_inventory WHERE pharmacy_id=%s", (pharmacy_id,))
    inventory = cursor.fetchall()
    cursor.close()
    return render_template('manage_inventory.html', form=form, inventory=inventory)