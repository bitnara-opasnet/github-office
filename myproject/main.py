from flask import Flask, request, render_template, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import config
from models import Member, db	# main.py에서 Member 클래스를 import

 
app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

 
@app.route('/')
def _list():
    name = ['Elice', 'Dodo', 'Checher', 'Queen']
    age = 15
	
    # 주어진 name 리스트를 사용하고, 나이와 함께, DB에 추가
    for data in name:
        member = Member(data,age)
        age += 1
        db.session.add(member)
    db.session.commit()		# DB를 commit()
    member_list = Member.query.all()	# member_list에 Member의 모든 튜플 저장
 
    if(type(member_list)!=type([])):
        member_list=[member_list]
    return render_template('member_list.html', member_list=member_list)
 
if __name__ == "__main__":
    app.debug=True
    app.run(host='0.0.0.0')