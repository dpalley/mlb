from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import psycopg2
import json
import secrets
from sqlalchemy.dialects.postgresql import JSON
import os
import logging


app = Flask(__name__)

# log user activity for user CRUD and player draft/release
user_logger = logging.getLogger(__name__)
user_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:  %(levelname)s:  %(module)s:  %(funcName)s:  %(message)s:')
file_handler = logging.FileHandler('user_activity.log')
file_handler.setFormatter(formatter)
user_logger.addHandler(file_handler)

user_logger.info('Start/restart time')


#set default config variables
app.debug = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(24)

if app.config['ENV'] == 'development':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mlb:password@localhost:5432/mlb'

if app.config['ENV'] == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']


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
