from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchDoctorForm(FlaskForm):
    search = StringField('Search by Name or Specialization', validators=[DataRequired()])
    submit = SubmitField('Search')
