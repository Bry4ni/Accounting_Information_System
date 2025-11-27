import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('AIS_SECRET_KEY', 'dev-secret-key-change-this')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'ais.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
