from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, EmailField, validators


class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired(
        "Don't leave this blank empty !"), validators.length(min=5, max=40)])
    password = PasswordField(
        'Password', [validators.DataRequired("Don't leave this blank empty !")])


class RegistrationForm(FlaskForm):
    pass


class ForgotPasswordForm(FlaskForm):
    pass


class ResetPasswordForm(FlaskForm):
    pass
