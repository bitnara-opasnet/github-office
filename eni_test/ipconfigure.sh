#!/bin/bash

# enp0s3
ifnames=`ifconfig | awk '/^[e]/ {print $1}'`
echo "interface name : ${ifnames}"
echo "would you like to change dhcp to static? (y/n) : "
read ans

# if [ ${ans} = "y" ] || [ ${ans} = "Y" ]
if [ ${ans} = "y" -o ${ans} = "Y" ]
then
    echo "ip address :"
    read ipaddress
    echo "netmask :"
    read netmask
    echo "gateway :"
    read gateway
    echo "DNS :"
    read dns
    interface="auto ${ifnames}\n iface ${ifnames} inet static\n address ${ipaddress}\n netmask ${netmask}\n gateway ${gateway}\n dns-nameservers ${dns}\n"
    # dhcp=`cat /etc/network/interfaces | sed -n '11,12p'`
elif [ ${ans} = "n" -o ${ans} = "N" ]
then
    echo "exit"
    exit 0
else
    echo "Invalid input. Press y or n"
fi
exit 0