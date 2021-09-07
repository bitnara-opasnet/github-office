from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange

class TopologyForm(FlaskForm):
    Params = RadioField('생성 여부', [DataRequired()], choices = [('Y','Y'),('N','N')], render_kw={'class': 'form-control'})
    ApNum = IntegerField ('AP 개수',  render_kw={'class': 'form-control'})
    EdgeNum = IntegerField('Edge 개수', render_kw={'class': 'form-control'})
    ClientCount = IntegerField('연결된 client수', render_kw={'class': 'form-control'})
    rechable = StringField('link 연결여부', [DataRequired()], render_kw={'class': 'form-control'})
    UnrechableNum = IntegerField('연결 해제할 link 개수', render_kw={'class': 'form-control'})

class ClientForm(FlaskForm):
    wireless_num = IntegerField ('무선 client 개수',  render_kw={'class': 'form-control'})
    wired_num = IntegerField('유선 client 개수', render_kw={'class': 'form-control'}) 
