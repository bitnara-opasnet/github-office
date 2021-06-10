from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from create_device import network_device, finaldict
import base64

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "SECRET_KEY"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
jwt = JWTManager(app)

@app.route('/')

@app.route('/dna/system/api/v1/auth/token', methods=['GET','POST'])
def user_login():
    if request.method == 'GET':
        return render_template('post.html')
    elif request.method == 'POST':
        header_params = request.headers.get('Authorization')
        header_params = header_params.split(' ')[1]
        header_params = base64.b64decode(header_params.encode('utf-8')).decode('utf-8')
        print(header_params)
        id = header_params.split(':')[0]
        password = header_params.split(':')[1]
        # id = request.form['id']
        # password = request.form['password']
        if not id:
            return jsonify({"msg": "Missing username parameter"}), 400
        if not id:
            return jsonify({"msg": "Missing password parameter"}), 400
        if id != 'admin' or password != 'Cisco!23':
            return jsonify({"msg": "Bad username or password"}), 401
            
        access_token = create_access_token(identity=id)
        return jsonify({'Token':access_token})


# 인증
@app.route("/dna/intent/api/v1/network-device", methods=["GET"])
# @jwt_required
def networkdevice():
    final_dict = finaldict()
    return jsonify(final_dict)

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')
