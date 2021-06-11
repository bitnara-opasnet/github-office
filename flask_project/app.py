from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
@app.route('/')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/test', methods=['GET','POST'])
def test():
    if request.method == 'GET':
        return render_template('post.html')
    elif request.method == 'POST':
        value = request.form['id']
        return value
    
@app.route('/jsonfile')
def jsonfile():
    with open('network_device.json', 'r') as json_file:
        json_data = json.load(json_file)
    column_list = ['managementIpAddress', 'macAddress', 'role',  'platformId', 'hostname']
    data_list = []
    for i in json_data.get('response'):
        inlist = []
        for j in column_list:
            inlist.append(i.get(j))
        data_list.append(inlist)

    final = []
    a = {}
    for data in data_list:
        for i,j in zip(column_list, data):
            a.update({i:j})
            dic1 = dict(a.items())
        final.append(dic1)
    return jsonify({'request': final})

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')

