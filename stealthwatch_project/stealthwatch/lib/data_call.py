import json

def read_json(filename):
    path = '/home/bitnara/101-rest-apis/stealthwatch-enterprise-sample-scripts/json_data/'
    with open(path + filename, 'r') as json_file:
        result = json.load(json_file)
    return result