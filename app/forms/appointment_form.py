from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

class AppointmentForm(FlaskForm):
    doctor_id = SelectField('Select Doctor', coerce=int, validators=[DataRequired()])
    appointment_date = StringField('Appointment Date (YYYY-MM-DD)', validators=[DataRequired()])
    submit = SubmitField('Book Appointment')
