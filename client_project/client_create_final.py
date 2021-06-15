from flask import Flask, Response
from get_api import get_xml_data
from create_client import create_active, active_data_fromDB, get_macaddr, active_insert_DB, get_ap_data

app = Flask(__name__)

@app.route('/admin/API/mnt/Session/ActiveList')
def getActiveList():
    # active_data = create_active(20, 'https://100.64.0.100/admin/API/mnt/Session/ActiveList', 'dict')
    active_data = active_insert_DB(1, 'https://100.64.0.100/admin/API/mnt/Session/ActiveList', 'dict')
    return Response(active_data, mimetype='application/xml')

AP_data = get_ap_data()
client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/68:EC:C5:DD:04:D2')

@app.route('/admin/API/mnt/Session/MACAddress/<string:macaddr>')
def getMACAddress(macaddr): 
    active_data = active_data_fromDB()
    client_data = get_macaddr(AP_data, client_sample, active_data, macaddr)
    return Response(client_data, mimetype='application/xml')

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')
