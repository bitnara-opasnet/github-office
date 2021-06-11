from flask import request
from flask_restx import Resource, Namespace, fields
import jwt
import bcrypt

users = {}
Auth = Namespace('Auth')

user_fields = Auth.model('User', {'id' : fields.String(description = 'User Id', Required=True)})
user_fields_auth = Auth.inherit('User Auth', user_fields, {'password' : fields.String(description = 'Password', Required=True)})
jwt_fields = Auth.model('JWT', {'Auth-Token': fields.String(description='Authorization', required=True)
})

@Auth.route('/')
class Authtoken(Resource):
    @Auth.expect(user_fields_auth)
    def post(self):
        id = request.json['id']
        password = request.json['password']
        users[id] = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return {'Token':  jwt.encode({'id': id}, "secret", algorithm="HS256").decode("UTF-8")}              

@Auth.route('/login')
class AuthLogin(Resource):
    @Auth.expect(user_fields_auth)   
    def post(self):
        id = request.json['id']
        return {'Token':  jwt.encode({'id': id}, "secret", algorithm="HS256").decode("UTF-8")}       