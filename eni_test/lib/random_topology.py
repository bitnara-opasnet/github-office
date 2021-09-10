import json
import ipaddress
import random
import copy
from lib.get_api import getApi

getapi = getApi()

class GetTopology(object):
    def get_hostname(self, data):
        if data.get('family') == 'Unified AP' and data.get('role') == 'ACCESS':
            data['group_name'] = 'AP'
            data['group'] = '4'
        elif data.get('family') == 'Switches and Hubs' and data.get('role') == 'ACCESS':
            data['group_name'] = 'Edge'
            data['group'] = '3'
        elif data.get('family') == 'Switches and Hubs' and data.get('role') == 'DISTRIBUTION':
            data['group_name'] = 'Border'
            data['group'] = '2'
        elif data.get('family') == 'Switches and Hubs' and data.get('role') == 'CORE':
            data['group_name'] = 'Border'
            data['group'] = '2'
        elif data.get('family') == 'Switches and Hubs' and data.get('role') == 'BORDER ROUTER':
            data['group_name'] = 'Border'
            data['group'] = '2'
        elif data.get('family') == 'Routers' and data.get('role') == 'BORDER ROUTER':
            data['group_name'] = 'Fusion'
            data['group'] = '1'
        elif data.get('family') == 'Wireless Controller' and data.get('role') == 'ACCESS':
            data['group_name'] = 'WLC'
            data['group'] = '5'
        elif data.get('family') == 'cloud node' and data.get('role') == 'cloud node':
            data['group_name'] = 'Internet'
            data['group'] = '0'
        else:
            data['group_name'] = 'UNKNOWN'
            data['group'] = '0'

    # ip 생성 
    def get_last_ip(self, node_data, group_name):
        ip_list = []
        for i in node_data:
            if i.get('group_name') == group_name:
                ip_list.append(i.get('ip'))
        ip_list.sort()
        last_ip = ip_list[-1]
        return last_ip

    def get_hostip_list(self, ap_ip, cidr, num):
        l = []
        host4 = ipaddress.ip_interface(ap_ip + cidr)
        netaddr = host4.network
        for x in netaddr.hosts():
            if ipaddress.ip_address(x) > ipaddress.ip_address(ap_ip):
                l.append(str(x))
                if len(l) >= num:
                    break
        return l

    # mac address 생성
    def get_mac_addr(self):
        count = 6
        mac_sample = '7c:21:0d:9f:0a:24'
        str_pool = 'abcdefgqrstuvwxyz1234567890hijklmnop'
        res = ''
        for i in range(count):
            res += random.choice(str_pool)
        result = mac_sample[:8] +':'+ res[:2] +':'+ res[2:4] +':'+ res[4:]
        return result

    # label 생성
    def get_label(self):
        count = 4
        label_sample = 'AP6C41.0EC5.9954'
        str_pool = '0123456789'
        res = ''
        for i in range(count):
            res += random.choice(str_pool)
        result = label_sample[:-4] + res
        return result

    # 제너레이터 함수 
    def increase_num(self, num):
        n=num
        while True:
            n+=1        
            yield n

    # 새로운 node 생성
    def random_node_create(self, node_data, group_name, cidr, node_num, num, client_num): 
        # 새로운 node 정보 생성 (ip, mac address, id, label)
        last_ip = self.get_last_ip(node_data, group_name)
        node_n = self.increase_num(node_num)
        id_sample = '30015a66-1fb6-452b-8504-f0990f8a9509'
        ip_list = self.get_hostip_list(last_ip, cidr, 100)

        random_node = []
        for i in ip_list:
            random_node.append([i, self.get_mac_addr(), id_sample[:-4] + str(next(node_n)), self.get_label()])

        # sample로 사용할 node 선택
        for i in node_data:              
            if i.get('ip')== last_ip:
                ori_node_one = i
        ori_node_one = copy.deepcopy(ori_node_one) 

        # 변경된 node 정보 입력 
        final_nodes = []
        for i in range(num):
            ori_node_one.update({'ip':random_node[i][0], 
                                'id':random_node[i][2],
                                #  'clientcount': client_num,
                                'label':random_node[i][3]})
            ori_node_one.get('additionalInfo').update({'macAddress': random_node[i][1]})
            random_dic1 = dict(ori_node_one.items())
            random_dic2 = {'additionalInfo': dict(ori_node_one['additionalInfo'])}
            random_dic1.update(random_dic2)
            final_nodes.append(random_dic1)
        return(final_nodes)

    # 
    def new_node_list(self, node_data, final_nodes):
        node_id_list = []
        for i in node_data:
            node_id_list.append(i.get('id'))

        new_node_list = []
        for i in final_nodes:
            if i.get('id') in node_id_list:
                pass
            else:
                new_node_list.append(i)
        return new_node_list 

    # 새로운 edge link 정보 생성
    def random_edge_link(self, new_node_data, total_num, div_num):
        new_node_list = new_node_data
        link_n1 = self.increase_num(302)
        link_n2 = self.increase_num(314)
        id_sample1 = '352302'
        id_sample2 = '352314'
        random_link = []
        for i in range(total_num):
            if i < div_num:
                random_link.append([new_node_list[i].get('id'), id_sample1[:-3] + str(next(link_n1))])
            else:
                random_link.append([new_node_list[i].get('id'), id_sample2[:-3] + str(next(link_n2))])
        return random_link

    # edge link 정보 사용, edge link 생성
    def edge_link_create(self, new_node_data, link_data, total_num, div_num):
        for i in link_data:
            if i.get('endPortIpv4Address') == '100.124.128.6':
                ori_link_one = i 
            elif i.get('endPortIpv4Address') == '100.124.128.168':
                ori_link_two = i
        ori_link_one = copy.deepcopy(ori_link_one)
        ori_link_two = copy.deepcopy(ori_link_two)

        final_links = []
        random_link = self.random_edge_link(new_node_data, total_num, div_num)
        for i in range(total_num):
            if i < div_num:
                ori_link_one.update({'id': random_link[i][1], 'target': random_link[i][0]})
                random_dic1 = dict(ori_link_one.items())
            else:
                ori_link_two.update({'id': random_link[i][1], 'target': random_link[i][0]})
                random_dic1 = dict(ori_link_two.items()) 
            final_links.append(random_dic1)
        return(final_links) 

    def random_ap_link(self, new_node_data, total_num, div_num1, div_num2, div_num3):
        new_node_list = new_node_data
        link_n1 = self.increase_num(100000)
        link_n2 = self.increase_num(200000)
        link_n3 = self.increase_num(300000)
        link_n4 = self.increase_num(400000)
        random_link = []
        for i in range(total_num):
            if i < div_num1:
                random_link.append([new_node_list[i].get('id'), str(next(link_n1))])
            elif div_num1 <= i < div_num2:
                random_link.append([new_node_list[i].get('id'), str(next(link_n2))])
            elif div_num2 <= i < div_num3:
                random_link.append([new_node_list[i].get('id'), str(next(link_n3))])
            else:
                random_link.append([new_node_list[i].get('id'), str(next(link_n4))])
        return random_link

    def ap_link_create(self, new_node_data, link_data, Edge_node, total_num, div_num1, div_num2, div_num3):
        for i in link_data:
            if i.get('source') == '28975461-7826-4cac-b9f6-88aa9e5e3f3f':
                ori_link_one = i 
            elif i.get('source') == '30015a66-1fb6-452b-8504-f0990f8a9509':
                ori_link_two = i
        ori_link_one = copy.deepcopy(ori_link_one)
        ori_link_two = copy.deepcopy(ori_link_two)
        ori_link_three = copy.deepcopy(ori_link_one)
        ori_link_four = copy.deepcopy(ori_link_two)
        new_edge = []
        for i in Edge_node:
            if i.get('id') == '30015a66-1fb6-452b-8504-f0990f8a1001':
                new_edge.append(i)
            elif i.get('id') == '30015a66-1fb6-452b-8504-f0990f8a1002':
                new_edge.append(i)
        new_links = []
        ori_link_three.update({'target': new_edge[0].get('id'), 'id': '300000'})
        random_dic1 = dict(ori_link_three.items())
        new_links.append(random_dic1) 
        ori_link_four.update({'target': new_edge[1].get('id'), 'id': '400000'})
        random_dic1 = dict(ori_link_four.items())
        new_links.append(random_dic1) 
        ori_link_three = copy.deepcopy(new_links[0])
        ori_link_four = copy.deepcopy(new_links[1])
        random_link = self.random_ap_link(new_node_data, total_num, div_num1, div_num2, div_num3)
        final_links = []
        for i in range(total_num):
            if i < div_num1:
                ori_link_one.update({'id': random_link[i][1], 'source': random_link[i][0]})
                random_dic1 = dict(ori_link_one.items())
            elif div_num1 <= i < div_num2:
                ori_link_two.update({'id': random_link[i][1], 'source': random_link[i][0]})
                random_dic1 = dict(ori_link_two.items()) 
            elif div_num2 <= i < div_num3:
                ori_link_three.update({'id': random_link[i][1], 'source': random_link[i][0]})
                random_dic1 = dict(ori_link_three.items()) 
            else:
                ori_link_four.update({'id': random_link[i][1], 'source': random_link[i][0]})
                random_dic1 = dict(ori_link_four.items())    
            final_links.append(random_dic1) 
        return(final_links) 

    # json 데이터 활용한 topology 생성
    def get_topology_data(self):
        ap_num=7
        edge_num=4
        with open('physical-topology-demo1.json', 'r') as json_file:
            json_data = json.load(json_file)

        ori_node = json_data['nodes']
        final_nodes = json_data['nodes'][:]
        final_links = json_data['links'][:]

        Edge_node = self.random_node_create(ori_node, 'Edge', '/24', 1000, edge_num, 2)
        Edge_links = self.edge_link_create(Edge_node, final_links, edge_num, 2)
        for i in Edge_links:
            final_links.append(i)

        AP_node = self.random_node_create(ori_node, 'AP', '/24', 9509, ap_num, 10)
        for i in AP_node:
            final_nodes.append(i)

        ap_node_list = self.new_node_list(ori_node, final_nodes)
        ap_links = self.ap_link_create(ap_node_list, final_links, Edge_node, ap_num, 5, 10, 20)

        for i in Edge_node:
            final_nodes.append(i)
        for i in ap_links:
            final_links.append(i)

        final_dict = dict({'links': final_links, 'nodes': final_nodes})
        with open('physical-topology-demo1_{0}_{1}.json'.format(edge_num, ap_num), 'w') as outfile:
            json.dump(final_dict, outfile, indent=4)
        return final_dict


    def get_random_link(self, new_node_data, div_num):
        new_node_list = new_node_data
        link_n1 = self.increase_num(100000)
        link_n2 = self.increase_num(200000)
        random_link = []
        for i in range(len(new_node_data)):
            if i < div_num:
                random_link.append([new_node_list[i].get('id'), str(next(link_n1))])
            else:
                random_link.append([new_node_list[i].get('id'), str(next(link_n2))])
        return random_link

    def get_ap_link(self, new_node_data, link_list):
        ap_links = self.get_random_link(new_node_data, 1)
        for i in link_list:
            if i.get('source') == '28975461-7826-4cac-b9f6-88aa9e5e3f3f':
                ori_link_one = i 
        ori_link_one = copy.deepcopy(ori_link_one)
        new_links = []
        for i in range(len(ap_links)):
            ori_link_one.update({'id': ap_links[i][1], 'source': ap_links[i][0]})
            random_dic1 = dict(ori_link_one.items()) 
            new_links.append(random_dic1) 
        return new_links

    # dna에서 불러온 data 활용 topology 생성
    def get_random_topology3(self, params, ap_num, edge_num, client_count, rechable, unrechable_num=0):
        is_token = getapi.get_auth_token()['Token']
        json_data = getapi.get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/topology/physical-topology')
        topology_data = json_data['response']
        for i in topology_data['nodes']:
            self.get_hostname(i)
            i['reachabilityStatus'] = 'reachable'
            i['clientcount'] = client_count

        ori_node = topology_data['nodes']
        final_nodes = topology_data['nodes'][:]
        final_links = topology_data['links'][:]
        
        if ap_num >= 1: 
            AP_node = self.random_node_create(ori_node, 'AP', '/24', 9509, ap_num, client_count)
            for i in AP_node:
                final_nodes.append(i)
            ap_node_list = self.new_node_list(ori_node, final_nodes)
            new_links = self.get_ap_link(ap_node_list, final_links)
            for i in new_links:
                final_links.append(i)
        else: 
            pass
        
        if edge_num >=1:
            Edge_node = self.random_node_create(ori_node, 'Edge', '/24', 1000, edge_num, client_count)
            Edge_links = self.edge_link_create(Edge_node, final_links, edge_num, 1)
            for i in Edge_links:
                final_links.append(i) 
            for i in Edge_node:
                final_nodes.append(i)
        else:
            pass

        if rechable == 'N':
            for i in range(unrechable_num):
                final_links[i].update({'linkStatus': '1up'})
                final_nodes[i].update({'reachabilityStatus': '1reachable'})
        else:
            pass
        final_dict = dict({'response': {'links': final_links, 'nodes': final_nodes}, 'version': '1.0'})

        if params == 'N':
            return json_data
        else:
            return final_dict 