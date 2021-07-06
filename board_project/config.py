import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# BASE_DIR = os.path.dirname(__file__)
# SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'main.db'))
# SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
base_path = os.path.dirname(os.path.abspath( __file__ )) 
db_path = os.path.join(base_path, 'board.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+db_path
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

app.secret_key = os.urandom(24)
db = SQLAlchemy(app)