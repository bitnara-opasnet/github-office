#!/usr/bin/env python

import datetime
from pytz import timezone
from socket import *
import time
import timeit

SRV = '10.0.2.15'
# SRV = '192.168.103.253'
PORT = 514

def get_msg(dt):
    a = dt.strftime('%b %d %H:%M:%S')
    b = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    c = dt.strftime('%z')
    msg = """<181> {} admin CISE_Failed_Attempts 0000027489 3 0 {} {} 0000311023 5440 NOTICE RADIUS: (KBNR) Endpoint abandoned EAP session and started new, 
    ConfigVersionId=74, Device IP Address=100.124.128.161, DestinationIPAddress=100.64.0.100, UserName=ABC, AcsSessionID=admin/385305582/9414, 
    AuthenticationMethod=MSCHAPV2, SelectedAccessService=Default Network Access, DetailedInfo=Invalid username or password specified\, Retry is allowed, 
    FailureReason=22056 Subject not found in the applicable identity store(s), Step=11001, Step=11017, Step=15049, Step=15008, Step=11507, Step=12500, 
    Step=12625, Step=11006, Step=11001, Step=11018, Step=12301, Step=12300, Step=12625, Step=11006, Step=11001, Step=11018, Step=12302, Step=12318, 
    Step=12800, Step=12805, Step=12806, Step=12807, Step=12810, Step=12811, Step=12305, Step=11006, Step=11001, Step=11018, Step=12304, Step=12318, 
    Step=12812, Step=12813, Step=12804, Step=12801, Step=12802, Step=12914, Step=12816, Step=12310, Step=12305, Step=11006,"""
    result = msg.format(a, b, c).encode('utf-8')
    return result

def send_mans(data):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.sendto(data,(SRV, PORT))
    sock.close()

def send_msg_while():
    while True:
        cur_time = timezone('Asia/Seoul').localize(datetime.datetime.now())
        t = get_msg(cur_time)
        send_mans(t)
        time.sleep(0.2)

from threading import Thread
t1 = Thread(target = send_msg_while)
t1.start()


# 경과시간 측정
# for i in range(10):
#     cur_time = timezone('Asia/Seoul').localize(datetime.datetime.now())
#     t = get_msg(cur_time)
#     start_time = time.process_time()
#     send_mans(t)
#     end_time = time.process_time()
#     print(start_time - end_time)
