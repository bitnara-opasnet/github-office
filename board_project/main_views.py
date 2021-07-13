from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, g, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_paginate import Pagination, get_page_parameter
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import login_required, login_user, logout_user, current_user
from models import Board, db, Support, User, Stocks
import os
import sqlite3
import json
import datetime
from werkzeug.urls import url_encode
from lib.workbook import make_workbook, make_workbook_chart
from lib.get_api import get_auth_token, get_api_data
import requests
import pandas as pd

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

@app.route('/board/api')
@login_required
def board_api():
    conn = sqlite3.connect('board.db')
    cur = conn.cursor()
    cur.execute("select * from board;")
    table_col = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    board_list = []
    for i in rows:
        board_list.append(dict(zip(table_col,i)))    
    return jsonify(board_list)

@app.route('/user/api')
@login_required
def user_api():
    conn = sqlite3.connect('board.db')
    cur = conn.cursor()
    cur.execute("select * from user;")
    table_col = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    user_list = []
    for i in rows:
        user_list.append(dict(zip(table_col,i)))    
    return jsonify(user_list) 

@app.route('/board/download')
@login_required
def download():
    conn = sqlite3.connect('board.db')
    cur = conn.cursor()
    cur.execute("select * from board;")
    table_col = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    table_data = []
    for i in rows:
        table_data.append(list(i))
    table_data = tuple(table_data)
    make_workbook('board_list.xlsx', table_col, table_data)
    return send_file('board_list.xlsx', attachment_filename='board_list.xlsx')

@app.route('/stock')
def stock():
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()
    cur.execute("select * from stock;") 
    title = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    stock_list = []
        # for i in rows:
        #     stock_data.append(dict(zip(title,i)))
    for i in rows:
        stock_list.append(i)
    cur.close()
    conn.close()
    return render_template("device_detail.html", title=title, stock_list=stock_list)

@app.route('/stock2')
def stock2():
    keyword=request.args.get('keyword')
    page=request.args.get(get_page_parameter(), type=int, default=1)
    limit = 5
    if keyword:
        search_params = '&' + url_encode({'keyword':keyword}) 
        stocks = Stocks.query.filter(Stocks.name.contains(keyword)).order_by(Stocks.id.asc())
        stocks = stocks.paginate(page=page, per_page=5)
    else:
        search_params = ''
        stocks = Stocks.query.order_by(Stocks.id.asc())
        stocks = stocks.paginate(page=page, per_page=5)
    return render_template("stock_detail.html", stocks=stocks, page=page, limit=limit, keyword=keyword, search_params=search_params)

@app.route("/stock2/chart")
def CandleChart():
    name=request.args.get('name')
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    url = 'https://finance.naver.com/item/sise_day.nhn?code=005930&page=1'

    r = requests.get(url, headers={"user-agent": user_agent})
    tb = r.content.decode('euc-kr')
    table = pd.read_html(tb, header = 0)[0] 

    table = table.dropna()
    table = table[['날짜','저가','시가','종가','고가']]
    stock_list = []
    for i in range(len(table)):
        stock_list.append(list(table.iloc[i]))
    return render_template("detail_chart.html", chartData = stock_list, name=name)

@app.route('/stock/download')
def stockdownload():
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()
    cur.execute("select * from stock;") 
    title = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    stock_list = []
    for i in rows:
        stock_list.append(i)
    table_data = tuple(stock_list)
    make_workbook('stock_list.xlsx', title, table_data)
    return send_file('stock_list.xlsx', attachment_filename='stock_list.xlsx')

@app.route('/Devicelist')
def devicelist():
    is_token = get_auth_token()['Token']
    device_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')
    title_list = ['managementIpAddress', 'macAddress', 'role',  'platformId', 'hostname', 'softwareVersion']
    keyword = request.args.get('keyword')
    category = request.args.get('category')

    if category and keyword:
        search_params = '&' + url_encode({'category':category, 'keyword':keyword}) 
        category_list = []
        for i in device_data.get('response'):
            # category_list.append(i.get('managementIpAddress'))
            category_list.append(i.get(category))

        searched_list = []
        for ip in category_list:
            if ip.find(keyword) != -1 : 
                searched_list.append(ip)

        device_list = []
        for i in device_data.get('response'):
            imsi_list = []
            for j in searched_list:
                # if i.get('managementIpAddress') == j :
                if i.get(category) == j :
                    for k in title_list:
                        imsi_list.append(i.get(k))
            device_list.append(imsi_list)
        device_list = list(filter(None, device_list))
        device_list = tuple(device_list)

    else:
        search_params = ''
        device_list = []
        for i in device_data.get('response'):
            imsi_list = []
            for j in title_list:
                imsi_list.append(i.get(j))
            device_list.append(imsi_list)
        device_list = tuple(device_list)
     
    return render_template("device_list.html", device_list=device_list, search_params=search_params, title_list=title_list)

@app.route('/device_list/download')
def devicedownload():
    is_token = get_auth_token()['Token']
    device_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')
    title_list = ['managementIpAddress', 'macAddress', 'role',  'platformId', 'hostname', 'softwareVersion']

    device_list = []
    for i in device_data.get('response'):
        imsi_list = []
        for j in title_list:
            imsi_list.append(i.get(j))
        device_list.append(imsi_list)
    device_list = tuple(device_list)    

    df = pd.DataFrame(device_list, columns=title_list)
    chart_df = df.groupby('platformId').size().reset_index(name='count')
    chart_title = list(chart_df.columns)
    chart_data = []
    for i in range(len(chart_df)):
        chart_data.append(list(chart_df.iloc[i]))
    chart_data = tuple(chart_data)

    make_workbook_chart('device_list.xlsx', title_list, device_list, chart_title, chart_data, 11, 19, 'column', 'network device count_bar','H1')
    return send_file('device_list.xlsx', attachment_filename='device_list.xlsx', as_attachment=True)


