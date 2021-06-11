from get_api import get_xml_data
from get_random import random_data_create
from create_client import active_dict
import xmltodict
import json


active_data = active_dict(10, 'https://100.64.0.100/admin/API/mnt/Session/ActiveList')
active_Session = active_data.get('activeList').get('activeSession')
for i in active_Session:
    print(i.get('calling_station_id'))


client_data = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/68:EC:C5:DD:04:D2')
client_data = json.dumps(xmltodict.parse(client_data, process_namespaces=True))
client_data = json.loads(client_data)

sample_data = client_data.get('sessionParameters').copy()


final_data = []
for i in active_Session:
    sample_data.update({'calling_station_id':i.get('calling_station_id'), 'calling_station_id':random_data[i][1], 
                              'user_name':random_data[i][2]})
    random_dic1 = dict(sample_data_one.items())
    final_data.append(random_dic1)

# for i in s.split(':!:'):
# ...     print(i)