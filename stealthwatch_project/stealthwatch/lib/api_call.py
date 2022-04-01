import json
import requests
import http.client
import ssl
import datetime 
import time
import pytz
import urllib
import pandas as pd
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
    
    def get_host_list(self, search_time=5, record_limit=500, source_group='', source_ip='', source_port='', destination_ip = '', destination_port='', destination_group='', application_id=''):
        api_session = self.get_api_session() 
        if api_session:
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
            if source_group:
                request_data.update({
                    "subject": {
                        "hostGroups": {
                        "includes": [source_group],
                        "excludes": []
                        },
                    }
                })
            if destination_port:
                if destination_port.startswith('!'):
                    request_data.update({
                        "peer": {
                            "tcpUdpPorts": {
                                "includes": [],
                                "excludes": [destination_port[1:]]
                            },
                        }
                    })
                else:   
                    request_data.update({
                        "peer": {
                            "tcpUdpPorts": {
                                "includes": [destination_port],
                                "excludes": []
                            },
                        }
                    })
            if destination_ip:
                if destination_ip.startswith('!'):
                    request_data.update({
                        "peer": {
                            "ipAddresses": {
                                "includes": [],
                                "excludes": [destination_ip[1:]]
                            },
                        }
                    })
                else:   
                    request_data.update({
                        "peer": {
                            "ipAddresses": {
                                "includes": [destination_ip],
                                "excludes": []
                            },
                        }
                    })                                               
            if destination_group:
                request_data.update({
                    "peer": {
                        "hostGroups": {
                        "includes": [destination_group],
                        "excludes": []
                        },
                    }
                })
            if application_id:
                request_data.update({
                    "flow": {
                        "applications": {
                        "includes": [application_id],
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
    
    def get_application_traffic(self):
        traffic_url = 'https://' + self.ip + '/sw-reporting/v1/tenants/' + self.tenant_id  + '/internalHosts/applications/traffic/hourly'
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

def flow_results(flow_results, tag_list, port_dict, flag_dict):
    results = {}
    now = datetime.datetime.now()

    if flow_results:
        for i in tag_list:
            for j in flow_results:
                if j['subject']['hostGroupIds'][0] == i.tagid:
                    j['subject']['hostGroupname'] = i.name
                if j['peer']['hostGroupIds'][0] == i.tagid:
                    j['peer']['hostGroupname'] = i.name
                
        final_list = []
        date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
        for i in flow_results:
            i['statistics']['firstActiveTime'] = datetime.datetime.strptime(i['statistics']['firstActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
            i['statistics']['firstActiveTime'] = i['statistics']['firstActiveTime'].strftime('%Y-%m-%d %H:%M:%S')
            i['statistics']['lastActiveTime'] = datetime.datetime.strptime(i['statistics']['lastActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
            i['statistics']['lastActiveTime'] = i['statistics']['lastActiveTime'].strftime('%Y-%m-%d %H:%M:%S')   
            i['subject']['hostGroupIds'] = i['subject']['hostGroupIds'][0]
            i['peer']['hostGroupIds'] = i['peer']['hostGroupIds'][0]

            if str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower() in port_dict:
                i['applicationName'] = port_dict.get(str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower())
            else:
                i['applicationName'] = 'Unassigned'
            if i['subject']['countryCode'] in flag_dict:
                i['subject']['flag'] = flag_dict.get(i['subject']['countryCode'])
            else:
                i['subject']['flag'] = ''

            # result 딕셔너리 생성
            result = {}
            result['subject_name'] = i['subject']['hostGroupname']
            result['protocol'] = i['peer']['portProtocol']['protocol']
            result['port'] = i['peer']['portProtocol']['port']
            result['application'] = i['applicationName']
            result['bps'] = i['statistics']['byteRate']
            result['rtt'] = i['statistics']['rttAverage']
            result['lastActiveTime'] = i['statistics']['lastActiveTime']
            result['source_ip'] = i['subject']['ipAddress']
            final_list.append(result)

        # final list 딕셔너리로 dataframe 생성
        df = pd.DataFrame(final_list)
        df['subject_count'] = df.groupby('subject_name')['subject_name'].transform('count')
        df['port_count'] = df.groupby(['protocol','port'])['protocol'].transform('count')
        
        subject_list = df.drop_duplicates(['subject_name'], keep='first').to_dict('records')
        port_df = df.drop_duplicates(['protocol', 'port'], keep='first')
        udp_list = port_df[port_df['protocol'] == 'UDP'].to_dict('records')
        tcp_list = port_df[port_df['protocol'] == 'TCP'].to_dict('records')

        # bps array 생성
        chart_df = df.set_index('lastActiveTime', drop=False)
        endtime = now - datetime.timedelta(minutes=5)
        end_timestamp = endtime.strftime('%Y-%m-%d %H:%M:%S')
        time_df = pd.DataFrame({'time_stamp':pd.date_range(end_timestamp, periods=300, freq='S'), 'time_range':[i for i in range(1, 301)]})
        time_df = time_df.set_index('time_stamp')
        result_df = pd.merge(chart_df, time_df, left_index=True, right_index=True, how="right")
        result_df = result_df.fillna(0)
        chart_results = result_df.to_dict('records')
        results = {'results': flow_results, 'subject_list': subject_list, 'udp_list': udp_list, 'tcp_list': tcp_list, 'chart_results': chart_results
        }
    return results