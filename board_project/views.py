from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_paginate import Pagination, get_page_parameter
from models import Board
import os
import sqlite3
import psycopg2

app = Flask(__name__)
db = SQLAlchemy(app)
# migrate = Migrate(app, db)

basedir = os.path.abspath(os.path.dirname(__file__)) 
dbfile = os.path.join(basedir, 'board.db') 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db.init_app(app) 
db.app = app 
db.create_all() 

@app.route('/')
def index():
    return "hello world"

# 게시판 내용 조회 (Read)
@app.route('/') 
def list():
    page=request.args.get(get_page_parameter(), type=int, default=1)
    boards = Board.query.all()
    boards = Board.query.paginate(page=page, per_page=5)
    return render_template('list.html', rows=boards) 

# 게시판 내용 추가 (Create)
@app.route('/add',methods=["POST", "GET"])
def add():
    if request.method == "POST":
        new_board = Board(name=request.form['name'], context=request.form['context'])
        db.session.add(new_board)
        db.session.commit()
        return redirect(url_for("index"))
    else:  
        return render_template("input.html")