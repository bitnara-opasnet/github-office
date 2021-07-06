from flask import Flask, render_template, request, redirect, url_for, session
import os
from models import db, Board
import datetime


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'hello'

@app.route('/add',methods=["POST", "GET"])
def add():
    if request.method == "POST":
        new_board = Board(name=request.form['name'], title=request.form['title'], content=request.form['content'], create_date=datetime.datetime.now())
        db.session.add(new_board)
        db.session.commit()
        return redirect(url_for("index"))
    else:  
        return render_template("input.html")

basdir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basdir, 'board.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'jqiowejrojzxcovnklqnweiorjqwoijroi'

db.init_app(app)
db.app = app
db.create_all()

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8080)