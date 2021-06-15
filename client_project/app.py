from flask import Flask
from flask_restx import Resource, Api

app = Flask(__name__)
api = Api(app)


@api.route('/hello/<string:name>')  # url pattern으로 name 설정
class Hello(Resource):
    def get(self, name):  # 멤버 함수의 파라미터로 name 설정
        return "Welcome, %s!" % name
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')