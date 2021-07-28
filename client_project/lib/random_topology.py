import json
import ipaddress
import random
import copy

def get_hostname(data):
    if data.get('family') == 'Unified AP' and data.get('role') == 'ACCESS' :
        result = 'AP'
    elif data.get('family') == 'Switches and Hubs' and data.get('role') == 'ACCESS' :
        result = 'Edge'
    elif data.get('family') == 'Switches and Hubs' and data.get('role') == 'DISTRIBUTION' :
        result = 'Border'
    elif data.get('family') == 'Switches and Hubs' and data.get('role') == 'CORE' :
        result = 'Border'
    elif data.get('family') == 'Switches and Hubs' and data.get('role') == 'BORDER ROUTER' :
        result = 'Border'
    elif data.get('family') == 'Routers' and data.get('role') == 'BORDER ROUTER' :
        result = 'Router'
    elif data.get('family') == 'Wireless Controller' and data.get('role') == 'ACCESS':
        result = 'WLC'
    else:
        result = 'UNKNOWN'
    return result

# ip 생성 
def get_last_ip(node_data, group_name):
    ip_list = []
    for i in node_data:
        if i.get('group_name') == group_name:
            ip_list.append(i.get('ip'))
    ip_list.sort()
    last_ip = ip_list[-1]
    return last_ip

def get_hostip_list(ap_ip, cidr, num):
    l = []
    host4 = ipaddress.ip_interface(ap_ip + cidr)
    netaddr = host4.network
    for x in netaddr.hosts():
        if ipaddress.ip_address(x) > ipaddress.ip_address(ap_ip):
            l.append(str(x))
            if len(l) >= num:
                break
    return l

#mac address 생성
def get_mac_addr():
    count = 4
    mac_sample = '7c:21:0d:9f:0a:24'
    str_pool = 'abcdefgqrstuvwxyz1234567890hijklmnop'
    res = ''
    for i in range(count):
        res += random.choice(str_pool)
    result = mac_sample[:8] +':'+ res[:2] +':'+ res[2:4] +':'+ res[4:]
    return result

#label 생성
def get_label():
    count = 4
    label_sample = 'AP6C41.0EC5.9954'
    str_pool = '0123456789'
    res = ''
    for i in range(count):
        res += random.choice(str_pool)
    result = label_sample[:-4] + res
    return result

#제너레이터 함수 
def increase_num(num):
    n=num
    while True:
        n+=1        
        yield n

def random_node_create(node_data, group_name, cidr, node_num, num): 
    final_nodes = []
    last_ip = get_last_ip(node_data, group_name)
    node_n = increase_num(node_num)
    id_sample = '30015a66-1fb6-452b-8504-f0990f8a9509'

    for i in node_data:              
        if i.get('ip')== last_ip:
            ori_node_one = i
    ori_node_one = copy.deepcopy(ori_node_one) 

    ip_list = get_hostip_list(last_ip, cidr, 100)
    random_node = []
    for i in ip_list:
        random_node.append([i, get_mac_addr(), id_sample[:-4] + str(next(node_n)), get_label()])

    for i in range(num):
        ori_node_one.update({'ip':random_node[i][0], 
                             'id':random_node[i][2],
                             'label':random_node[i][3]})
        ori_node_one.get('additionalInfo').update({'macAddress':random_node[i][1]})
        random_dic1 = dict(ori_node_one.items())
        random_dic2 = {'additionalInfo' : dict(ori_node_one['additionalInfo'])}
        random_dic1.update(random_dic2)
        final_nodes.append(random_dic1)
    return(final_nodes)

def new_node_list(node_data, final_nodes):
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

def random_edge_link(new_node_data, total_num, div_num):
    new_node_list = new_node_data
    link_n1 = increase_num(302)
    link_n2 = increase_num(314)
    id_sample1 = '352302'
    id_sample2 = '352314'
    random_link = []
    for i in range(total_num):
        if i < div_num:
            random_link.append([new_node_list[i].get('id'), id_sample1[:-3] + str(next(link_n1))])
        else:
            random_link.append([new_node_list[i].get('id'), id_sample2[:-3] + str(next(link_n2))])
    return random_link

def edge_link_create(new_node_data, link_data, total_num, div_num):
    for i in link_data:
        if i.get('endPortIpv4Address') == '100.124.128.6':
            ori_link_one = i 
        elif i.get('endPortIpv4Address') == '100.124.128.168':
            ori_link_two = i
    ori_link_one = copy.deepcopy(ori_link_one)
    ori_link_two = copy.deepcopy(ori_link_two)

    final_links = []
    random_link = random_edge_link(new_node_data, total_num, div_num)
    for i in range(total_num):
        if i < div_num:
            ori_link_one.update({'id':random_link[i][1], 'target':random_link[i][0]})
            random_dic1 = dict(ori_link_one.items())
        else:
            ori_link_two.update({'id':random_link[i][1], 'target':random_link[i][0]})
            random_dic1 = dict(ori_link_two.items()) 
        final_links.append(random_dic1)    
    return(final_links) 

def random_ap_link(new_node_data, total_num, div_num1, div_num2, div_num3):
    new_node_list = new_node_data
    link_n1 = increase_num(100000)
    link_n2 = increase_num(200000)
    link_n3 = increase_num(300000)
    link_n4 = increase_num(400000)
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

def ap_link_create(new_node_data, link_data, Edge_node, total_num, div_num1, div_num2, div_num3):
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
        if i.get('id') == '30015a66-1fb6-452b-8504-f0990f8a1001' :
            new_edge.append(i)
        elif i.get('id') == '30015a66-1fb6-452b-8504-f0990f8a1002' :
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
    random_link = random_ap_link(new_node_data, total_num, div_num1, div_num2, div_num3)
    final_links = []
    for i in range(total_num):
        if i < div_num1:
            ori_link_one.update({'id':random_link[i][1], 'source':random_link[i][0]})
            random_dic1 = dict(ori_link_one.items())
        elif div_num1 <= i < div_num2:
            ori_link_two.update({'id':random_link[i][1], 'source':random_link[i][0]})
            random_dic1 = dict(ori_link_two.items()) 
        elif div_num2 <= i < div_num3:
            ori_link_three.update({'id':random_link[i][1], 'source':random_link[i][0]})
            random_dic1 = dict(ori_link_three.items()) 
        else:
            ori_link_four.update({'id':random_link[i][1], 'source':random_link[i][0]})
            random_dic1 = dict(ori_link_four.items())    
        final_links.append(random_dic1) 
    return(final_links) 

def get_topology_data():
    with open('physical-topology-demo1.json', 'r') as json_file:
        json_data = json.load(json_file)

    ori_node = json_data['nodes']
    final_nodes = json_data['nodes'][:]
    final_links = json_data['links'][:]

    Edge_node = random_node_create(ori_node, 'Edge', '/24', 1000, 15)
    Edge_links = edge_link_create(Edge_node, final_links, 15, 10)
    for i in Edge_links:
        final_links.append(i)

    AP_node = random_node_create(ori_node, 'AP', '/24', 9509, 30)
    for i in AP_node:
        final_nodes.append(i)

    ap_node_list = new_node_list(ori_node, final_nodes)
    ap_links = ap_link_create(ap_node_list, final_links, Edge_node, 30, 5, 10, 20)

    for i in Edge_node:
        final_nodes.append(i)
    for i in ap_links:
        final_links.append(i)

    final_dict = dict({'links' : final_links, 'nodes' : final_nodes})
    # with open('physical-topology-demo1_15_30.json', 'w') as outfile:
    #     json.dump(final_dict, outfile, indent=4)

    return final_dict