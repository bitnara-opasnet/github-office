from create_client import active_data_fromDB, get_macaddr, get_device_sample, create_active
from get_api import get_xml_data
import xmltodict
import json
import re
import datetime
from pytz import timezone
from active_DB import active_DB

wired_client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/00:0C:29:FD:D7:70')
wireless_client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/68:EC:C5:DD:04:D2')

def get_macaddr(ap, client, mac_addr):
    active_data = active_data_fromDB()
    client_data = json.dumps(xmltodict.parse(client, process_namespaces=True))
    client_data = json.loads(client_data)
    for i in active_data:
        if i.get('calling_station_id') == mac_addr:
            active_sample_data = i
    if active_sample_data.get('user_name').endswith('s') == True:
        wireless_client_sample = client_data.get('sessionParameters').copy()
        attr_string = client_data.get('sessionParameters').get('other_attr_string')
        attr_string = re.sub(client_data.get('sessionParameters').get('user_name') , active_sample_data.get('user_name'), attr_string)
        if int(active_sample_data.get('user_name').split('r')[1])%2 == 0:
            attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], AP_data[0].get('macAddress').replace(':','-'))
        else:
            attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], AP_data[1].get('macAddress').replace(':','-'))
        attr_string = ':'.join(attr_split)
        cur_time = timezone('Asia/Seoul').localize(datetime.datetime.now())
        cur_time = cur_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + cur_time.isoformat()[-6:]
        client_sample_data.update({'user_name': active_sample_data.get('user_name'),
                                'framed_ip_address': active_sample_data.get('framed_ip_address'),
                                'calling_station_id': active_sample_data.get('calling_station_id'),
                                'orig_calling_station_id':active_sample_data.get('calling_station_id').replace(':','-').lower(),
                                'other_attr_string': attr_string, 'auth_acs_timestamp':cur_time,'auth_acsview_timestamp': cur_time})
        column_list = ['passed', 'failed', 'started', 'stopped']
        for i in column_list:
            client_sample_data.get(i)['@xsi:type'] = client_sample_data.get(i).pop('@http://www.w3.org/2001/XMLSchema-instance:type')
        final_dic = dict({'sessionParameters':client_sample_data})
        client_xml = xmltodict.unparse(final_dic, full_document=False)
        client_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + client_xml
    elif active_sample_data.get('user_name').endswith('d') == True:
        wired_client_sample = client_data.get('sessionParameters').copy()
    else:
        client_xml = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/{}'.format(mac_addr))
    return(client_xml)


def Macaddr_roof(num):
    active_data = active_DB.active_data_fromDB()
    url = 'http://192.168.103.252:5000/admin/API/mnt/Session/MACAddress/'
    mac_addr_list = []
    for i in range(num):
        mac_addr_list.append(get_xml_data(url + active_data[i].get('calling_station_id')))
    client_list = []
    for i in mac_addr_list:
        l = json.dumps(xmltodict.parse(i, process_namespaces=True))
        l = json.loads(l)
        client_list.append(l)
    return (client_list)

client_list = Macaddr_roof(10)

for i in client_list:
    if i.get('sessionParameters') == None:
        pass
    else:
        print(i.get('sessionParameters').get('destination_ip_address'))    

AP_data = get_device_sample('wireless')
client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/00:0C:29:FD:D7:70')
active_data = active_data_fromDB()

client_sample = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/68:EC:C5:DD:04:D2')
client_data = json.dumps(xmltodict.parse(client_sample, process_namespaces=True))
client_data = json.loads(client_data)
client_sample_data = client_data.get('sessionParameters').copy()

column_list = ['passed', 'failed', 'started', 'stopped']
for i in column_list:
    client_sample_data.get(i)['@xsi:type'] = client_sample_data.get(i).pop('@http://www.w3.org/2001/XMLSchema-instance:type')


final_dic = dict({'sessionParameters':active_data})
active_xml = xmltodict.unparse(final_dic, pretty=True, full_document=False)
active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml


active_data = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/ActiveList')
active_data = json.dumps(xmltodict.parse(active_data, process_namespaces=True))
active_data = json.loads(active_data)
active_Session = active_data.get('activeList').get('activeSession')


def random_data_create(wireless_num, wired_num, cidr, data): 
    wireless_ip = '100.100.10.104'
    wired_ip = '100.100.20.101'
    wireless_ip_list = get_hostip_list(wireless_ip, cidr, wireless_num)
    wired_ip_list = get_hostip_list(wired_ip, cidr, wired_num)
    n = increase_num(0)
    random_data = []
    for i in range(wireless_num + wired_num):
        random_mac = get_mac_addr()
        if random_mac in random_data:
            random_data.append([i, get_mac_addr(), 'user'+str(next(n))])
        else:
            random_data.append([i, random_mac,'user'+ str(next(n))])
    for i in data:              
        if i.get('framed_ip_address') == ip:
            sample_data_one = i.copy()
            break
    final_data = []
    for i in range(num):
        sample_data_one.update({'framed_ip_address':random_data[i][0], 'calling_station_id':random_data[i][1], 'user_name':random_data[i][2]})
        random_dic1 = dict(sample_data_one.items())
        final_data.append(random_dic1)
    return(final_data)

def create_active(wireless_num, wired_num, url, params):
    active_data = get_xml_data(url)
    active_data = json.dumps(xmltodict.parse(active_data, process_namespaces=True))
    active_data = json.loads(active_data)
    active_Session = active_data.get('activeList').get('activeSession')
    # wireless_client = random_data_create('100.100.10.104', wireless_num, '/16', active_Session)
    wired_client = random_data_create('100.100.20.101', wired_num, '/16', active_Session)
    final_list = []
    for i in active_Session:
        final_list.append(i)
    # for i in wireless_client:
    #     final_list.append(i)
    for i in wired_client:
        final_list.append(i)
    active_dict = {'activeList':{"@noOfActiveSession": len(final_list), 'activeSession':final_list}}
    if params == 'dict':
        return(active_dict)
    elif params == 'xml':
        active_xml = xmltodict.unparse(active_dict, pretty=True, full_document=False)
        active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml
        return(active_xml)
create_active(10, 5, 'https://100.64.0.100/admin/API/mnt/Session/ActiveList', 'dict')

if int(active_sample_data.get('user_name').split('_')[2])%2 == 0:
    attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wired_data[0].get('macAddress'))
else:
    attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wired_data[1].get('macAddress'))
attr_string = ':!:'.join(attr_split)