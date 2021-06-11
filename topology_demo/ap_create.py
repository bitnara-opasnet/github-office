#!/usr/bin/env python

import json

#local directory 확인
# file_path = "/user/user/physical-topology-demo1.json"
# with open('/python/dev1/pyshical-topology-demo1.json', "r") as json_file:
#      json_data = json.load(json_file)
#      print(json_data['nodes'])


with open('physical-topology-demo1.json', "r") as json_file:
     json_data = json.load(json_file)
     print(json_data['nodes'])

ori_node = json_data['nodes'][3]

str_ip = ori_node['ip']
str_macadd = ori_node['additionalInfo']['macAddress']
str_lab = ori_node['label']
str_id = ori_node['id']

result_data = []
for i in range(len(random_data)):
    random_data[i]['ip'] = str_ip[:-3] + str(int(str_ip[-3:]) +i)
    random_data[i]['additionalInfo']['macAddress'] = str_macadd[:-2] + str(int(str_macadd[-2:]) +i)
    random_data[i]['label'] = str_lab[:-4] + str(int(str_lab[-4:]) +i)
    random_data[i]['id'] = str_id[:-4] + str(int(str_id[-4:]) +i)
    print(random_data[i])
    #result_data.append(random_data[i])

result_data = []
for i in range(len(5)):
    dict()

print(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(2)))





res = []
for i in range(5):
    res.append(9509+i)
    print(res[i]) 