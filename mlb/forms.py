from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import Length, Email, Required, EqualTo, ValidationError
from mlb.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username         = StringField(validators = [Length(min=4, max=20)])
    email            = StringField(validators = [Email()])
    password         = PasswordField(validators = [Length(min=6, max=20)])
    confirm_password = PasswordField(validators = [EqualTo('password')])
    submit           = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose another.')

class LoginForm(FlaskForm):
    email       = StringField('Email Address', validators = [Email()])
    password    = PasswordField('Password', validators = [Length(min=6, max=20)])
    remember_me = BooleanField('Remember Me')
    submit      = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField(validators = [Length(min=4, max=20)])
    email    = StringField(validators = [Email()])
    submit   = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose another.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose another.')

class TeamForm(FlaskForm):
    # https://stackoverflow.com/questions/23283348/validate-wtform-form-based-on-clicked-button
    # select   = ButtonField("Process", name="action", value=PROCESS)
    # team_name = StringField('team')
    # team_url  = StringField('url')
    # team_id   = StringField('id')
    submit    = SubmitField('test')

class SearchForm(FlaskForm):
    name   = StringField(validators = [Length(min=3)])
    status = RadioField('Status', choices=[('Y','Active'),('N','Inactive/Historic')])
    submit = SubmitField('Search')
