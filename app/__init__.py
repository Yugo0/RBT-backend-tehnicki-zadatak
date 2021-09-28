from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

from app import app
from app.arrangements import arrangement_bp

app.register_blueprint(arrangement_bp)
