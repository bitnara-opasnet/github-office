from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

db = SQLAlchemy()
     
class User(db.Model): 
    __tablename__ = 'user_table' 
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    userid = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, userid, email, password):
        self.userid = userid
        self.email = email
        # self.set_password(password)
        self.password = password
    
    # def set_password(self, password):
    #     self.password = generate_password_hash(password)
 
    # def check_password(self, password):
    #     return check_password_hash(self.password, password)
 
class Member(db.Model):	
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) 
    age = db.Column(db.Integer, nullable=False)
	
    def __init__(self,name,age):
        self.name = name
        self.age = age

class Board(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) 
    context = db.Column(db.String(50))
    
    def __init__(self,name,context):
        self.name = name
        self.context = context
