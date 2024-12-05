from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from app.models import User

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class FavoriteForm(FlaskForm):
    anime_id = HiddenField('Anime ID', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    # Username field with length and required validation
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(3, 50, message="Username must be between 3 and 50 characters.")
    ])
    
    # Password field with length and required validation
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(6, 128, message="Password must be between 6 and 128 characters.")
    ])
    
    # Confirm password field, ensuring both inputs match
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message="Passwords must match.")
    ])
    
    # Submit button
    submit = SubmitField('Register')

    # Custom validation: check if the username already exists
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose another.')
        

class LoginForm(FlaskForm):
    # Username field for login
    username = StringField('Username', validators=[DataRequired()])
    
    # Password field for login
    password = PasswordField('Password', validators=[DataRequired()])
    
    # Submit button
    submit = SubmitField('Log In')