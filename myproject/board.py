from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from models import db, Board
import os
import sqlite3

app = Flask(__name__)
# board = []

# 게시판 내용 조회 (Read)
@app.route('/')
def index():
    engine = create_engine('sqlite:///board.db')
    board = engine.execute('SELECT * FROM Board;')
    # board = db.session.query(Board).all()
    return render_template('list.html', rows=board) 
  
# 게시판 내용 추가 (Create)
@app.route('/add',methods=["POST", "GET"])
def add():
    if request.method == "POST":
        new_board = Board(name=request.form['name'], context=request.form['context'])
        db.session.add(new_board)
        db.session.commit()
        return redirect(url_for("index"))
        # return render_template("add.html")
    else:  
        engine = create_engine('sqlite:///board.db')
        board = engine.execute('SELECT * FROM Board;')
        # return render_template("list.html", rows=board) 
        return render_template("input.html")
 
# 게시판 내용 갱신 (Update) 
@app.route('/update/<int:uid>', methods=["GET","POST"])
def update(uid):
    if request.method == "POST":
        index = uid
        name = request.form["name"]
        context = request.form["context"]
        conn = sqlite3.connect('board.db')
        cur = conn.cursor()
        cur.execute('UPDATE Board SET context = ? where id= ?', (context, index))
        cur.execute('UPDATE Board SET name = ? where id= ?', (name, index))
        conn.commit()
        return redirect(url_for("index"))
    else:  
        conn = sqlite3.connect('board.db') 
        cur = conn.cursor()  
        cur.execute('SELECT * FROM Board;')
        board = cur.fetchall()
        return render_template("update.html", index=uid, rows=board)
 
# 게시판 내용 삭제 (Delete)
@app.route('/delete/<int:uid>') 
def delete(uid):
    conn = sqlite3.connect('board.db') 
    cur = conn.cursor()
    index = uid 
    try:
        cur.execute('DELETE FROM Board WHERE id = ?', (index,))
        conn.commit() 
    except:
        db.session.rollback()
    return redirect(url_for("index"))

@app.route('/search', methods=["GET","POST"])
def search():
    if request.method == 'POST':
        name = request.form["name"]
        conn = sqlite3.connect('board.db')
        cur = conn.cursor()  
        cur.execute('SELECT * FROM board WHERE name = "{}";'.format(name))
        board = cur.fetchall()
        return render_template("search.html", rows=board)
    else:
        return render_template("search.html")

if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__)) 
    dbfile = os.path.join(basedir, 'board.db') 

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

    db.init_app(app) 
    db.app = app 
    db.create_all() 
 
    app.debug=True
    app.run(host='0.0.0.0', port=8080)
