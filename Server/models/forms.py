from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    user = StringField("user", validators=[DataRequired()])
    password = PasswordField("password")