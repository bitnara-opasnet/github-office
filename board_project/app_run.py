import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import Board
from flask_migrate import Migrate
import main_views

app = main_views.app

if __name__=='__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=5000) 