#!/bin/bash
PATH="/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin";
CWD=`pwd`
# cp /etc/network/interfaces ${CWD}/
# cp /etc/network/interfaces /etc/network/backup

# ifnames=`ifconfig | awk '/^[e]/ {print $1}'`
# echo "interface name : ${ifnames}"

# ip 선택
ifnames=`ifconfig -a | awk '/^[a-z]/ {print $1}'`
echo "select IP you want to change."
select ifname in $ifnames
do
    echo "interface name : ${ifname}"
    break
done

# interface 상태 변경 여부 선택
while true; do
echo "would you like to change ${ifname} interface? (y/n) : "
read ans
if [ ${ans} = "y" -o ${ans} = "Y" ]
then
    break
elif [ ${ans} = "n" -o ${ans} = "N" ]
then
    echo "exit"
    exit 0
else
    echo "Invalid input. Press y or n"
    continue
fi
done

# static 존재 여부 확인 후 사용자에게 입력 받아서 변경
# if [[ -z `grep "static" /etc/network/interfaces` ]]; 
if [[ -z `grep "static" ${CWD}/interfaces` ]]; 
then 
    echo "If you want to modify it, press the 'ctrl+backspace' key."
    read -p "ip address: " ipaddr
    read -p "netmask: " netmask
    read -p "gateway: " gateway
    read -p "DNS: " dns
    interface="""\nauto ${ifname}\niface ${ifname} inet static\naddress ${ipaddr}\nnetmask ${netmask}\ngateway ${gateway}\ndns-nameservers ${dns}"""
    echo -e ${interface} >> ${CWD}/interfaces
    sed -i '11,12s/^/#/' ${CWD}/interfaces
    # echo -e ${interface} >> /etc/network/interfaces
    # sed -i '11,12s/^/#/' /etc/network/interfaces
    echo "Successful change."
else
    echo "static ip is already exist." 
    # 수정을 원할 경우
fi

# 이상 출력을 정상 출력으로 리다이렉트
# /bin/rm -f ipconfigure.sh > /dev/null 2>&1

# 시스템 재부팅
while true; do
echo -n "Reboot the system now [Default: y]"
read awr3
if [[ "$awr3" == [Yy] || "$awr3" == "" ]]
    then
    echo "The system will reboot immediately."
    sleep 1
    sync;sync;sync;init 6
    break
elif [[ "$awr3" == [Nn] ]]
    then
    echo "CAUTION: Please note that you must reboot the system."
    exit 1
else
    echo "Invalid input. Press the y or n"
fi
done

