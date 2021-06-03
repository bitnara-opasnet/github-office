import json
import ipaddress
import random
import copy

#생성할 개수 지정 
create_count = 15
div_count = 10

with open('physical-topology-demo1.json', 'r') as json_file:
    json_data = json.load(json_file)

ori_node = json_data['nodes']

# ip 생성 
def get_ap_ip():
    ip_list = []
    for i in ori_node:
        if i.get('group_name') == 'AP':
            ip_list.append(i.get('ip'))
    ip_list.sort()
    last_ip = ip_list[-1]
    return last_ip

def get_hostip_list(ap_ip,cidr):
    l = []
    host4 = ipaddress.ip_interface(ap_ip + cidr)
    netaddr = host4.network
    for x in netaddr.hosts():
        if ipaddress.ip_address(x) > ipaddress.ip_address(ap_ip):
            l.append(str(x))
    return l

ap_ip = get_ap_ip() 
cidr = '/24'

#mac address 생성
def get_mac_addr():
    count = 4
    mac_sample = '7c:21:0d:9f:0a:24'
    str_pool = 'abcdefgqrstuvwxyz1234567890hijklmnop'
    res = ''
    for i in range(count):
        res += random.choice(str_pool)
    result = mac_sample[:-5] + res[:2] +':'+ res[2:]
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

#랜덤 id 생성을 위한 변수 저장
node_n = increase_num(9509)
id_sample = '30015a66-1fb6-452b-8504-f0990f8a9509'

#random ap list 생성
ip_list = get_hostip_list(ap_ip,cidr)
random_node = []
for i in ip_list:
    random_node.append([i, get_mac_addr(), id_sample[:-4] + str(next(node_n)), get_label()])

# sample로 사용할 node 하나만 선택
for i in ori_node:              
    if i.get('ip')==get_ap_ip():
        ori_node_one = i
ori_node_one = copy.deepcopy(ori_node_one)         

#final node 생성
final_nodes = json_data['nodes'][:]
def random_node_create(num): 
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

# node 생성
final_nodes = random_node_create(int('{}'.format(create_count)))

node_id_list = []
for i in json_data['nodes']:
    node_id_list.append(i.get('id'))

new_node_list = []
for i in final_nodes:
    if i.get('id') in node_id_list:
        pass
    else:
        new_node_list.append(i)

# random link 생성
link_n1 = increase_num(303)
link_n2 = increase_num(316)
id_sample1 = '252303'
id_sample2 = '252316'

def get_random_link(total_num,div_num):
    random_link = []
    for i in range(total_num):
        if i < div_num:
           random_link.append([new_node_list[i].get('id'), id_sample1[:-3] + str(next(link_n1))])
        else:
            random_link.append([new_node_list[i].get('id'), id_sample2[:-3] + str(next(link_n2))])
    return(random_link)
random_link = get_random_link(create_count, div_count)


for i in json_data['links']:
    if i.get('source') == '28975461-7826-4cac-b9f6-88aa9e5e3f3f':
        ori_link_one = i 
    elif i.get('source') == '30015a66-1fb6-452b-8504-f0990f8a9509':
        ori_link_two = i
ori_link_one = copy.deepcopy(ori_link_one)
ori_link_two = copy.deepcopy(ori_link_two)

#final link 생성
final_links = json_data['links'][:]
def random_link_create(total_num, div_num):
    for i in range(total_num):
        if i < div_num:
            ori_link_one.update({'id':random_link[i][1], 'source':random_link[i][0]})
            random_dic1 = dict(ori_link_one.items())
        else:
            ori_link_two.update({'id':random_link[i][1], 'source':random_link[i][0]})
            random_dic1 = dict(ori_link_two.items()) 
        final_links.append(random_dic1)    
    return(final_links)  

# link 생성 (개수 지정)
final_links = random_link_create(create_count, div_count)
# for i in final_links:
#     if i.get('startPortIpv4Mask'):
#         i.update({'startPortIpv4Mask':i.get('startPortIpv4Mask').replace(" ","")})

print(len(final_nodes), len(final_links))
final_ap_dict = dict({'links' : final_links, 'nodes' : final_nodes})

#json 파일로 내보내기
# with open('physical-topology-demo1_{}_{}.json'.format(div_count, div_count), 'w') as outfile:
#     json.dump(final_ap_dict, outfile, indent=4)

with open('physical-topology-demo1_5_10.json', 'w') as outfile:
    json.dump(final_ap_dict, outfile, indent=4)