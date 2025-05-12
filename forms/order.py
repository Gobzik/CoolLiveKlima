from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed


class RegisterOrder(FlaskForm):
    name = StringField(
        'First Name',
        validators=[
            DataRequired(message="First name is required"),
            Length(min=2, max=50, message="First name must be between 2 and 50 characters")
        ]
    )

    surname = StringField(
        'Last Name',
        validators=[
            DataRequired(message="Last name is required"),
            Length(min=2, max=50, message="Last name must be between 2 and 50 characters")
        ]
    )

    phone_number = StringField(
        'Phone Number',
        validators=[
            DataRequired(message="Phone number is required"),
            Length(min=5, max=20, message="Phone number must be between 5 and 20 characters")
        ]
    )

    address = StringField(
        'Installation Address',
        validators=[
            DataRequired(message="Installation address is required"),
            Length(min=5, max=200, message="Address must be between 5 and 200 characters")
        ]
    )

    description = TextAreaField(
        'Additional Details',
        validators=[
            Length(max=500, message="Description cannot exceed 500 characters")
        ],
        render_kw={"placeholder": "Optional: Describe any special installation requirements"}
    )

    photo = FileField(
        'Upload Photo (if needed)'
    )

    submit = SubmitField('Submit Request')