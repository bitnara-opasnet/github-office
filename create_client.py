from get_api import get_xml_data
from get_random import random_data_create
import xmltodict
import json

def active_dict(num, url):
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
    return(active_dict)

def active_xml(num, url):
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
    active_xml = xmltodict.unparse(active_dict, pretty=True, full_document=False)
    active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml
    return(active_xml)