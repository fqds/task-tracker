from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

app = Flask(__name__)
app.secret_key = 'some secret salt'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config["POSTGRES"]["USERNAME"]}:{config["POSTGRES"]["PASSWORD"]}@{config["POSTGRES"]["HOST"]}:{config["POSTGRES"]["PORT"]}/{config["POSTGRES"]["NAME"]}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)

from web import models, routes

app.app_context().push()
db.create_all()
