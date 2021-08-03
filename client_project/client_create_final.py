import xmltodict
import random
import json
from flask import Flask, Response, jsonify
from lib.get_api import get_xml_data, get_json_data
from active_DB import active_DB
from create_client import create_active, get_macaddr, get_device_sample
from lib.random_topology import get_topology_data, get_random_topology, dna_topology_data, get_random_topology1, get_random_topology2, get_random_topology3
from lib.get_api import get_auth_token, get_api_data

app = Flask(__name__) 

@app.route('/createActiveList') 
def createActiveList():
    active_data = create_active(wireless_num=500, wired_num=200, url='https://100.64.0.100/admin/API/mnt/Session/ActiveList', params='dict')
    active_data = active_DB().active_insert_DB(active_data)
    return Response(active_data, mimetype='application/xml')

@app.route('/admin/API/mnt/Session/ActiveList')
def getActiveList():
    active_data = active_DB().active_data_fromDB_limit()
    active_dict = {'activeList':{"@noOfActiveSession": len(active_data), 'activeSession':active_data}}
    active_xml = xmltodict.unparse(active_dict, pretty=True, full_document=False)
    active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml
    return Response(active_xml, mimetype='application/xml')

wireless_data = get_device_sample('wireless')
wired_data = get_device_sample('wired') 
wireless_client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/68:EC:C5:DD:04:D2')
wired_client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/00:0C:29:FD:D7:70')
# wired_client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/00:0C:29:F6:99:95')


@app.route('/admin/API/mnt/Session/MACAddress/<string:macaddr>')
def getMACAddress(macaddr): 
    active_data = active_DB().active_data_fromDB()
    client_data = get_macaddr(wireless_data, wired_data, active_data, wireless_client_sample,wired_client_sample, macaddr)
    return Response(client_data, mimetype='application/xml')

@app.route('/createtopology')
def createtopology():
    final_dict = dna_topology_data(0)
    return jsonify(final_dict)

@app.route('/dna/intent/api/v1/network-device')
def networkdevice():
    is_token = get_auth_token()['Token']
    json_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')
    return jsonify(json_data)

@app.route('/dna/intent/api/v1/topology/physical-topology')
def getTopology():
    # final_dict = dna_topology_data(num) 
    num = random.randint(1,2)
    # final_dict = get_random_topology(num)
    # final_dict = get_random_topology1(num)
    final_dict = get_random_topology3(1, ap_num=1, rechable='Y', unrechable_num=0)
    # final_dict = get_random_topology4()
    print(len(final_dict['response'].get('nodes')))
    print(len(final_dict['response'].get('links')))
    return jsonify(final_dict)  

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8080)

