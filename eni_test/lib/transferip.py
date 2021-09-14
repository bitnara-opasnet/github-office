#!/usr/bin/env python

import argparse
import ipaddress

# netmask를 cidr로 변환: '255.255.252.0' --> 22
def netmasktocidr(subnetmask):
    cidr = ipaddress.ip_network('0.0.0.0/'+subnetmask).prefixlen
    return cidr

# cidr을 netmask로 변환: 25 --> '255.255.255.128'
def cidrtonetmask2(bit):
    net4 = ipaddress.ip_network('0.0.0.0/'+str(bit)).netmask
    return str(net4)

def transferip():
    parser = argparse.ArgumentParser()
    parser.add_argument('--netmask', metavar='netmask', type=str, help='netmask')
    parser.add_argument('--cidr', metavar='cidr', type=str, help='cidr')
    args = parser.parse_args()
    if args.netmask:
        netmask = args.netmask
        rst = netmasktocidr(netmask)
    else:
        cidr = args.cidr
        rst = cidrtonetmask2(cidr)
    print(rst)

if __name__ == '__main__':
    transferip()


