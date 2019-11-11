from mlb import db, login_manager
# from teams import get_teams, get_players
from sqlalchemy.dialects.postgresql import JSON
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(50), unique=True, nullable=False)
    email      = db.Column(db.String(50), unique=True, nullable=False)
    password   = db.Column(db.String(60), nullable=False)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Team(db.Model):
    id         = db.Column(db.Integer, primary_key=True, autoincrement=False)
    logo       = db.Column(db.String(50), unique=True, nullable=False)
    name       = db.Column(db.String(50), unique=True, nullable=False)
    shortName  = db.Column(db.String(50), unique=True, nullable=False)
    url        = db.Column(db.String(50), unique=True, nullable=False)
    league     = db.Column(db.String(30), unique=False, nullable=False)
    division   = db.Column(db.String(30), unique=False, nullable=False)
    players    = db.relationship('Player', backref='team', lazy=True)
    def __repr__(self):
        return f"{self.name} ({self.division}) ID - {self.id}"


class Player(db.Model):
    id         = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name       = db.Column(db.String(50), unique=False, nullable=False)
    position   = db.Column(db.String(50), unique=False)
    image_url  = db.Column(db.String(80))
    team_name  = db.Column(db.String(50), unique=False)
    active     = db.Column(db.Boolean, default=True)
    team_id    = db.Column(db.Integer, db.ForeignKey('team.id'))
    def __repr__(self):
        player_team = Team.query.filter_by(team_id = id).first()
        return f"{self.name}, {self.position} for the {player_team.name}"


class League(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    info = db.Column(JSON)
    def __repr__(self):
        return f"League('{self.info}')"
