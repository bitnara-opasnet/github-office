from get_api import get_xml_data
import xmltodict
import json

client_data = get_xml_data('https://100.64.0.100/admin/API/mnt/Session/ActiveList')
client_data = json.dumps(xmltodict.parse(client_data, process_namespaces=True))
client_data = json.loads(client_data)

