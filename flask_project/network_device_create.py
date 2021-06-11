from flask import Flask
from flask_restx import Api
from auth import Auth
from create_device import network_device

app = Flask(__name__)
api = Api(app)

api.add_namespace(network_device, '/network/device')
api.add_namespace(Auth, '/dna/system/api/v1/auth/token')

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')