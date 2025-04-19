from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired

class DoctorProfileForm(FlaskForm):
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    specialization = StringField('Specialization')
    experience_years = IntegerField('Years of Experience')
    qualifications = StringField('Qualifications')
    hospital_affiliation = StringField('Hospital Affiliation')
    bio = StringField('Short Bio')
    contact_number = StringField('Contact Number')
    available_timeslots = StringField('Available Timeslots (e.g. Mon-Fri 9AM-1PM)')
    submit = SubmitField('Save Profile')

class PatientProfileForm(FlaskForm):
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    blood_group = StringField('Blood Group')
    contact_number = StringField('Contact Number')
    address = StringField('Address')
    medical_history = StringField('Medical History')
    allergies = StringField('Allergies')
    current_medications = StringField('Current Medications')
    emergency_contact = StringField('Emergency Contact')
    submit = SubmitField('Save Profile')
