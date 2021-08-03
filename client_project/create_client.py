from lib.get_api import get_auth_token, get_api_data, get_xml_data
from get_device_random import random_data_create, device_devision
from get_random import random_data_create
import xmltodict
import json
import re
import datetime
from pytz import timezone
import random

def create_active(wireless_num, wired_num, url, params):
    active_data = get_xml_data(url)
    active_data = json.dumps(xmltodict.parse(active_data, process_namespaces=True))
    active_data = json.loads(active_data)
    active_Session = active_data.get('activeList').get('activeSession')
    wireless_client = random_data_create('100.100.10.103', wireless_num, '/16', active_Session, 'wireless')
    wired_client = random_data_create('100.100.20.101', wired_num, '/16', active_Session, 'wired')
    final_list = []
    for i in active_Session:
        final_list.append(i)
    for i in wireless_client:
        final_list.append(i)
    for i in wired_client:
        final_list.append(i)
    active_dict = {'activeList':{"@noOfActiveSession": len(final_list), 'activeSession':final_list}}
    if params == 'dict': 
        return(active_dict)
    elif params == 'xml':
        active_xml = xmltodict.unparse(active_dict, pretty=True, full_document=False)
        active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml
        return(active_xml)  

def get_device_sample(params):
    is_token = get_auth_token()['Token']
    device_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')
    if params == 'wireless':
        device_sample = device_devision(device_data, 'Unified AP', 'ACCESS')
    elif params == 'wired':
        device_sample = device_devision(device_data, 'Switches and Hubs', 'ACCESS')
    return(device_sample)

def get_macaddr(wireless_device_data, wired_device_data, active_data, wireless_client, wired_client, mac_addr):
    for i in active_data:
        if i.get('calling_station_id') == mac_addr:
            active_sample_data = i
    if active_sample_data.get('user_name').split('_')[0] == 'wireless':
        client_data = json.dumps(xmltodict.parse(wireless_client, process_namespaces=True))
        client_data = json.loads(client_data)
        client_sample_data = client_data.get('sessionParameters').copy()
        attr_string = client_data.get('sessionParameters').get('other_attr_string')
        attr_string = re.sub(client_data.get('sessionParameters').get('user_name') , active_sample_data.get('user_name'), attr_string)
        attr_split = attr_string.split(':')
        if 'Called-Station-ID=7c-21-0d-9f-0a-20' in attr_split: 
            split_index = attr_split.index('Called-Station-ID=7c-21-0d-9f-0a-20')
        else:
            split_index = attr_split.index('Called-Station-ID=0c-75-bd-b7-9e-c0')
        if int(active_sample_data.get('user_name').split('_')[2])%2 == 0:
            attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wireless_device_data[0].get('macAddress').replace(':','-'))
        else:
            attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wireless_device_data[1].get('macAddress').replace(':','-'))
        attr_string = ':'.join(attr_split)
        cur_time = timezone('Asia/Seoul').localize(datetime.datetime.now())
        cur_time = cur_time.isoformat()[:-9] + cur_time.isoformat()[-6:]
        # if active_sample_data.get('user_name').split('_')[2].endswith(('1','2')):
        #     client_sample_data.update({'cts_security_group' : 'GR101'})
        # elif active_sample_data.get('user_name').split('_')[2].endswith(('3','4')):
        #     client_sample_data.update({'cts_security_group' : 'GR102'})
        # else:
        #     client_sample_data.update({'cts_security_group' : 'GR'+str(random.randint(103, 110))})
        client_sample_data.update({'user_name': active_sample_data.get('user_name'),
                                'framed_ip_address': active_sample_data.get('framed_ip_address'),
                                'calling_station_id': active_sample_data.get('calling_station_id'),
                                'orig_calling_station_id':active_sample_data.get('calling_station_id').replace(':','-').lower(),
                                'cts_security_group' : 'GR'+str(random.randint(1, 10)),
                                'other_attr_string': attr_string, 'acct_acs_timestamp':cur_time,'acct_acsview_timestamp': cur_time})
        column_list = ['passed', 'failed', 'started', 'stopped']
        for i in column_list:
            client_sample_data.get(i)['@xsi:type'] = client_sample_data.get(i).pop('@http://www.w3.org/2001/XMLSchema-instance:type')
        final_dic = dict({'sessionParameters':client_sample_data})
        client_xml = xmltodict.unparse(final_dic, full_document=False)
        client_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + client_xml
    elif active_sample_data.get('user_name').split('_')[0] == 'wired':
        client_data = json.dumps(xmltodict.parse(wired_client, process_namespaces=True))
        client_data = json.loads(client_data)
        client_sample_data = client_data.get('sessionParameters').copy()
        attr_string = client_data.get('sessionParameters').get('other_attr_string')
        attr_string = re.sub(client_data.get('sessionParameters').get('user_name') , active_sample_data.get('user_name'), attr_string)
        if attr_string.find(':!:') != -1 :
            attr_split = attr_string.split(':!:')
            split_index = attr_split.index('Called-Station-ID=DC:F7:19:00:63:02')
            if int(active_sample_data.get('user_name').split('_')[2])%2 == 0:
                attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wired_device_data[0].get('macAddress'))
            else:
                attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wired_device_data[1].get('macAddress'))
            attr_string = ':!:'.join(attr_split)
        else:
            attr_split = attr_string.split(',')
            split_index = attr_split.index('Called-Station-ID=DC:F7:19:00:63:02')
            if int(active_sample_data.get('user_name').split('_')[2])%2 == 0:
                attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wired_device_data[0].get('macAddress'))
            else:
                attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wired_device_data[1].get('macAddress'))
            attr_string = ','.join(attr_split)
        cur_time = timezone('Asia/Seoul').localize(datetime.datetime.now())
        cur_time = cur_time.isoformat()[:-9] + cur_time.isoformat()[-6:]
        # if active_sample_data.get('user_name').split('_')[2].endswith(('1','2')):
        #     client_sample_data.update({'cts_security_group' : 'GR101'})
        # elif active_sample_data.get('user_name').split('_')[2].endswith(('3','4')):
        #     client_sample_data.update({'cts_security_group' : 'GR102'})
        # else:
        #     client_sample_data.update({'cts_security_group' : 'GR'+str(random.randint(103, 110))})
        client_sample_data.update({'user_name': active_sample_data.get('user_name'),
                                'framed_ip_address': active_sample_data.get('framed_ip_address'),
                                'calling_station_id': active_sample_data.get('calling_station_id'),
                                'orig_calling_station_id':active_sample_data.get('calling_station_id').replace(':','-'),
                                'cts_security_group' : 'GR'+str(random.randint(1, 10)),
                                'other_attr_string': attr_string, 'acct_acs_timestamp':cur_time,'acct_acsview_timestamp': cur_time})
        if 'passed' in list(client_sample_data.keys()) :
            column_list = ['passed', 'failed', 'started', 'stopped']
        else:
            column_list = ['started', 'stopped']
        for i in column_list:
            client_sample_data.get(i)['@xsi:type'] = client_sample_data.get(i).pop('@http://www.w3.org/2001/XMLSchema-instance:type')
        final_dic = dict({'sessionParameters':client_sample_data})
        client_xml = xmltodict.unparse(final_dic, full_document=False)
        client_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + client_xml
    else:
        client_xml = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/{}'.format(mac_addr))
    return(client_xml)