from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Regexp


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    phone_number = StringField('Phone number', validators=[DataRequired(), Length(min=5, max=15),
                                                           Regexp(r'^\+?[0-9]+$', message='Your number could contain '
                                                                                          'only "+" and numbers')])
    email = EmailField('Email', validators=[DataRequired(), Email(message='Your email must contain "@" and "."')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password_again = PasswordField('Password again', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email(message='Your email must contain "@" and "."')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')
