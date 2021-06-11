import ipaddress
import random

def get_ip(data):
    ip_list = []
    for i in data:
        if i.get('framed_ip_address') != None:
            ip_list.append(i.get('framed_ip_address'))      
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
    mac_sample = '68:EC:C5:DD:04:D2'
    str_pool = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    res = ''
    for i in range(count):
        res += random.choice(str_pool)
    result = mac_sample[:-5] + res[:2] +':'+ res[2:]
    return result
    
def increase_num(num):
    n=num
    while True:
        n+=1        
        yield n

def random_data_create(num, cidr, data): 
    ap_ip = get_ip(data)
    ip_list = get_hostip_list(ap_ip, cidr)
    n = increase_num(0)
    random_data = []
    for i in ip_list:
        random_data.append([i, get_mac_addr(), 'test_user'+str(next(n))])
    for i in data:              
        if i.get('framed_ip_address')== get_ip(data):
            sample_data_one = i.copy()
    final_data = []
    for i in range(num):
        sample_data_one.update({'framed_ip_address':random_data[i][0], 'calling_station_id':random_data[i][1], 
                              'user_name':random_data[i][2]})
        random_dic1 = dict(sample_data_one.items())
        final_data.append(random_dic1)
    return(final_data)