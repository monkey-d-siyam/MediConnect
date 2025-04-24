from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from flask_wtf.file import FileField, FileAllowed

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('doctor', 'Doctor'), ('patient', 'Patient')], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DoctorProfileForm(FlaskForm):
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    specialization = StringField('Specialization', validators=[DataRequired()])
    experience_years = StringField('Years of Experience', validators=[DataRequired()])
    qualifications = StringField('Qualifications', validators=[DataRequired()])
    hospital_affiliation = StringField('Hospital Affiliation', validators=[DataRequired()])
    bio = TextAreaField('Short Bio', validators=[DataRequired(), Length(max=500)])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    available_timeslots = StringField('Available Timeslots', validators=[DataRequired()])
    submit = SubmitField('Save Profile')

class PatientProfileForm(FlaskForm):
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(max=15)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(max=255)])
    medical_history = TextAreaField('Medical History', validators=[DataRequired()])
    allergies = TextAreaField('Allergies', validators=[DataRequired()])
    current_medications = TextAreaField('Current Medications', validators=[DataRequired()])
    emergency_contact = StringField('Emergency Contact', validators=[DataRequired(), Length(max=15)])
    prescriptions = FileField('Upload Prescriptions (PDF)', validators=[FileAllowed(['pdf'], 'PDF files only!')])
    medical_reports = FileField('Upload Medical Reports (PDF)', validators=[FileAllowed(['pdf'], 'PDF files only!')])
    submit = SubmitField('Save Changes')
