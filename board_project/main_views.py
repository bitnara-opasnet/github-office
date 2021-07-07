from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, g
from flask_sqlalchemy import SQLAlchemy
from flask_paginate import Pagination, get_page_parameter
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import login_required, login_user, logout_user, current_user
from models import Board, db, Support, User
import os
import sqlite3
import json
import datetime
from werkzeug.urls import url_encode

app = Flask(__name__)
# db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db = SQLAlchemy()
# migrate = Migrate()

base_path = os.path.dirname(os.path.abspath( __file__ )) 
db_path = os.path.join(base_path, 'board.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+db_path
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY']='asdfasdfasdfqwerty' 
app.config['JSON_AS_ASCII'] = False

db.init_app(app) 
migrate.init_app(app, db)
db.app = app  
db.create_all()  

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_request
def before_request():
    g.user = current_user

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        usertable = User(username=request.form['username'], email=request.form['email'], password=request.form['password']) 
        db.session.add(usertable) 
        db.session.commit() 
        return render_template("registered.html") 
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        data = User.query.filter_by(username=username, password=password).first()
        if data is None:
            return redirect(url_for('login'))
        else:
            session['username'] = request.form['username']
            login_user(data)
            return redirect(request.args.get('next') or url_for('board'))

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    logout_user()
    return redirect(url_for('login'))

# 게시판 내용 조회 (Read)
@app.route('/board')
@login_required 
def board():
    category_list = ['name', 'title']
    page=request.args.get(get_page_parameter(), type=int, default=1)
    category=request.args.get('category')
    keyword=request.args.get('keyword')
    page_url = request.args.get('page')
    limit = 5
    # print(page)
    if category and keyword:
        search_params = '&' + url_encode({'category':category, 'keyword':keyword}) #&category=title&keyword=abc
        if category == 'name': 
            boards = Board.query.filter(Board.name.contains(keyword)).order_by(Board.create_date.desc())
            boards = boards.paginate(page=page, per_page=5)
        elif category == 'title':
            boards = Board.query.filter(Board.title.contains(keyword)).order_by(Board.create_date.desc())
            boards = boards.paginate(page=page, per_page=5)
    else:
        search_params = ''
        boards = Board.query.order_by(Board.create_date.desc())
        boards = boards.paginate(page=page, per_page=5)
    return render_template('list.html', rows=boards, page=page, limit=limit, page_url=page_url, search_params = search_params, category_list=category_list)


# 게시판 내용 추가 (Create)
@app.route('/add',methods=["POST", "GET"])
@login_required
def add():
    if request.method == "POST":
        new_board = Board(name=request.form['name'], title=request.form['title'], content=request.form['content'], create_date=datetime.datetime.now())
        db.session.add(new_board)
        db.session.commit()
        return redirect(url_for("board"))
    else:  
        return render_template("input.html") 

#Detail
@app.route('/detail/<int:id>')
@login_required
def detail(id):
    category=request.args.get('category')
    keyword=request.args.get('keyword')
    search_params = '&' + url_encode({'category':category, 'keyword':keyword})
    row_id = id
    page = request.args.get('page')
    board = Board.query.filter_by(id=row_id).all()
    # print(page)
    return render_template("detail.html", rows=board, page=page, search_params=search_params)

# 게시판 내용 갱신 (Update) 
# @app.route('/detail/<string:title>/update', methods=["GET","POST"])
# def update(title):
#     if request.method == "POST":
#         name = request.form["name"]
#         title1 = request.form["title"]
#         content = request.form["content"]
#         conn = sqlite3.connect('board.db')
#         cur = conn.cursor()
#         cur.execute('UPDATE Board SET title = ? where name= ?', (title1, name))
#         cur.execute('UPDATE Board SET content = ? where name= ?', (content, name))
#         cur.execute('UPDATE Board SET create_date = ? where name= ?', (datetime.datetime.now(), name))
#         conn.commit()
#         return redirect(url_for("detail", title=title1))
#     else:  
#         name = title  
#         board = Board.query.filter_by(title=name).all()
#         return render_template("update.html", rows=board)

#게시판 내용 갱신 (Update) 
@app.route('/detail/<int:id>/update', methods=["GET","POST"])
@login_required
def update(id):
    category=request.args.get('category')
    keyword=request.args.get('keyword')
    # search_params = '&' + url_encode({'category':category, 'keyword':keyword})
    page=request.args.get('page')
    if request.method == "POST":
        row_id = id 
        title = request.form["title"]
        content = request.form["content"]
        board = Board.query.filter_by(id=row_id).first()
        board.title = title
        board.content = content 
        board.create_date = datetime.datetime.now()
        db.session.commit()
        return redirect(url_for("board", page=page, keyword=keyword, category=category))
    else:  
        row_id = id 
        board = Board.query.filter_by(id=row_id).all()
        return render_template("update.html", rows=board, keyword=keyword, category=category)


# 게시판 내용 삭제 (Delete)
# @app.route('/detail/<string:title>/delete') 
# def delete(title):
#     name = title  
#     conn = sqlite3.connect('board.db') 
#     cur = conn.cursor()
#     try:
#         cur.execute('DELETE FROM Board WHERE title = ?', (name,))
#         conn.commit() 
#     except:
#         db.session.rollback()
#     return redirect(url_for("board"))

# Delete
@app.route('/detail/<int:id>/delete') 
@login_required
def delete(id):
    row_id = id 
    board = Board.query.filter_by(id=row_id).first()
    db.session.delete(board)
    db.session.commit()
    return redirect(url_for("board")) 

# 검색하기
@app.route('/search', methods=["GET","POST"])
@login_required
def search(): 
    category_list = ['name', 'title']
    page=request.args.get(get_page_parameter(), type=int, default=1)
    category=request.args.get('category')
    keyword=request.args.get('keyword')
    page_url = request.args.get('page')
    limit = 5
    # boards = Board.query.all()
    if category and keyword:
        search_params = '&' + url_encode({'category':category, 'keyword':keyword}) 
        if category == 'name': 
            boards = Board.query.filter(Board.name.contains(keyword)).order_by(Board.create_date.desc())
            boards = boards.paginate(page=page, per_page=5)
        elif category == 'title':
            boards = Board.query.filter(Board.title.contains(keyword)).order_by(Board.create_date.desc())
            boards = boards.paginate(page=page, per_page=5)
    else:
        search_params = ''
        boards = Board.query.order_by(Board.create_date.desc())
        boards = boards.paginate(page=page, per_page=5)
    return render_template('search.html', rows=boards, page=page, limit=limit, page_url=page_url, search_params = search_params, category_list=category_list, keyword=keyword)

#문의 게시판
@app.route('/support', methods=["POST", "GET"])
@login_required
def support():
    if request.method == "POST":
        new_support = Support(name=request.form['name'], content=request.form['content'], phone=request.form['phonenumber'])
        db.session.add(new_support)
        db.session.commit()
        return redirect(url_for("board"))
    else:
        return render_template("support.html")

@app.route('/api')
def api():
    conn = sqlite3.connect('board.db')
    cur = conn.cursor()
    cur.execute("select * from board;")
    table_col = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    board_list = []
    for i in rows:
        board_list.append(dict(zip(table_col,i)))    
    return jsonify(board_list)

@app.route('/login2', methods=['GET', 'POST'])
def login2():
	if request.method == 'GET':
		return render_template('login.html')
	else:
		email = request.form['email']
		passw = request.form['password']
		try:
			data = User.query.filter_by(email=email, password=passw).first()
			if data is not None:
				session['logged_in'] = True
				return redirect(url_for('board'))
			else:
				return 'Dont Login'
		except:
			return "Dont Login"


