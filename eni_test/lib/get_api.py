import requests
import base64

class getApi(object):
    def __init__(self):
        self.id = 'admin'
        self.password = 'Cisco!23'

    def get_auth_token(self):
        url = "https://100.64.0.101/dna/system/api/v1/auth/token"
        id = self.id
        pw = self.password
        cre = id+':'+pw
        credential_info = base64.b64encode(cre.encode('utf-8'))
        credential_info = 'Basic '+credential_info.decode('utf-8')
        payload = {}
        headers = {
            'content-type': 'application/json',
            'authorization': credential_info
        }
        x_auth_token = requests.request(
            "POST", url, headers=headers, data=payload, verify=False)
        return(x_auth_token.json())


    def get_api_data(self, token, uri_addr):
        url = uri_addr
        headers = {
            'X-Auth-Token': '{}'.format(token),
            'content-type': 'application/json'
        }
        response = requests.get(url, headers=headers, verify=False)
        return response.json()


    def get_xml_data(self, uri_addr):
        url = uri_addr
        id = self.id
        pw = self.password
        cre = id+':'+pw
        credential_info = base64.b64encode(cre.encode('utf-8'))
        credential_info = 'Basic '+credential_info.decode('utf-8')
        headers = {
            'Authorization': credential_info,
            'content-type': 'application/xml'
        }
        response = requests.get(url, headers=headers, verify=False)
        return response.text


    def get_json_data(self, uri_addr):
        url = uri_addr
        id = self.id
        pw = self.password
        cre = id+':'+pw
        credential_info = base64.b64encode(cre.encode('utf-8'))
        credential_info = 'Basic '+credential_info.decode('utf-8')
        headers = {
            'Authorization': credential_info,
            'content-type': 'application/json'
        }
        response = requests.get(url, headers=headers, verify=False)
        return response.json()
