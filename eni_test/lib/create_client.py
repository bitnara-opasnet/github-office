from lib.get_api import getApi
from lib.get_random import GetRandomClient
import xmltodict
import json
import re
import datetime
from pytz import timezone
import random

getapi = getApi()
randomClient = GetRandomClient()

class CreateClient(object):
    # active list 생성
    def create_active(self, wireless_num, wired_num, url, params):
        active_data = getapi.get_xml_data(url)
        active_data = json.loads(json.dumps(xmltodict.parse(active_data, process_namespaces=True)))
        active_Session = active_data.get('activeList').get('activeSession')
        wireless_client = randomClient.random_data_create('100.100.10.102', wireless_num, '/16', active_Session, 'wireless')
        wired_client = randomClient.random_data_create('100.100.20.101', wired_num, '/16', active_Session, 'wired')

        final_list = []
        for i in active_Session:
            final_list.append(i)
        for i in wireless_client:
            final_list.append(i)
        for i in wired_client:
            final_list.append(i)
        active_dict = {'activeList':{"@noOfActiveSession": len(final_list), 'activeSession':final_list}}

        if params == 'dict': 
            return(active_dict)
        elif params == 'xml':
            active_xml = xmltodict.unparse(active_dict, pretty=True, full_document=False)
            active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml
            return(active_xml)  

    def get_device_sample(self, params):
        is_token = getapi.get_auth_token()['Token']
        device_data = getapi.get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')
        if params == 'wireless':
            device_sample = randomClient.device_devision(device_data, 'Unified AP', 'ACCESS')
        elif params == 'wired':
            device_sample = randomClient.device_devision(device_data, 'Switches and Hubs', 'ACCESS')
        return(device_sample)

    def get_macaddr(self, wireless_device_data, wired_device_data, active_data, wireless_client, wired_client, mac_addr):
        # DB에 저장된 active list 중에서 입력된 mac address가 같은 데이터 찾기
        for i in active_data: 
            if i.get('calling_station_id') == mac_addr:
                active_selected_data = i

        # wireless client 생성
        if active_selected_data.get('user_name').split('_')[0] == 'wireless':
            client_data = json.loads(json.dumps(xmltodict.parse(wireless_client, process_namespaces=True)))
            client_sample_data = client_data.get('sessionParameters').copy() # 사용할 sample data
            attr_string = client_data.get('sessionParameters').get('other_attr_string') 
            # sample의 user_name을 생성할 데이터의 username으로 교체
            attr_string = re.sub(client_data.get('sessionParameters').get('user_name'), active_selected_data.get('user_name'), attr_string)

            # :로 분리 후 called station id 위치 찾기 
            attr_split = attr_string.split(':')
            if 'Called-Station-ID=7c-21-0d-9f-0a-20' in attr_split: 
                split_index = attr_split.index('Called-Station-ID=7c-21-0d-9f-0a-20')
            else:
                split_index = attr_split.index('Called-Station-ID=0c-75-bd-b7-9e-c0')

            # AP 두개에 나눠서 client 설정
            if int(active_selected_data.get('user_name').split('_')[2])%2 == 0:
                attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wireless_device_data[0].get('macAddress').replace(':','-'))
            else:
                attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wireless_device_data[1].get('macAddress').replace(':','-'))    
            attr_string = ':'.join(attr_split)

            # 현재시간으로 time 설정
            cur_time = timezone('Asia/Seoul').localize(datetime.datetime.now())
            cur_time = cur_time.isoformat()[:-9] + cur_time.isoformat()[-6:]

            # 변경된 client 정보 입력 
            client_sample_data.update({'user_name': active_selected_data.get('user_name'),
                                    'framed_ip_address': active_selected_data.get('framed_ip_address'),
                                    'calling_station_id': active_selected_data.get('calling_station_id'),
                                    'orig_calling_station_id': active_selected_data.get('calling_station_id').replace(':','-').lower(),
                                    'cts_security_group': 'GR'+str(random.randint(1, 5)),
                                    'other_attr_string': attr_string, 'acct_acs_timestamp':cur_time,'acct_acsview_timestamp': cur_time})

            # namespace 변경                        
            column_list = ['passed', 'failed', 'started', 'stopped']
            for i in column_list:
                client_sample_data.get(i)['@xsi:type'] = client_sample_data.get(i).pop('@http://www.w3.org/2001/XMLSchema-instance:type')
            final_dic = dict({'sessionParameters': client_sample_data})
            client_xml = xmltodict.unparse(final_dic, full_document=False)
            client_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + client_xml

        # wired client 생성    
        elif active_selected_data.get('user_name').split('_')[0] == 'wired':
            client_data = json.dumps(xmltodict.parse(wired_client, process_namespaces=True))
            client_data = json.loads(client_data)
            client_sample_data = client_data.get('sessionParameters').copy()
            attr_string = client_data.get('sessionParameters').get('other_attr_string')
            attr_string = re.sub(client_data.get('sessionParameters').get('user_name') , active_selected_data.get('user_name'), attr_string)

            # wired client 정보가 제대로 호출될 경우
            if attr_string.find(':!:') != -1:
                attr_split = attr_string.split(':!:')
                split_index = attr_split.index('Called-Station-ID=DC:F7:19:00:63:02')
                if int(active_selected_data.get('user_name').split('_')[2])%2 == 0:
                    attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wired_device_data[0].get('macAddress'))
                else:
                    attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wired_device_data[1].get('macAddress'))
                attr_string = ':!:'.join(attr_split)

            #wired client 정보가 제대로 호출되지 않을 경우 콤마로 구분기호 변경
            else:
                attr_split = attr_string.split(',')
                split_index = attr_split.index('Called-Station-ID=DC:F7:19:00:63:02')
                if int(active_selected_data.get('user_name').split('_')[2])%2 == 0:
                    attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wired_device_data[0].get('macAddress'))
                else:
                    attr_split[split_index] = attr_split[split_index].replace(attr_split[split_index].split('=')[1], wired_device_data[1].get('macAddress'))
                attr_string = ','.join(attr_split)
            
            # 현재시간으로 time 설정
            cur_time = timezone('Asia/Seoul').localize(datetime.datetime.now())
            cur_time = cur_time.isoformat()[:-9] + cur_time.isoformat()[-6:]

            # 변경된 client 정보 입력 
            client_sample_data.update({'user_name': active_selected_data.get('user_name'),
                                    'framed_ip_address': active_selected_data.get('framed_ip_address'),
                                    'calling_station_id': active_selected_data.get('calling_station_id'),
                                    'orig_calling_station_id':active_selected_data.get('calling_station_id').replace(':','-'),
                                    'cts_security_group': 'GR'+str(random.randint(1, 5)),
                                    'other_attr_string': attr_string, 'acct_acs_timestamp':cur_time,'acct_acsview_timestamp': cur_time})

            # client 정보가 제대로 호출되지 않을 경우 예외처리
            if 'passed' in list(client_sample_data.keys()):
                column_list = ['passed', 'failed', 'started', 'stopped']
            else:
                column_list = ['started', 'stopped']
            for i in column_list:
                client_sample_data.get(i)['@xsi:type'] = client_sample_data.get(i).pop('@http://www.w3.org/2001/XMLSchema-instance:type')
            final_dic = dict({'sessionParameters':client_sample_data})
            client_xml = xmltodict.unparse(final_dic, full_document=False)
            client_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + client_xml

        # 기존 데이터 호출
        else:
            client_xml = getapi.get_xml_data('https://100.64.0.100/admin/API/mnt/Session/MACAddress/{}'.format(mac_addr))
        return(client_xml)