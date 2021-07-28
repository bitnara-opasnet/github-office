from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) 
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text)
    create_date = db.Column(db.DateTime(), nullable=False)
    image_name = db.Column(db.String(50)) 

    def __init__(self, name, title, content, create_date, image_name):
        self.name = name
        self.title = title
        self.content = content
        self.create_date = create_date
        self.image_name = image_name
    
    def __repr__(self):
        return '<name {}>'.format(self.name)

class Support(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) 
    phone = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(100))    

    def __init__(self,name,phone,content):
        self.name = name
        self.phone = phone
        self.content = content
    
    def __repr__(self):
        return '<name {}>'.format(self.name)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Stocks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    nowVal = db.Column(db.String(200))
    PrePricenowVal = db.Column(db.String(120))
    fluctuation = db.Column(db.String(120))
    faceVal = db.Column(db.String(120))
    totalVal = db.Column(db.String(120))
    stockListNum = db.Column(db.String(120))
    ROF = db.Column(db.String(120))
    volume = db.Column(db.String(120))
    PER = db.Column(db.String(120))
    ROE = db.Column(db.String(120))
    Code = db.Column(db.String(120))

    def __repr__(self):
        return '<name {}>'.format(self.name)

