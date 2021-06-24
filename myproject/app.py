# -*- coding: utf-8 -*-
import os 
from sqlalchemy import create_engine
from flask import Flask, render_template, request, redirect, session, url_for
from models import db
from models import User, Board
from flask_wtf.csrf import CSRFProtect 
from forms import RegisterForm, LoginForm, BoardForm
import sqlite3

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def mainpage():
    form = LoginForm() 
    if form.validate_on_submit():
        return redirect(url_for("login")) 
    # return render_template('login.html', form=form)
    return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit(): 
        usertable = User(userid=form.data.get('userid'), email=form.data.get('email'), password=form.data.get('password')) 
        db.session.add(usertable) 
        db.session.commit() 
        return "회원가입 성공" 
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])  
def login():
    form = LoginForm() 
    if form.validate_on_submit():
        session['userid']=form.data.get('userid')   
        return redirect(url_for("index"))   
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None) 
    return redirect('/')

@app.route('/list')
def index():
    engine = create_engine('sqlite:///db.sqlite')
    board = engine.execute('SELECT * FROM board;')
    # board = db.session.query(Board).all()
    return render_template('list.html', rows=board) 

# 게시판 내용 추가 (Create)
@app.route('/add',methods=["POST", "GET"])
def add():
    form = BoardForm()
    if request.method == "POST" and form.validate_on_submit():
        new_board = Board(name=request.form['name'], context=request.form['context'])
        db.session.add(new_board)
        db.session.commit()
        return redirect(url_for("index"))
    else:  
        return render_template("add.html", form=form)

# 게시판 내용 갱신 (Update) 
@app.route('/update/<int:uid>', methods=["GET","POST"])
def update(uid):
    form = BoardForm()
    if request.method == "POST" and form.validate_on_submit():
        index = uid
        name = request.form["name"]
        context = request.form["context"]
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        cur.execute('UPDATE Board SET context = ? where id= ?', (context, index))
        cur.execute('UPDATE Board SET name = ? where id= ?', (name, index))
        conn.commit()
        return redirect(url_for("index"))
    else:
        conn = sqlite3.connect('db.sqlite') 
        cur = conn.cursor()  
        cur.execute('SELECT * FROM Board;')
        board = cur.fetchall()
        return render_template("modify.html", index=uid, form=form, rows=board)
 
# 게시판 내용 삭제 (Delete)
@app.route('/delete/<int:uid>') 
def delete(uid):
    conn = sqlite3.connect('db.sqlite') 
    cur = conn.cursor()
    index = uid
    try:
        cur.execute('DELETE FROM Board WHERE id = ?', (index,))
        conn.commit() 
    except:
        db.session.rollback()
    return redirect(url_for("index"))

#r게시판 내용 검색
@app.route('/search', methods=["GET","POST"])
def search(): 
    form = BoardForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = request.form["name"]
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()  
        cur.execute('SELECT * FROM board WHERE name = "?"', (name,))
        rows = cur.fetchall()
        return render_template("search2.html", rows=rows, form=form)
    else:
        # conn = sqlite3.connect('db.sqlite')  
        # cur = conn.cursor()  
        # cur.execute('SELECT * FROM board where name = "Alice";')
        # board = cur.fetchall()
        # return render_template("search2.html",  rows=board, form=form)
        return render_template("search2.html", form=form)

if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__)) 
    dbfile = os.path.join(basedir, 'db.sqlite') 

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    app.config['SECRET_KEY']='asdfasdfasdfqwerty' 

    csrf = CSRFProtect()
    csrf.init_app(app)

    db.init_app(app) 
    db.app = app
    db.create_all() 
 
    app.debug=True
    app.run(host='0.0.0.0', port=8080)
