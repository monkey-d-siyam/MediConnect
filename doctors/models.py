from extensions import mysql

def get_all_doctors():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT doctor_id, gender, specialization, experience_years, qualifications,
               hospital_affiliation, bio, contact_number, available_timeslots
        FROM doctor_profile
    """)
    doctors = cur.fetchall()
    cur.close()
    return doctors