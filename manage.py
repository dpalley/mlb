from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import os

from mlb import app, db

if app.config['ENV'] == 'development':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mlb:password@localhost:5432/mlb'

if app.config['ENV'] == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
