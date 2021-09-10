import os
import xmltodict
from flask import Flask, Response, jsonify, redirect, url_for, render_template, request, make_response, session
from lib.get_api import getApi
from lib.active_DB import active_DB
from lib.create_client import CreateClient
from lib.random_topology import get_random_topology3
from forms import TopologyForm, ClientForm
from models import Topology, db

app = Flask(__name__)

base_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_path, 'client.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+db_path
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'asdfasdfasdfqwerty'

db.init_app(app)
db.app = app
db.create_all()

# 인스턴스 생성
getapi = getApi()
active_db = active_DB()
# active_db.db_name = 'abc.db'
create_client = CreateClient()

wireless_data = create_client.get_device_sample('wireless')
wired_data = create_client.get_device_sample('wired')
wireless_client_sample = getapi.get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/D4:6D:6D:FA:85:0C')
wired_client_sample = getapi.get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/00:0C:29:FD:D7:70')
# wired_client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/00:0C:29:F6:99:95')

# active list 생성
@app.route('/createActiveList', methods=["GET", "POST"])
def createActiveList():
    form = ClientForm()
    if request.method == 'POST' and form.validate_on_submit():
        wireless_num = form.wireless_num.data
        wired_num = form.wired_num.data
        active_data = create_client.create_active(wireless_num, wired_num, url='https://100.64.0.100/admin/API/mnt/Session/ActiveList', params='dict')
        active_data = active_db.active_insert_DB(active_data)
        return Response(active_data, mimetype='application/xml')
    return render_template('client.html', form=form)

# active list 호출
@app.route('/admin/API/mnt/Session/ActiveList')
def getActiveList():
    active_data = active_db.active_data_fromDB_limit()
    active_dict = {'activeList': {"@noOfActiveSession": len(active_data), 'activeSession': active_data}}
    active_xml = xmltodict.unparse(active_dict, pretty=True, full_document=False)
    active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml
    return Response(active_xml, mimetype='application/xml')

# mac address로 세부내역 생성
@app.route('/admin/API/mnt/Session/MACAddress/<string:macaddr>')
def getMACAddress(macaddr):
    active_data = active_db.active_data_fromDB()
    client_data = create_client.get_macaddr(wireless_data, wired_data, active_data, wireless_client_sample, wired_client_sample, macaddr)
    return Response(client_data, mimetype='application/xml')

# network-device list 호출
@app.route('/dna/intent/api/v1/network-device')
def networkdevice():
    is_token = getapi.get_auth_token()['Token']
    json_data = getapi.get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')
    return jsonify(json_data)

# topology 생성
@app.route('/', methods=["GET", "POST"])
def physical_topology():
    form = TopologyForm()
    topology_id = Topology.query.count()
    if request.method == 'POST' and form.validate_on_submit():
        params = form.Params.data
        ap_num = form.ApNum.data
        edge_num = form.EdgeNum.data
        client_count = form.ClientCount.data
        rechable = form.rechable.data
        unrechable_num = form.UnrechableNum.data
        form_data = Topology(Params=params, ApNum=ap_num, EdgeNum=edge_num, ClientCount=client_count, rechable=rechable, UnrechableNum=unrechable_num)
        db.session.add(form_data)
        db.session.commit()
        # return jsonify(form_data)
        return render_template('physical-topology-sent.html', form=form, form_data=form_data)
    return render_template('physical-topology.html', form=form, topology_id=topology_id)

# topology 호출
@app.route('/dna/intent/api/v1/topology/physical-topology')
def getTopology():
    topology_id = Topology.query.count()
    topology = Topology.query.filter_by(id=topology_id).first()
    params = topology.Params
    ap_num = topology.ApNum
    edge_num = topology.EdgeNum
    client_count = topology.ClientCount
    rechable = topology.rechable
    unrechable_num = topology.UnrechableNum
    if params == 'N':
        final_dict = get_random_topology3('N', ap_num=0, edge_num=0, client_count=0, rechable='Y', unrechable_num=0)
    else:
        final_dict = get_random_topology3('Y', ap_num=ap_num, edge_num=edge_num, client_count=client_count, rechable=rechable, unrechable_num=unrechable_num)
    print(len(final_dict['response'].get('nodes')))
    print(len(final_dict['response'].get('links')))
    return jsonify(final_dict)
