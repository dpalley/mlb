from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, IntegerField
from wtforms.validators import Length, Email, Required, EqualTo, ValidationError
from mlb.models import User, Team
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username         = StringField(validators = [Length(min=4, max=20)])
    email            = StringField(validators = [Email()])
    team_name        = StringField(validators = [Length(min=4, max=20)])
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

    def validate_team(self, team):
        team = Team.query.filter_by(name = team_name.data).first()
        if team:
            raise ValidationError('That team name is taken. Please choose another.')


class LoginForm(FlaskForm):
    email       = StringField('Email Address', validators = [Email()])
    password    = PasswordField('Password', validators = [Length(min=6, max=20)])
    remember_me = BooleanField('Remember Me')
    submit      = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username  = StringField(validators = [Length(min=4, max=20)])
    email     = StringField(validators = [Email()])
    team_name = StringField(validators = [Length(min=4, max=20)])
    submit    = SubmitField('Update')

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

    def validate_team_name(self, team_name):
        current_id = current_user.id
        current_team = Team.query.filter_by(id = current_id).first()
        if team_name.data != current_team.name:
            team = Team.query.filter_by(name = team_name.data).first()
            if team:
                raise ValidationError('That team name is taken. Please choose another.')

class TeamForm(FlaskForm):
    # https://stackoverflow.com/questions/23283348/validate-wtform-form-based-on-clicked-button
    # select   = ButtonField("Process", name="action", value=PROCESS)
    # team_name = StringField('team')
    # team_url  = StringField('url')
    # team_id   = StringField('id')
    submit    = SubmitField('test')

class SearchForm(FlaskForm):
    name   = StringField(validators = [Length(min=3)])
    # status = RadioField('Status', default = ('Y','Active'), choices=[('Y','Active'),('N','Inactive/Historic')])
    submit = SubmitField('Search')

class FantasySelectForm(FlaskForm):
    select    = SubmitField('Select')
    release   = SubmitField('Release')
    play      = SubmitField('Play')
    bench     = SubmitField('Bench')
    player_id = IntegerField()
