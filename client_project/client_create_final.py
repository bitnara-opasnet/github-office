import xmltodict
from flask import Flask, Response
from get_api import get_xml_data
from active_DB import active_DB
from create_client import create_active, get_macaddr, get_device_sample

app = Flask(__name__) 

@app.route('/createActiveList') 
def createActiveList():
    active_data = create_active(wireless_num=1500, wired_num=100, url='https://100.64.0.100/admin/API/mnt/Session/ActiveList', params='dict')
    active_data = active_DB.active_insert_DB(active_data)
    return Response(active_data, mimetype='application/xml')

@app.route('/admin/API/mnt/Session/ActiveList')
def getActiveList():
    active_data = active_DB.active_data_fromDB_limit()
    active_dict = {'activeList':{"@noOfActiveSession": len(active_data), 'activeSession':active_data}}
    active_xml = xmltodict.unparse(active_dict, pretty=True, full_document=False)
    active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml
    return Response(active_xml, mimetype='application/xml')

wireless_data = get_device_sample('wireless')
wired_data = get_device_sample('wired')
wireless_client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/68:EC:C5:DD:04:D2')
wired_client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/00:0C:29:FD:D7:70')


@app.route('/admin/API/mnt/Session/MACAddress/<string:macaddr>')
def getMACAddress(macaddr): 
    active_data = active_DB.active_data_fromDB()
    client_data = get_macaddr(wireless_data, wired_data, active_data, wireless_client_sample,wired_client_sample,macaddr)
    return Response(client_data, mimetype='application/xml')

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')

