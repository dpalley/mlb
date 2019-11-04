from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import psycopg2
import json
import secrets
from sqlalchemy.dialects.postgresql import JSON
import os


app = Flask(__name__)

#set default config variables
app.debug = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(24)


# 'dev', 'prod', 'test'
ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mlb:password@localhost:5432/mlb'

if ENV == 'prod':
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hokalujnsvymxw:67b2b9de02ff6bba57f7ea38e160a6486341074dd4003327e98ca36dde2b8564@ec2-54-235-96-48.compute-1.amazonaws.com:5432/d1c3q968639kod'

if ENV == 'test':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mlb:password@localhost:5432/mlb'


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# change NO_TABLES to TRUE if database tables need to be created
NO_TABLES = True
if NO_TABLES:
    from mlb import routes
    from .models import User, Team, Player, League
    db.create_all()
