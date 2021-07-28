import requests
import base64

def get_auth_token():
  url = "https://100.64.0.101/dna/system/api/v1/auth/token"
  id = 'admin'
  pw = 'Cisco!23' 
  cre = id+':'+pw
  credential_info = base64.b64encode(cre.encode('utf-8'))
  credential_info = 'Basic '+credential_info.decode('utf-8')
  payload = {}
  headers = {
      'content-type': 'application/json',
      'authorization': credential_info
  }
  x_auth_token = requests.request("POST", url, headers=headers, data=payload, verify=False)
  return(x_auth_token.json())