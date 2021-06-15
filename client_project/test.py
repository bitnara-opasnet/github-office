from create_client import active_data_fromDB, get_macaddr, get_ap_data, create_active
from get_api import get_xml_data
from flask import Flask, Response
import xmltodict
import json
import psycopg2

def active_insert_DB(active_data):
    active_Session = active_data.get('activeList').get('activeSession')

    column_list = ['user_name', 'calling_station_id', 'nas_ip_address', 'acct_session_id', 'audit_session_id', 'server', 'framed_ip_address', 'framed_ipv6_address']
    data_list = []
    for i in active_Session:
        imsi_list = []
        for j in column_list:
            imsi_list.append(i.get(j))
        data_list.append(imsi_list)  

    host_name = '127.0.0.1'
    db_name = 'testdb'
    user_name = 'testuser'
    password = '1q2w3'
    table_name = 'active_session'
    create_query = """create table active_session (user_name varchar(255), calling_station_id varchar(255), nas_ip_address varchar(255), 
                                                    acct_session_id varchar(255), audit_session_id varchar(255), server varchar(255),
                                                    framed_ip_address varchar(255), framed_ipv6_address varchar(255));"""
    insert_query = """insert into active_session (user_name, calling_station_id, nas_ip_address, acct_session_id, audit_session_id, 
                        server, framed_ip_address, framed_ipv6_address) values(%s, %s, %s, %s, %s, %s, %s, %s);"""   

    try:
        conn = psycopg2.connect(host = host_name, dbname = db_name, user = user_name, password = password)
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS {};'.format(table_name))
        cur.execute(create_query)
        cur.executemany(insert_query, data_list)
        conn.commit()
        cur.close()
        conn.close() 
    except psycopg2.DatabaseError as db_err:
            print(db_err)

    active_xml = xmltodict.unparse(active_data, pretty=True, full_document=False)
    active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml
 
    return (active_xml)  

def Macaddr_roof():
    mac_addr_list = []
    for i in active_data: 
        mac_addr_list.append(get_xml_data('http://192.168.103.252:5000/admin/API/mnt/Session/MACAddress/{}'.format(i.get('calling_station_id'))))
    return (mac_addr_list)

AP_data = get_ap_data()
client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/68:EC:C5:DD:04:D2')
active_data = active_data_fromDB()

app = Flask(__name__)

@app.route('/admin/API/mnt/Session/ActiveList')
def getActiveList():
    active_data = create_active(20, 'https://100.64.0.100/admin/API/mnt/Session/ActiveList', 'dict')
    active_list = active_insert_DB(active_data)
    return Response(active_list, mimetype='application/xml')



@app.route('/admin/API/mnt/Session/MACAddress/<string:macaddr>')
def getMACAddress(macaddr): 
    AP_data = get_ap_data()
    client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/68:EC:C5:DD:04:D2')
    active_data = active_data_fromDB()
    client_data = get_macaddr(AP_data, client_sample, active_data, macaddr)
    return Response(client_data, mimetype='application/xml')

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')

client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/68:EC:C5:DD:04:D2')
client_data = json.dumps(xmltodict.parse(client_sample, process_namespaces=True))
client_data = json.loads(client_data)

column_list = ['passed', 'failed', 'started', 'stopped']
data_list = []
for i in column_list:
    print(client_data.get('sessionParameters').get(i))

[client_data.get('sessionParameters').pop(key) for key in ['passed', 'failed']] 
client_data.get('sessionParameters').pop('endpoint_policy') 

client_xml = xmltodict.unparse(client_data, full_document=False)


from collections import OrderedDict
od = OrderedDict()
od['passed'] = client_data.get('sessionParameters').get('passed')
od['failed'] = client_data.get('sessionParameters').get('failed')
