from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Length, Email, Required, EqualTo


class RegistrationForm(FlaskForm):
    # username         = StringField(render_kw={"placeholder": "Username"}, validators = [Length(min=4, max=20)])
    # email            = StringField(render_kw={"placeholder": "Email"}, validators = [Email()])
    # password         = PasswordField(render_kw={"placeholder": "Password"}, validators = [Length(min=6, max=20)])
    # confirm_password = PasswordField(render_kw={"placeholder": "Confirm Password"}, validators = [EqualTo('password')])
    # accept_rules     = BooleanField('I accept the site rules', validators = [Required()])

    username         = StringField(validators = [Length(min=4, max=20)])
    email            = StringField(validators = [Email()])
    password         = PasswordField(validators = [Length(min=6, max=20)])
    confirm_password = PasswordField(validators = [EqualTo('password')])
    # accept_rules     = BooleanField('I accept the site rules', validators = [Required()])
    submit           = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email            = StringField('Email Address', validators = [Email()])
    password         = PasswordField('Password', validators = [Length(min=6, max=20)])
    remember_me      = BooleanField('Remember Me')
    submit           = SubmitField('Login')


class SearchForm(FlaskForm):
    pass