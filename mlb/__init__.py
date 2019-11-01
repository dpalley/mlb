from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import psycopg2
import json
import secrets
from sqlalchemy.dialects.postgresql import JSON


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(24)

# modify for Heroku
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mlb:password@localhost:5432/mlb'
# app.config['DATABASE_URL'] = 'postgresql://mlb:password@localhost:5432/mlb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
