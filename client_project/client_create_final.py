from flask import Flask, Response
from flask_restful import Api
from create_client import finalxml

app = Flask(__name__)
api = Api(app)

@app.route('/admin/API/mnt/Session/ActiveList')
def finalxml():
    final_xml = finalxml()
    return Response(final_xml, mimetype='application/xml')

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')