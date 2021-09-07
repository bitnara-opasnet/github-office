import ipaddress
import random

class GetRandomClient(object):
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

    def get_mac_addr(self):   
        count = 6
        mac_sample = '68:EC:C5:DD:04:D2'
        str_pool = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        res = ''
        for i in range(count):
            res += random.choice(str_pool)
        result = mac_sample[:8] +':'+ res[:2] +':'+ res[2:4] +':'+ res[4:]
        return result
        
    def increase_num(self, num):
        n=num
        while True:
            n+=1        
            yield n

    def random_data_create(self, ip, num, cidr, data, params): 
        ip_list = self.get_hostip_list(ip, cidr, num)
        n = self.increase_num(0)
        random_data = []
        for i in ip_list:
            random_mac = self.get_mac_addr()
            if random_mac in random_data:
                if params == 'wireless':
                    random_data.append([i, self.get_mac_addr(), 'wireless_user_'+str(next(n))])
                else:
                    random_data.append([i, self.get_mac_addr(), 'wired_user_'+str(next(n))])
            else:
                if params == 'wireless' : 
                    random_data.append([i, random_mac,'wireless_user_'+ str(next(n))])
                else:
                    random_data.append([i, random_mac,'wired_user_'+ str(next(n))])
        for i in data:              
            if i.get('framed_ip_address') == ip:
                sample_data_one = i.copy()
        final_data = []
        for i in range(num):
            sample_data_one.update({'framed_ip_address':random_data[i][0], 'calling_station_id':random_data[i][1], 'user_name':random_data[i][2]})
            random_dic1 = dict(sample_data_one.items())
            final_data.append(random_dic1)
        return(final_data)

    def device_devision(self, data, famliy_name, role_name):
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



