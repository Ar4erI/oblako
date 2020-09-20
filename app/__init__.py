import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager


# Init app
app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.secret_key = 'f48481f5948f6ced640f5292e92dee0a0db71346'
app.permanent_session_lifetime

# Init LoginManager
login_manager = LoginManager(app)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# Blueprints
from users import users
from admin import admin

app.register_blueprint(users, url_prefix='/user')
app.register_blueprint(admin, url_prefix='/admin')

from app import models, urls
