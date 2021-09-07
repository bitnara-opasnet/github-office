import ipaddress
import random
import copy

def get_ap_ip(data, family_name, role_name):
    ip_list = []
    for i in data:
        if i.get('family') == family_name and i.get('role') == role_name:
            ip_list.append(i.get('managementIpAddress'))
    ip_list.sort()
    last_ip = ip_list[-1]
    return last_ip

def get_hostip_list(ap_ip, cidr):
    l = []
    host4 = ipaddress.ip_interface(ap_ip + cidr)
    netaddr = host4.network
    for x in netaddr.hosts():
        if ipaddress.ip_address(x) > ipaddress.ip_address(ap_ip):
            l.append(str(x))
    return l

def get_mac_addr():
    count = 4
    mac_sample = '7c:21:0d:9f:0a:24'
    str_pool = 'abcdefgqrstuvwxyz1234567890hijklmnop'
    res = ''
    for i in range(count):
        res += random.choice(str_pool)
    result = mac_sample[:-5] + res[:2] +':'+ res[2:]
    return result

def get_id():
    count = 4
    id_sample = '30015a66-1fb6-452b-8504-f0990f8a9509'
    str_pool = 'abcdefgqrstuvwxyz1234567890hijklmnop'
    res = ''
    for i in range(count):
        res += random.choice(str_pool)
    result = id_sample[:-4] + res
    return result

def get_hostname(data): 
    count = 4
    str_pool = 'abcdefgqrstuvwxyz1234567890hijklmnop'
    if data[0].get('family') == 'Unified AP' and data[0].get('role') == 'ACCESS' :
        name_sample = 'AP04EB.409E.60C0'
    elif data[0].get('family') == 'Switches and Hubs' and data[0].get('role') == 'ACCESS' :
        name_sample = 'EdgeEB.409E.60C0'
    elif data[0].get('family') == 'Switches and Hubs' and data[0].get('role') == 'DISTRIBUTION' :
        name_sample = 'Border.409E.60C0'
    elif data[0].get('family') == 'Routers' and data[0].get('role') == 'BORDER ROUTER' :
        name_sample = 'Router.409E.60C0'
    res = ''
    for i in range(count):
        res += random.choice(str_pool)
    result = name_sample[:-4] + res
    return result


def device_devision(data, famliy_name, role_name):
    result_list = []
    for i in data.get('response'):
        if i.get('family') == famliy_name and i.get('role') == role_name:
            result_list.append(i)
    if result_list[0].get('family') == 'Unified AP' and result_list[0].get('role') == 'ACCESS' :
        return (result_list)
    elif result_list[0].get('family') == 'Switches and Hubs' and result_list[0].get('role') == 'ACCESS' :
        return (result_list)
    elif result_list[0].get('family') == 'Switches and Hubs' and result_list[0].get('role') =='DISTRIBUTION' :
        return (result_list)
    elif result_list[0].get('family') == 'Routers' and result_list[0].get('role') == 'BORDER ROUTER' :
        return (result_list)
    else:
        return('UNKNOWN')

def random_data_create(num, cidr, data, family_name, role_name): 
    ap_ip = get_ap_ip(data, family_name, role_name)
    ip_list = get_hostip_list(ap_ip, cidr)

    random_data = []
    for i in ip_list:
        random_data.append([i, get_mac_addr(), get_id(), get_hostname(data)])

    sample_data_one = copy.deepcopy(data[0])
    final_data = []
    for i in range(num):
        sample_data_one.update({'managementIpAddress':random_data[i][0], 'macAddress':random_data[i][1], 
                              'id':random_data[i][2], 'hostname': random_data[i][3]})
        random_dic1 = dict(sample_data_one.items())
        final_data.append(random_dic1)
    return(final_data)