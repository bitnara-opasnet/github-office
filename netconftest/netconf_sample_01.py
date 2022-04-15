import os
import sys
from ncclient import manager

cur_dir_path = os.path.dirname(os.path.realpath(__file__)) 

host = '100.124.0.1'
port = 830
username = 'opas'
password = 'Cisco!23'
hostkey_verify = False

hostname_filter = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                    </native>
                </filter>
                '''
def main():
    with manager.connect(host = host,
                        port = port,
                        username = username,
                        password = password,
                        hostkey_verify = hostkey_verify) as m:
                        netconf_reply = m.get_config(source='running', filter=hostname_filter).xml
                        
                        # netconf_reply = m.get(xml_content)
if __name__ == '__main__':
    sys.exit(main())