from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import json
import secrets
from sqlalchemy.dialects.postgresql import JSON


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mlb:password@localhost:5432/mlb'
db = SQLAlchemy(app)

from mlb import routes
