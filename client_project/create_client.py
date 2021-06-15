from get_api import get_auth_token, get_api_data
from get_device_random import random_data_create, device_devision
from get_api import get_xml_data
from get_random import random_data_create
import xmltodict
import json
import psycopg2
import re
import datetime
from pytz import timezone

def create_active(num, url, params):
    active_data = get_xml_data(url)
    active_data = json.dumps(xmltodict.parse(active_data, process_namespaces=True))
    active_data = json.loads(active_data)
    active_Session = active_data.get('activeList').get('activeSession')
    random_client = random_data_create(num, '/20', active_Session)

    final_list = []
    for i in active_Session:
        final_list.append(i)
    for i in random_client:
        final_list.append(i)
    active_dict = {'activeList':{"@noOfActiveSession": len(final_list), 'activeSession':final_list}}

    if params == 'dict':
        return(active_dict)
    elif params == 'xml':
        active_xml = xmltodict.unparse(active_dict, pretty=True, full_document=False)
        active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml
        return(active_xml)


def active_insert_DB(num, url, params='dict'):
    active_data = create_active(num, url, params)
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

def active_data_fromDB():
    host_name = '127.0.0.1'
    db_name = 'testdb'
    user_name = 'testuser'
    password = '1q2w3'
    table_name = 'active_session'

    conn = psycopg2.connect(host = host_name, dbname = db_name, user = user_name, password = password)
    cur = conn.cursor()
    cur.execute("select * from {};".format(table_name))
    table_col = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    active_data = []
    for i in rows:
        active_data.append(dict(zip(table_col,i)))
    cur.close()
    conn.close()
    return(active_data)

def get_ap_data():
    is_token = get_auth_token()['Token']
    device_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')
    AP_data = device_devision(device_data, 'Unified AP', 'ACCESS')
    return(AP_data)

def get_macaddr(ap, client, active_data, mac_addr):    
    client_data = json.dumps(xmltodict.parse(client, process_namespaces=True))
    client_data = json.loads(client_data)
    for i in active_data:
        if i.get('calling_station_id') == mac_addr:
            client_sample_data = client_data.get('sessionParameters').copy()
            active_sample_data = i
    attr_string = client_data.get('sessionParameters').get('other_attr_string')
    attr_string = re.sub(r'ID=+[a-z-0-9]+:','ID={}:'.format(ap[1].get('macAddress').replace(':','-')),attr_string)
    attr_string = re.sub(client_data.get('sessionParameters').get('user_name') , active_sample_data.get('user_name'), attr_string)
    cur_time = timezone('Asia/Seoul').localize(datetime.datetime.now())
    cur_time = cur_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + cur_time.isoformat()[-6:]
    client_sample_data.update({'user_name': active_sample_data.get('user_name'),
                            'framed_ip_address': active_sample_data.get('framed_ip_address'),
                            'calling_station_id': active_sample_data.get('calling_station_id'),
                            'orig_calling_station_id':active_sample_data.get('calling_station_id').replace(':','-').lower(),
                            'other_attr_string': attr_string, 'auth_acs_timestamp':cur_time,'auth_acsview_timestamp': cur_time})
    final_dic = dict({'sessionParameters':client_sample_data})
    client_xml = xmltodict.unparse(final_dic, full_document=False)
    client_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + client_xml
    return(client_xml)