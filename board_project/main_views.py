# -*- coding: utf-8 -*-
from platform import platform
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, g, send_file, escape, make_response
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
import requests
import psutil
from time import time
import pandas as pd
from datetime import timedelta
from werkzeug.urls import url_encode
from werkzeug.utils import secure_filename
from lib.xlsxpkg import make_chart, make_workbook
from lib.crawlingpkg.stock_crawling import stock_crawiling
from lib.apipkg.get_token import get_auth_token
from lib.apipkg.get_api import get_api_data, get_xml_data
from lib.random_topology import get_topology_data, get_hostname
from lib.sysinfo import getLoad, getplatform, net_io, cpu_info, swap_info, mem_info
from PIL import Image

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
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=120)

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
    username = session.get('username')
    if username is None:
        g.user = None
        username = ''
    else:
        g.user = User.query.get(username)
        username = '%s' % escape(session['username'])
    return render_template('index.html', username=username)
    # return redirect(url_for('login'))

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        usertable = User(username=request.form['username'], email=request.form['email'], password=request.form['password']) 
        db.session.add(usertable) 
        db.session.commit() 
        session['username'] = request.form['username']
        username = '%s' % escape(session['username'])
        return render_template("registered.html", username=username) 
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        error = None
        username = request.form['username'] 
        password = request.form['password']
        data = User.query.filter_by(username=username, password=password).first()
        if data is None:
            error = "Invalid username or password. Please try again!"
            # return redirect(url_for('login'))
            return render_template("login.html", error=error)
        else:
            session['username'] = request.form['username']
            login_user(data)
            return redirect(request.args.get('next') or url_for('board'))

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    logout_user()
    return redirect(url_for('main'))

@app.route('/user')
def user_detail():
    username = '%s' % escape(session['username'])
    user_data = User.query.filter_by(username=username).first()
    return render_template('user_detail.html', user_data=user_data)

@app.route('/user/<int:id>/update', methods=["GET","POST"])
def user_update(id):
    userid = id
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        user_data = User.query.filter_by(id=userid).first()
        user_data.name = name
        user_data.email = email
        user_data.password = password
        db.session.commit()
        return redirect(url_for("user_detail"))
    else:  
        user_data = User.query.filter_by(id=userid).first()
        return render_template("user_update.html", user_data=user_data)

# 게시판 내용 조회 (Read)
@app.route('/board')
@login_required 
def board():
    category_list = ['name', 'title']
    page=request.args.get(get_page_parameter(), type=int, default=1)
    category=request.args.get('category')
    keyword=request.args.get('keyword')
    page_url = request.args.get('page')
    limit = 7
    # print(page)
    if category and keyword:
        search_params = '&' + url_encode({'category':category, 'keyword':keyword}) #&category=title&keyword=abc
        if category == 'name': 
            boards = Board.query.filter(Board.name.contains(keyword)).order_by(Board.create_date.desc())
            boards = boards.paginate(page=page, per_page=limit)
        elif category == 'title':
            boards = Board.query.filter(Board.title.contains(keyword)).order_by(Board.create_date.desc())
            boards = boards.paginate(page=page, per_page=limit)
    else:
        search_params = ''
        boards = Board.query.order_by(Board.create_date.desc())
        boards = boards.paginate(page=page, per_page=limit)
    return render_template('list.html', rows=boards, page=page, limit=limit, page_url=page_url, search_params = search_params, category_list=category_list)

# 게시판 내용 추가 (Create)
@app.route('/add',methods=["POST", "GET"])
@login_required
def add():
    if request.method == "POST":
        if request.files['file'] :
            f = request.files['file']
            if f.filename.split('.')[1] in ['jpg', 'png']:
                # sfname = '/image/'+str(secure_filename(f.filename))
                # f.save('./static'+ sfname)
                sfname = str(secure_filename(f.filename))
                f.save('./static/image/'+ sfname)
                # image1 = Image.open('./static'+ sfname) 
                # imag1_size = image1.size
                # image1 = image1.resize((int(imag1_size[0]*(0.5)), int(imag1_size[1]*(0.5))))
                # imag1_size = image1.size
                # image1.save('./static'+ sfname)
            else:
                sfname = str(secure_filename(f.filename))
                f.save('./upload/'+ secure_filename(sfname))
        else:
            sfname = ''
        new_board = Board(name=request.form['name'], title=request.form['title'], content=request.form['content'], create_date=datetime.datetime.now(), image_name=sfname)
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
    board = Board.query.filter_by(id=row_id).first()
    return render_template("detail2.html", rows=board, page=page, search_params=search_params, board=board)

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
        board = Board.query.filter_by(id=row_id).first()
        title = request.form["title"]
        content = request.form["content"]
        if request.files['file'] :
            f = request.files['file']
            if f.filename.split('.')[1] in ['jpg', 'png']:
                sfname = str(secure_filename(f.filename))
                f.save('./static/image/'+ sfname)
            else:
                sfname = str(secure_filename(f.filename))
                f.save('./upload/'+ secure_filename(f.filename))
            board.image_name = sfname
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
    return jsonify({'response':board_list})

@app.route('/user/api')
# @login_required
def user_api():
    conn = sqlite3.connect('board.db')
    cur = conn.cursor()
    cur.execute("select * from user;")
    table_col = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    user_list = []
    for i in rows:
        user_list.append(dict(zip(table_col,i)))    
    return jsonify({'response':user_list}) 

@app.route('/board/download')
@login_required
def download(): 
    now = datetime.datetime.now().strftime('%Y%m%d')
    category=request.args.get('category')
    keyword=request.args.get('keyword')
    conn = sqlite3.connect('board.db')
    cur = conn.cursor() 
    if category and keyword :
        if category == 'name':
            cur.execute("select * from board where name like '%{}%';".format(keyword)) 
        elif category == 'title':
            cur.execute("select * from board where title like '%{}%';".format(keyword)) 
    else:
        cur.execute("select * from board;")
    table_col = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    table_data = []
    for i in rows:
        table_data.append(list(i))
    table_data = tuple(table_data)
    make_workbook.make_workbook('board_list_{}.xlsx'.format(now), table_col, table_data)
    return send_file('board_list_{}.xlsx'.format(now), attachment_filename='board_list_{}.xlsx'.format(now), as_attachment=True)

@app.route('/stock2')
@login_required
def stock2():
    # stock_crawiling()
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

# @app.route('/stock/download')
# @login_required
# def stockdownload():
#     conn = sqlite3.connect("stock.db")
#     cur = conn.cursor()
#     cur.execute("select * from stock;") 
#     title = [desc[0] for desc in cur.description]
#     rows = cur.fetchall()
#     stock_list = []
#     for i in rows:
#         stock_list.append(i)
#     table_data = tuple(stock_list)
#     make_workbook.make_workbook('stock_list.xlsx', title, table_data)
#     return send_file('stock_list.xlsx', attachment_filename='stock_list.xlsx', as_attachment=True)

@app.route('/stock/download')
@login_required
def stockdownloads():
    keyword=request.args.get('keyword')
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()
    if keyword :
        keyword=request.args.get('keyword')
        cur.execute("select * from stock where name like '%{}%';".format(keyword)) 
    else:
        keyword=''
        cur.execute("select * from stock;")
    title = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    stock_list = []
    for i in rows:
        stock_list.append(i)
    table_data = tuple(stock_list)
    make_workbook.make_workbook('stock_list.xlsx', title, table_data)
    return send_file('stock_list.xlsx', attachment_filename='stock_list.xlsx', as_attachment=True)

@app.route("/stock2/chart")
@login_required
def CandleChart():
    keyword=request.args.get('keyword')
    search_params = '&' + url_encode({'keyword':keyword}) 
    page=request.args.get('page')
    code=request.args.get('code')
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    url = 'https://finance.naver.com/item/sise_day.nhn?code={}&page=1'.format(code)
    r = requests.get(url, headers={"user-agent": user_agent})
    tb = r.content.decode('euc-kr')
    table = pd.read_html(tb, header = 0)[0] 

    table = table.dropna()
    table = table[['날짜','저가','시가','종가','고가']]
    stock_list = []
    for i in range(len(table)):
        stock_list.append(list(table.iloc[i]))
    
    stocks = Stocks.query.filter(Stocks.Code.contains(code)).order_by(Stocks.id.asc())
    return render_template("detail_chart.html", chartData = stock_list, code=code, stocks=stocks, page=page, search_params=search_params)

@app.route("/stock2/chart/download")
@login_required
def Chartdownload():
    code=request.args.get('code')
    name=request.args.get('name')
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    url = 'https://finance.naver.com/item/sise_day.nhn?code={}&page=1'.format(code)
    r = requests.get(url, headers={"user-agent": user_agent})
    tb = r.content.decode('euc-kr')
    table = pd.read_html(tb, header = 0)[0] 
    table = table.dropna()
    table = table[['날짜','저가','시가','종가','고가']]
    title = ['date','row','opening price','closing price','high']
    stock_list = []
    for i in range(len(table)):
        stock_list.append(list(table.iloc[i]))
    table_data = tuple(stock_list)
    make_workbook.make_workbook('chart.xlsx', title, table_data)
    return send_file('chart.xlsx', attachment_filename='chart.xlsx', as_attachment=True)

@app.route('/device_list')
@login_required 
def devicelist():
    # is_token = get_auth_token()['Token']
    # device_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')
    with open('network_device.json', 'r') as json_file:
        device_data = json.load(json_file)

    for i in device_data.get('response'):
        i.update({'Item': get_hostname(i)})

    title_list = ['Item','managementIpAddress', 'macAddress', 'role',  'platformId', 'hostname', 'softwareVersion']
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
        searched_list = set(searched_list)

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
        # device_list = tuple(device_list)
 
    else:
        search_params = ''
        device_list = []
        for i in device_data.get('response'):
            imsi_list = []
            for j in title_list:
                imsi_list.append(i.get(j))
            device_list.append(imsi_list)
        # device_list = tuple(device_list)
    
    df = pd.DataFrame(device_list, columns=title_list)
    chart_df = df.groupby('platformId').size().reset_index(name='count')
    chart = {}
    for i in range(len(chart_df['platformId'])):
        chart.update({chart_df['platformId'][i] : chart_df['count'][i]})
    return render_template("device_list.html", device_list=device_list, search_params=search_params, title_list=title_list, chart=chart)

@app.route('/device_list/download')
@login_required
def devicedownload():
    # is_token = get_auth_token()['Token']
    # device_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')
    with open('network_device.json', 'r') as json_file:
        device_data = json.load(json_file)

    for i in device_data.get('response'):
        i.update({'Item': get_hostname(i)})   

    title_list = ['Item','managementIpAddress', 'macAddress', 'role',  'platformId', 'hostname', 'softwareVersion']
    keyword = request.args.get('keyword')
    category = request.args.get('category')

    if category and keyword:
        category_list = []
        for i in device_data.get('response'):
            # category_list.append(i.get('managementIpAddress'))
            category_list.append(i.get(category))

        searched_list = []
        for item in category_list:
            if item.find(keyword) != -1 : 
                searched_list.append(item)
        searched_list = set(searched_list)

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
 
    else:
        device_list = []
        for i in device_data.get('response'):
            imsi_list = []
            for j in title_list:
                imsi_list.append(i.get(j))
            device_list.append(imsi_list)

    df = pd.DataFrame(device_list, columns=title_list)
    chart_df = df.groupby('platformId').size().reset_index(name='count')
    chart_title = list(chart_df.columns)
    chart_data = []
    for i in range(len(chart_df)):
        chart_data.append(list(chart_df.iloc[i]))

    device_list = tuple(device_list)     
    chart_data = tuple(chart_data)

    make_chart.make_workbook_chart('device_list.xlsx', title_list, device_list, chart_title, chart_data, 11, 19, 'column', 'network device count_bar','I1')
    return send_file('device_list.xlsx', attachment_filename='device_list.xlsx', as_attachment=True)

@app.route('/device_list/<int:id>/detail')
@login_required
def devicedetail(id):
    # is_token = get_auth_token()['Token']
    # device_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')
    with open('network_device.json', 'r') as json_file:
        device_data = json.load(json_file)
    category=request.args.get('category')
    keyword=request.args.get('keyword')
    search_params = '&' + url_encode({'category':category, 'keyword':keyword})
    row_id = id -1
    device_detail = device_data.get('response')[row_id]
    title_list = list(device_detail.keys())
    device_list = list(device_detail.values())
    return render_template("device_detail.html", device_list=device_list, title_list=title_list, device_detail=device_detail, search_params=search_params)

@app.route('/sample')
def logo():
    return render_template('logo_sample.html')

if not app.debug: # debug=False일때만 실행
    import logging
    from logging.handlers import RotatingFileHandler  
    file_handler = RotatingFileHandler(
        'dave_server.log', maxBytes=2000, backupCount=10)
    file_handler.setLevel(logging.WARNING)  #단계설정
    app.logger.addHandler(file_handler)
 
@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('page_not_found error')
    return "<h1> 404 error</h1>", 404

@app.route('/dna/intent/api/v1/topology/physical-topology')
@login_required
def getTopology():
    final_dict = get_topology_data() 
    return jsonify(final_dict)

@app.route('/sysinfo')
@login_required
def sysinfo():
    final_dict = getLoad()
    cpu = final_dict.get('cpu')
    memory = final_dict.get('memory')
    swap = final_dict.get('swap')
    disks = final_dict.get('disk')
    networks = final_dict.get('network')
    address=[]
    netmask=[]
    broadcast_=[]
    for network in networks:
        for key, values in network.items():
            for value in values:
                address.append(value.get('address'))
                netmask.append(value.get('netmask'))
                broadcast_.append(value.get('broadcast'))
    net_list = [address,netmask,broadcast_]
    plat = getplatform()
    return render_template("sysinfo.html", cpu=cpu, memory=memory, swap=swap, disks=disks, plat=plat, net_list=net_list, networks=networks)

@app.route('/sysinfodata')
@login_required
def sysinfodata():
    # sysinfodic = {'results':[]}
    sysinfodic = {}
    net_rst = net_io()
    cpu_rst = cpu_info()
    swap_rst = swap_info()
    mem_rst = mem_info()
    sysinfodic['net_rst'] = net_rst
    sysinfodic['cpu_rst'] = cpu_rst
    sysinfodic['swap_rst'] = swap_rst
    sysinfodic['mem_rst'] = mem_rst
    return jsonify(sysinfodic)

@app.route('/liveresource')
@login_required
def live_resource():
    return render_template("sysinfo2.html") 

@app.route('/sysinfodata2')
@login_required
def sysinfodata2(): 
    cpu = psutil.cpu_times_percent()
    idle = cpu.idle
    net = psutil.net_io_counters()
    sent = [time() * 1000, round(net.bytes_sent/1024, 2)]
    recv = [time() * 1000, round(net.bytes_recv/1024, 2)]
    data = {'sent':sent, 'recv':recv}
    # response = make_response(json.dumps(data))
    # response.content_type = 'application/json'
    # return response
    return jsonify(data)

@app.route('/sysinfodata3')
@login_required
def sysinfodata3(): 
    cpu = psutil.cpu_times_percent()
    idle = cpu.idle
    data = {'idle':idle}
    # response = make_response(json.dumps(data))
    # response.content_type = 'application/json'
    # return response
    return jsonify(data)