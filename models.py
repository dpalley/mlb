from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from teams import get_teams, get_players
from sqlalchemy.dialects.postgresql import JSON


app = Flask(__name__)
db = SQLAlchemy(app)

class User(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(50), unique=True, nullable=False)
    email      = db.Column(db.String(50), unique=True, nullable=False)
    password   = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(50), nullable=False, default='default.jpg')
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Team(db.Model):
    id        = db.Column(db.Integer, primary_key=True, autoincrement=False)
    logo      = db.Column(db.String(50), unique=True, nullable=False)
    name      = db.Column(db.String(50), unique=True, nullable=False)
    shortName = db.Column(db.String(50), unique=True, nullable=False)
    url       = db.Column(db.String(50), unique=True, nullable=False)
    league    = db.Column(db.String(30), unique=False, nullable=False)
    division  = db.Column(db.String(30), unique=False, nullable=False)
    image_file = db.Column(db.String(50), nullable=False, default='default.jpg')
    def __repr__(self):
        return f"Team('{self.shortName}', '{self.image_file}')"

class Player(db.Model):
    id   = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(50), unique=False, nullable=False)
    image_file = db.Column(db.String(50), nullable=False, default='default.jpg')
    def __repr__(self):
        return f"Player('{self.name}', '{self.image_file}')"

class League(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    info = db.Column(JSON)
    def __repr__(self):
        return f"League('{self.info}')"
