from flask import Flask, Response
from flask_restful import Api
from create_client import active_xml

app = Flask(__name__)
api = Api(app)

@app.route('/admin/API/mnt/Session/ActiveList')
def finalxml():
    active_data = active_xml(10, 'https://100.64.0.100/admin/API/mnt/Session/ActiveList')
    return Response(active_data, mimetype='application/xml')

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')