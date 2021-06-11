from get_api import get_auth_token, get_api_data
from get_random import random_data_create, device_devision
from flask import jsonify
from flask_restx import Resource, Namespace

network_device = Namespace('network_device')

is_token = get_auth_token()['Token']
device_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')

AP_sample = device_devision(device_data, 'Unified AP', 'ACCESS')
final_AP = random_data_create(439, '/22', AP_sample, 'Unified AP', 'ACCESS')

Edge_sample = device_devision(device_data, 'Switches and Hubs', 'ACCESS')
final_Edge = random_data_create(50, '/24', Edge_sample, 'Switches and Hubs', 'ACCESS')

Border_sample = device_devision(device_data, 'Switches and Hubs', 'DISTRIBUTION')
final_Border = random_data_create(10, '/24', Border_sample, 'Switches and Hubs', 'DISTRIBUTION')

Router_sample = device_devision(device_data, 'Routers', 'BORDER ROUTER')
final_Router = random_data_create(1, '/24', Router_sample, 'Routers', 'BORDER ROUTER' )

final_list = []
for i in device_data.get('response'):
    final_list.append(i)
for i in final_AP:
    final_list.append(i)
for i in final_Edge:
    final_list.append(i)
for i in final_Border:
    final_list.append(i)
for i in final_Router:
    final_list.append(i)

final_dict = {'response':final_list, "version": "1.0"}

def finaldict():
    return(final_dict)


@network_device.route('/')
class GetData(Resource):
    def get(self):
        return jsonify(final_dict)