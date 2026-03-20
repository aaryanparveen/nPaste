from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PasteForm(FlaskForm):
    title = StringField('Title', validators=[Optional(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    language = SelectField('Language', choices=[
        ('text', 'Plain Text'), ('python', 'Python'), ('javascript', 'JavaScript'), 
        ('html', 'HTML'), ('css', 'CSS'), ('java', 'Java'), ('c', 'C'), 
        ('cpp', 'C++'), ('csharp', 'C#'), ('go', 'Go'), ('rust', 'Rust'),
        ('sql', 'SQL'), ('json', 'JSON'), ('xml', 'XML'), ('markdown', 'Markdown')
    ], default='text')
    tags = StringField('Tags (comma separated)', validators=[Optional(), Length(max=200)])
    custom_password = PasswordField('Password (Optional)', validators=[Optional()])
    is_private = BooleanField('Private Paste')
    expiry = SelectField('Expiration', choices=[
        ('never', 'Never'), ('10m', '10 Minutes'), ('1h', '1 Hour'), 
        ('1d', '1 Day'), ('1w', '1 Week'), ('1m', '1 Month')
    ], default='never')
    attachment = FileField('Attachment', validators=[FileAllowed(['txt', 'py', 'js', 'html', 'css', 'c', 'cpp', 'java', 'jpg', 'png', 'zip', 'pdf'], 'Images, Text or Archives only!')])
    submit = SubmitField('Create Paste')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Post Comment')

class PasswordCheckForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Access Paste')
