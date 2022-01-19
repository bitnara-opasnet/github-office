import json
import requests
import http.client
import ssl
import datetime 
import time
import pytz
import urllib 
from smp.models import ApiConfig

class ConfingApi(object):
    def config_api(self):
        if not ApiConfig.objects.exists():
            ApiConfig.objects.create(ipaddress='0.0.0.0', username='', password='')
        api_config = ApiConfig.objects.first()
        return api_config

class ApiCall(object):
    def __init__(self, ip, username, pwd):
        self.ip = ip
        self.username = username
        self.pwd = pwd
        self.tenant_id = '232'

    def get_auth(self):
        url = "https://" + self.ip + "/token/v2/authenticate"
        login_request_data = {
            "username": self.username,
            "password": self.pwd
        }
        api_session = requests.Session()
        try: 
            response = api_session.request("POST", url, verify=False, data=login_request_data, timeout=5)
            for cookie in response.cookies:
                if cookie.name == 'XSRF-TOKEN':
                    xsrf_token = cookie.value
                if cookie.name == 'stealthwatch.jwt':
                    jwt_token = cookie.value

            headers = {'Cookie': 'X-XSRF-TOKEN=' + xsrf_token + ';' + 'stealthwatch.jwt=' + jwt_token}
            return headers
        except requests.exceptions.Timeout:
            print('timeout')
            return None
    
    def get_tenants(self):
        url = 'https://' + self.ip + '/sw-reporting/v1/tenants/'
        headers = self.get_auth()

        if headers: 
            conn = http.client.HTTPSConnection(self.ip, 443, context=ssl._create_unverified_context())
            conn.request("GET", url, headers=headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            tenant_list = json.loads(data)["data"]
            return tenant_list[0]['id']
        else:
            print('error')
            return None

    def get_hostgroup_list(self):
        # tenant_id = self.get_tenants()
        url = 'https://' + self.ip + '/smc-configuration/rest/v1/tenants/' + self.tenant_id + '/tags/tree'
        headers = self.get_auth()

        if headers: 
            conn = http.client.HTTPSConnection(self.ip, 443, context=ssl._create_unverified_context())
            conn.request("GET", url, headers=headers)
            res = conn.getresponse().read().decode("utf-8")
            hostgroup_list = json.loads(res)["data"]
            conn.close()
            return hostgroup_list
        else:
            return None
    
    def get_hostgroup_detail(self, tag_id):
        url = 'https://' + self.ip + '/smc-configuration/rest/v1/tenants/' + self.tenant_id + '/tags/' + str(tag_id)
        headers = self.get_auth()
        if headers: 
            conn = http.client.HTTPSConnection(self.ip, 443, context=ssl._create_unverified_context())
            conn.request("GET", url, headers=headers)
            res = conn.getresponse().read().decode("utf-8")
            hostgroup_detail = json.loads(res)["data"]
            conn.close()
            return hostgroup_detail 
        else:
            return None
    
    def get_api_session(self):
        url = "https://" + self.ip + "/token/v2/authenticate"
        login_request_data = {
            "username": self.username,
            "password": self.pwd
        }
        api_session = requests.Session()
        try: 
            response = api_session.request("POST", url, verify=False, data=login_request_data, timeout=3)
            for cookie in response.cookies:
                if cookie.name == 'XSRF-TOKEN':
                    api_session.headers.update({"X-XSRF-TOKEN": cookie.value})
                    break
            return api_session
        except requests.exceptions.Timeout:
            print('timeout')
            return None
    
    def get_host_list(self, search_time=5, record_limit=500, tag_id='', source_ip='', source_port='', destination_port=''):
        api_session = self.get_api_session()
        if api_session is not None:
            end_datetime = datetime.datetime.now(pytz.timezone('utc'))
            start_datetime = end_datetime - datetime.timedelta(minutes=search_time)
            end_timestamp = end_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            start_timestamp = start_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            # print(end_timestamp, start_timestamp)

            request_data = {
                "startDateTime": start_timestamp,
                "endDateTime": end_timestamp,
                "recordLimit": record_limit,
            }
            if source_ip:
                if source_ip.startswith('!'):
                    request_data.update({
                        "subject": {
                            "ipAddresses": {
                                "includes": [],
                                "excludes": [source_ip[1:]]
                            },
                        }
                    })
                else:   
                    request_data.update({
                        "subject": {
                            "ipAddresses": {
                                "includes": [source_ip],
                                "excludes": []
                            },
                        }
                    })  
            if source_port:
                if source_port.startswith('!'):
                    request_data.update({
                        "subject": {
                            "tcpUdpPorts": {
                                "includes": [],
                                "excludes": [source_port[1:]]
                            },
                        }
                    })
                else:   
                    request_data.update({
                        "subject": {
                            "tcpUdpPorts": {
                                "includes": [source_port],
                                "excludes": []
                            },
                        }
                    })
            if destination_port:
                if destination_port.startswith('!'):
                    request_data.update({
                        "subject": {
                            "tcpUdpPorts": {
                                "includes": [],
                                "excludes": [destination_port[1:]]
                            },
                        }
                    })
                else:   
                    request_data.update({
                        "subject": {
                            "tcpUdpPorts": {
                                "includes": [destination_port],
                                "excludes": []
                            },
                        }
                    })                                             
            if tag_id:
                request_data.update({
                    "subject": {
                        "hostGroups": {
                        "includes": [tag_id],
                        "excludes": []
                        },
                    }
                })
            url = 'https://' + self.ip + '/sw-reporting/v2/tenants/' + self.tenant_id + '/flows/queries'
            request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            response = api_session.request("POST", url, verify=False, data=json.dumps(request_data), headers=request_headers)
            search = json.loads(response.content)["data"]["query"]

            url = 'https://' + self.ip + '/sw-reporting/v2/tenants/' + self.tenant_id + '/flows/queries/' + search["id"]
            while search["percentComplete"] != 100.0:
                response = api_session.request("GET", url, verify=False)
                search = json.loads(response.content)["data"]["query"]
                time.sleep(1)
            
            url = 'https://' + self.ip + '/sw-reporting/v2/tenants/' + self.tenant_id + '/flows/queries/' + search["id"] + '/results'
            response = api_session.request("GET", url, verify=False)
            results = json.loads(response.content)["data"]["flows"]

            URI = 'https://' + self.ip + '/token'
            response = api_session.delete(URI, timeout=30, verify=False)
            api_session.headers.update({"X-XSRF-TOKEN": None})
        else:
            results = None
        return results

    def get_hostgroups_traffic(self, tag_id=1):
        api_session = self.get_api_session()
        if api_session:
            end_datetime = datetime.datetime.now(pytz.timezone('utc'))
            start_datetime = end_datetime - datetime.timedelta(days=7)
            end_timestamp = end_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            start_timestamp = start_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            request_data = {
                "startDate": start_timestamp,
                "endDate": end_timestamp,
            }

            url = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id + '/tags/'+ str(tag_id) + '/traffic/queries'
            request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            response = api_session.request("POST", url, verify=False, data=json.dumps(request_data), headers=request_headers)
            search = json.loads(response.content)["data"]

            # Perform the query to initiate the search
            URL = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id + '/tags/' + str(tag_id) + '/traffic/queries/' + search["queryId"]
            response = api_session.request("GET", URL, verify=False, data=json.dumps(request_data))
            search = json.loads(response.content)["data"]

            URL = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id + '/tags/' + str(tag_id) + '/traffic/results/' + search["id"]
            response = api_session.request("GET", URL, verify=False)
            results = json.loads(response.content)["data"]
        else:
            results = None
        return results

    def get_traffic(self, tag_id):
        traffic_url = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id  + '/internalHosts/tags/' + str(tag_id) + '/traffic/hourly'
        headers = self.get_auth()
        if headers: 
            end_datetime = datetime.datetime.now(pytz.timezone('utc'))
            start_datetime = end_datetime - datetime.timedelta(days=7)
            start_timestamp = int(time.mktime(start_datetime.timetuple())*1000)
            url = traffic_url + '?filter[startAbsolute]='+ str(start_timestamp)

            conn = http.client.HTTPSConnection(self.ip, 443, context=ssl._create_unverified_context())
            conn.request("GET", url, headers=headers)
            res = conn.getresponse().read().decode("utf-8")
            traffic_hourly = json.loads(res)["data"]
            conn.close()
            return traffic_hourly
        else:
            return None
    
    def get_application_traffic(self, tag_id):
        traffic_url = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id  + '/internalHosts/tags/' + str(tag_id) + '/applications/traffic/hourly'
        headers = self.get_auth()
        if headers: 
            end_datetime = datetime.datetime.now(pytz.timezone('utc'))
            start_datetime = end_datetime - datetime.timedelta(hours=12)
            start_timestamp = int(time.mktime(start_datetime.timetuple())*1000)
            url = traffic_url + '?filter[startAbsolute]='+ str(start_timestamp)

            conn = http.client.HTTPSConnection(self.ip, 443, context=ssl._create_unverified_context())
            conn.request("GET", url, headers=headers)
            res = conn.getresponse().read().decode("utf-8")
            traffic_hourly = json.loads(res)["data"]
            conn.close()
            return traffic_hourly
        else:
            return None

    def get_traffic_outside(self, tag_id):
        traffic_url = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id  + '/externalHosts/tags/' + str(tag_id) + '/traffic/hourly'
        headers = self.get_auth()
        if headers: 
            end_datetime = datetime.datetime.now(pytz.timezone('utc'))
            start_datetime = end_datetime - datetime.timedelta(days=7)
            start_timestamp = int(time.mktime(start_datetime.timetuple())*1000)
            url = traffic_url + '?filter[startAbsolute]='+ str(start_timestamp)

            conn = http.client.HTTPSConnection(self.ip, 443, context=ssl._create_unverified_context())
            conn.request("GET", url, headers=headers)
            res = conn.getresponse().read().decode("utf-8")
            traffic_hourly = json.loads(res)["data"]
            conn.close()
            return traffic_hourly
        else:
            None

    def get_application_traffic_outside(self, tag_id):
        traffic_url = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id  + '/externalHosts/tags/' + str(tag_id) + '/applications/traffic/hourly'
        headers = self.get_auth()
        if headers: 
            end_datetime = datetime.datetime.now(pytz.timezone('utc'))
            start_datetime = end_datetime - datetime.timedelta(hours=12)
            start_timestamp = int(time.mktime(start_datetime.timetuple())*1000)
            url = traffic_url + '?filter[startAbsolute]='+ str(start_timestamp)

            conn = http.client.HTTPSConnection(self.ip, 443, context=ssl._create_unverified_context())
            conn.request("GET", url, headers=headers)
            res = conn.getresponse().read().decode("utf-8")
            traffic_hourly = json.loads(res)["data"]
            conn.close()
            return traffic_hourly
        else:
            return None

    def get_flow_reports(self, search_time=5, search_item='', maxRows=1000, tags='', ipaddress=''):
        api_session = self.get_api_session()
        if api_session:
            end_datetime = datetime.datetime.now(pytz.timezone('utc'))
            start_datetime = end_datetime - datetime.timedelta(minutes=search_time)
            end_timestamp = end_datetime.strftime('%Y-%m-%dT%H:%M:%S.000')
            start_timestamp = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.000')
            request_data = {
                "startTime": start_timestamp,
                "endTime": end_timestamp,
                "maxRows": maxRows,
            }
            if tags:
                request_data.update({"subject": 
                                        {"tags":{
                                            "includes":
                                            [tags],
                                            }
                                        }
                                    })
            if ipaddress:
                request_data.update({"subject": 
                                        {"ipAddresses":{
                                            "includes":
                                            [ipaddress],
                                            }
                                        }
                                    })                

            url = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id + '/flow-reports/' + search_item + '/queries'

            request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            response = api_session.request("POST", url, verify=False, data=json.dumps(request_data), headers=request_headers)
            search = json.loads(response.content)["data"]

            # Perform the query to initiate the search
            URL = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id + '/flow-reports/' + search_item + '/queries/' + search["queryId"]
            response = api_session.request("GET", URL, verify=False, data=json.dumps(request_data))
            search = json.loads(response.content)["data"]

            URL = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id + '/flow-reports/' + search_item + '/results/' + search["queryId"]
            response = api_session.request("GET", URL, verify=False)
            results = json.loads(response.content)["data"]
        else:
            results = None
        return results