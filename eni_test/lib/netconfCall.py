from ncclient import manager
import xmltodict
import json
import os

cur_dir_path = os.path.dirname(os.path.realpath(__file__)) 
# print(cur_dir_path)

class NetconfCall(object):
    def __init__(self):
        self.host = '100.127.100.20'
        self.port = 830
        self.username = 'opas'
        self.password = 'Cisco!23'
        self.hostkey_verify = False

    def openxml(self, filename):
        file_path = os.path.join(cur_dir_path, filename)
        # print(file_path)
        with open(file_path, 'r') as f:
            res = f.read()
        return res

    def get_reply(self, xmlf):
        xml_content = self.openxml(xmlf)
        # print(xml_content)
        with manager.connect(
                            host = self.host,
                            port = self.port,
                            username = self.username,
                            password = self.password,
                            hostkey_verify = self.hostkey_verify
                        ) as m:
                            netconf_reply = m.get_config(source='running', filter=('subtree', xml_content)).xml
                            # netconf_reply = m.get(xml_content)
        return netconf_reply

    def get_selected(self, data, selected):
        interface_list = []
        for i in data:
            selected_dict = {}
            for j in selected:
                selected_dict.update({j:i.get(j)})
            interface_list.append(selected_dict)
        return interface_list

ncfCall = NetconfCall()
# print(ncfCall.openxml('Cisco-IOS-XE-wireless-client-oper.xml'))
# 'Cisco-IOS-XE-wireless-access-point-oper.xml'
netconf_iface = ncfCall.get_reply('Cisco-IOS-XE-wireless-client-oper.xml')
print(netconf_iface)
# netconf_data = xmltodict.parse(netconf_iface.xml)["rpc-reply"]["data"]
# print(netconf_data)

# # Create a list of interfaces
# interfaces = netconf_data["interfaces"]['interface']

# interface = json.dumps(interfaces)
# interface = json.loads(interface)

# selected = ['name', 'ipv4', 'type']
# interface_list = netconf_reply.get_selected(interface, selected)

# netconf manual
# https://yuma123.org/wiki/index.php/Yuma_netconfd_Manual#.3Cget-config.3E 

# xml_content = openxml('ietf-interface.xml') + openxml('Cisco-IOS-XE-wireless-ap-cfg.xml')
# xml_content = openxml('ietf-interface.xml')
# ietf_interface = json.dumps(xmltodict.parse(xml_content))
# ietf_interface = json.loads(ietf_interface)

# xml_content = openxml('Cisco-IOS-XE-wireless-ap-cfg.xml')
# wireless_ap_cfg = json.dumps(xmltodict.parse(xml_content))
# wireless_ap_cfg = json.loads(wireless_ap_cfg)
# wireless_ap_cfg.update(ietf_interface)
# xml_content = xmltodict.unparse(wireless_ap_cfg, full_document=False)

# netconf_filter = """<nc:rpc xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:618101d4-1ea4-43d0-963c-485cec6cf6de">
#    <nc:get-config> 
#       <nc:filter type="subtree"> 
#          <if:interfaces xmlns:if="urn:ietf:params:xml:ns:yang:ietf-interfaces"> 
#             <if:interface> 
#             </if:interface> 
#          </if:interfaces> 
#       </nc:filter> 
#    </nc:get-config> 
# </nc:rpc>
# """