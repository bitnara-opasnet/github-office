from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, EqualTo
from models import User

class RegisterForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('password_2')]) #비밀번호 확인
    password_2 = PasswordField('repassword', validators=[DataRequired()])

class LoginForm(FlaskForm):
    class UserPassword(object):
        def __init__(self, message=None):
            self.message = message
            
        def __call__(self, form, field):
            userid = form['userid'].data
            password = field.data
            
            usertable = User.query.filter_by(userid=userid).first()
            if usertable.password != password:
            	raise ValueError('비밀번호 틀림')
                
    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), UserPassword()])

class BoardForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    context = TextAreaField('context', validators=[DataRequired()])