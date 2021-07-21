"""Forms for Flask note app."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Length, Email

class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=50)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30)])

class LoginForm(FlaskForm):
    """Form for user login."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class AddNoteForm(FlaskForm):
    """Add note to user notes"""

    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = TextAreaField("Content", validators=[InputRequired()])

class UpdateNoteForm(FlaskForm):
    """Update note to user notes"""

    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = TextAreaField("Content", validators=[InputRequired()])
