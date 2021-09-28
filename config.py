import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config(object):
    ENVIRONMENT = os.environ.get("ENVIRONMENT")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    DEBUG = os.environ.get("DEBUG")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
