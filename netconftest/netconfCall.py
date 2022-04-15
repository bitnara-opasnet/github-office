from ncclient import manager
import xmltodict
import json
import os
import re

cur_dir_path = os.path.dirname(os.path.realpath(__file__)) 
# print(cur_dir_path)

class NetconfCall(object):
    def __init__(self):
        # self.host = '100.127.100.20' #WLC
        self.host = '100.124.0.1' #Border
        self.port = 830
        self.username = 'opas'
        self.password = 'Cisco!23'
        self.hostkey_verify = False

    def openxml(self,  file_name, xml_path='',):
        if xml_path:
            file_path = xml_path + '/' + file_name
        else:
            file_path = file_name
        # print(file_path)
        with open(file_path, 'r') as f:
            res = f.read()
        return res

    def get_reply(self, xmlpath, xmlfile):
        xml_content = self.openxml(xml_path=xmlpath, file_name=xmlfile)
        # print(xml_content)
        with manager.connect(
                            host = self.host,
                            port = self.port,
                            username = self.username,
                            password = self.password,
                            hostkey_verify = self.hostkey_verify
                        ) as m:
                            netconf_reply = m.get_config(source='running', filter=('subtree', xml_content)).xml

        return netconf_reply


ncfCall = NetconfCall()
result = ncfCall.get_reply(xmlpath='/home/bitnara/netconftest/xmldata/standard', xmlfile='ietf-interfaces.xml')
print(result)