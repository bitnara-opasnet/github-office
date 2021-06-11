from get_api import get_xml_data
from get_random import random_data_create
import xmltodict
import json

client_data = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/ActiveList')
client_data = json.dumps(xmltodict.parse(client_data, process_namespaces=True))
client_data = json.loads(client_data)

active_Session = client_data.get('activeList').get('activeSession')
random_client = random_data_create(10, '/20', active_Session)

final_list = []
for i in active_Session:
    final_list.append(i)
for i in random_client:
    final_list.append(i)

final_dict = {'activeList':{"@noOfActiveSession": len(final_list), 'activeSession':final_list}}
final_xml = xmltodict.unparse(final_dict, pretty=True, full_document=False)
final_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + final_xml

def finalxml():
    return(final_xml)