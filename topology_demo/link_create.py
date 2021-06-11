import json
import ipaddress
import random

with open('physical-topology-demo1.json', 'r') as json_file:
    json_data = json.load(json_file)

with open('random_node.json', 'r') as json_file1:
    node_data = json.load(json_file1)

ori_link = json_data['links']


data = {
    "endPortID": "567c4449-0add-49d0-8207-2516d7518876",
    "startPortIpv4Mask": "255.255.  0.  0",
    "startPortID": "",
    "startPortIpv4Address": "100.123.0.100",
    "target": "ce947941-f5b6-438e-9d3d-84e6d24aae0c",
    "value": "1",
    "linkStatus": "up",
    "endPortSpeed": "5000000",
    "additionalInfo": {},
    "count": 1,
    "startPortSpeed": "5000000",
    "startPortName": "GigabitEthernet0",
    "id": "252303",
    "portbpsdata": {},
    "usage": "[0/0]Mbps",
    "endPortName": "TenGigabitEthernet1/0/1",
    "source": "28975461-7826-4cac-b9f6-88aa9e5e3f3f"
}

link_list = []
for i in json_data['links']:
    link_list.append(i['source'])

#id 생성
def increase_num(num):
    n=num
    while True:
        n+=1
        yield n

n = increase_num(303)
id_sample = '252303'
id_sample[:-3] + str(next(n))

random_link_list = []
for i in node_data:
    random_link_list.append([i.get('id'), id_sample[:-3] + str(next(n))])

random_list1 = []
for i in range(len(random_link_list)):
    data.update({ 'id':random_link_list[i][0], 'source':random_link_list[i][1]})
    random_dic1 = dict(data.items())
    random_list1.append(random_dic1)

with open('random_link.json', 'w') as outfile:
    json.dump({'links' : random_list1}, outfile, indent=4)


data.update({'startPortIpv4Mask':data.get('startPortIpv4Mask').replace(" ","")})