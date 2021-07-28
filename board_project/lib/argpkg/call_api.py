import argparse
import requests
import json
import base64

def printdata(uri_addr, type):
    content_type = type
    url = uri_addr
    id = 'admin'
    pw = 'Cisco!23'
    cre = id+':'+pw
    credential_info = base64.b64encode(cre.encode('utf-8'))
    credential_info = 'Basic '+credential_info.decode('utf-8')
    headers = {
        'Authorization': credential_info,
        'content-type': 'application/{}'.format(content_type)
    }
    response = requests.get(url, headers=headers, verify=False)
    if content_type == 'json' :
        return response.json()
    else:
        return response.text

def savedata(title, data):
    with open(title, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)

parser = argparse.ArgumentParser()
# parser.add_argument('method', metavar='http_method', help='{GET|POST|PUT|DELETE}', choices=['GET', 'POST', 'PUT', 'DELETE'])
parser.add_argument('url', metavar='url', type=str, help='API url')
parser.add_argument('type', metavar='type', type=str, help='API content type')
parser.add_argument('--version', '-v', action='version', version ='%(prog)s 1.0.0')
parser.add_argument('-s', '--save', metavar='save', type=str, help='save data (input title)')
args = parser.parse_args()
# mtd = args.method
url = args.url
type = args.type
title = args.save
data = printdata(url, type)

if args.save:
    savedata(title, data)
    print('save file in directory')
else:
    print(data)