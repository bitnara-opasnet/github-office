# -*- coding: utf-8 -*-

import requests
import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
import sqlite3
import re

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent={0}'.format(user_agent))
driver = webdriver.Chrome('/usr/bin/chromedriver',options=options)

url = 'https://finance.naver.com/sise/sise_market_sum.nhn'
result = requests.get(url)
soup = BeautifulSoup(result.content, "html.parser")

stock_head = soup.find("thead").find_all("th")
data_head = [head.get_text() for head in stock_head]
data_head = data_head[:-1]
stock_list = soup.find("table", attrs={"class": "type_2"}).find("tbody").find_all("tr")

# 회사 code 찾기
p = re.compile('=[0-9]+')
code_list = []
for i in stock_list:
    find_code = p.search(str(i))
    if p.search(str(i)) != None :
        find_code = find_code.group().replace('=','')
        code_list.append(find_code)

# 주식 정보 찾기
stock_data = []
for stock in stock_list:
     if len(stock) > 1 :
          stock_data.append(stock.get_text().split())

# 주식 정보에 회사 코드 넣기
for i,j in zip (stock_data, code_list):
    i.append(j)

stock_data_list=[]          
for i in stock_data:
    stock_data_list.append(tuple(i))

create_query = '''CREATE TABLE stock(id INTEGER, name varchar(255), nowVal varchar(255), PrePricenowVal varchar(255), fluctuation varchar(255), faceVal varchar(255), totalVal varchar(255), 
                                  stockListNum varchar(255), ROF varchar(255), volume varchar(255), PER varchar(255), ROE varchar(255))'''
insert_query = '''insert into stock (id, name, nowVal, PrePricenowVal, fluctuation, faceVal, totalVal, stockListNum, ROF, volume, PER, ROE) 
                              values(?, ?, ?,?,?,?,?,?,?,?,?,?);'''  

conn = sqlite3.connect("board.db")
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS stocks;')
cur.execute(create_query)
cur.executemany(insert_query, stock_data_list)
conn.commit()
cur.close()
conn.close() 

cur.execute("select * from stocks;")
rows = cur.fetchall()

import pandas as pd
url = 'https://finance.naver.com/item/sise.nhn?code=005930'

LANG="ko_KR.UTF-8"
LANG="ko_KR.EUC-KR"
LANGUAGE="ko_KR:ko:en_GB:en" 

# export LANG=ko_KR.utf8
soup.find_all(attrs={'class':'card-title'})

def get_hostname(data):
    if data[0].get('family') == 'Unified AP' and data[0].get('role') == 'ACCESS' :
        result = 'AP'
    elif data[0].get('family') == 'Switches and Hubs' and data[0].get('role') == 'ACCESS' :
        result = 'Edge'
    elif data[0].get('family') == 'Switches and Hubs' and data[0].get('role') == 'DISTRIBUTION' :
        result = 'Border'
    elif data[0].get('family') == 'Routers' and data[0].get('role') == 'BORDER ROUTER' :
        result = 'Router'
    return result

import json
from lib.random_topology import get_topology_data, get_hostname

with open('network_device.json', 'r') as json_file:
    device_data = json.load(json_file)

for i in device_data.get('response'):
    i.update({'Item':get_hostname(i)})

category = 'Item'
keyword = 'AP'

title_list = ['Item', 'managementIpAddress', 'macAddress', 'role',  'platformId', 'hostname', 'softwareVersion']

category_list = []
for i in device_data.get('response'):
    category_list.append(i.get(category))

searched_list = []
for item in category_list:
    if item.find(keyword) != -1 : 
        searched_list.append(item)
searched_list = set(searched_list)

device_list = []
for i in device_data.get('response'):
    imsi_list = []
    for j in searched_list:
        if i.get(category) == j :
            for k in title_list:
                imsi_list.append(i.get(k))
    device_list.append(imsi_list)

device_list = list(filter(None, device_list))
device_list = tuple(device_list)



device_list = []
for i in device_data.get('response'):
    imsi_list = []
    imsi_list.append(get_hostname(i))
    for j in title_list:
        imsi_list.append(i.get(j))
    device_list.append(imsi_list)
    
device_list = tuple(device_list)

def random_ap_link(new_node_data, total_num, div_num):
    new_node_list = new_node_data
    link_n1 = increase_num(303)
    link_n2 = increase_num(316)
    id_sample1 = '252303'
    id_sample2 = '252316'
    random_link = []
    for i in range(total_num):
        if i < div_num:
           random_link.append([new_node_list[i].get('id'), id_sample1[:-3] + str(next(link_n1))])
        else:
            random_link.append([new_node_list[i].get('id'), id_sample2[:-3] + str(next(link_n2))])
    return random_link

def ap_link_create(new_node_data, link_data, total_num, div_num):
    for i in link_data:
        if i.get('source') == '28975461-7826-4cac-b9f6-88aa9e5e3f3f':
            ori_link_one = i 
        elif i.get('source') == '30015a66-1fb6-452b-8504-f0990f8a9509':
            ori_link_two = i
    ori_link_one = copy.deepcopy(ori_link_one)
    ori_link_two = copy.deepcopy(ori_link_two)

    final_links = []
    random_link = random_ap_link(new_node_data, total_num, div_num)
    for i in range(total_num):
        if i < div_num:
            ori_link_one.update({'id':random_link[i][1], 'source':random_link[i][0]})
            random_dic1 = dict(ori_link_one.items())
        else:
            ori_link_two.update({'id':random_link[i][1], 'source':random_link[i][0]})
            random_dic1 = dict(ori_link_two.items()) 
        final_links.append(random_dic1)    
    return(final_links) 

import json
from lib.random_topology import *
import copy

with open('physical-topology-demo1.json', 'r') as json_file:
    json_data = json.load(json_file)

ori_node = json_data['nodes']
final_nodes = json_data['nodes'][:]
final_links = json_data['links'][:]

Edge_node = random_node_create(ori_node, 'Edge', '/24', 1000, 20)
Edge_links = edge_link_create(Edge_node, final_links, 20, 10)
for i in Edge_links:
    final_links.append(i)

AP_node = random_node_create(ori_node, 'AP', '/24', 9509, 30)
for i in AP_node:
    final_nodes.append(i)

ap_node_list = new_node_list(ori_node, final_nodes)

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
    ori_link_three.update({'target': new_edge[0].get('id'), 'id': '30000'})
    random_dic1 = dict(ori_link_three.items())
    new_links.append(random_dic1) 
    ori_link_four.update({'target': new_edge[1].get('id'), 'id': '40000'})
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

ap_links = ap_link_create(ap_node_list, final_links, 30, 5, 10, 20)


from PIL import Image
image1 = Image.open('./static/image/littledeep_illustration_flower_style1.png')
imag1_size = image1.size
image1 = image1.resize((int(imag1_size[0]*(0.5)), int(imag1_size[1]*(0.5))))
imag1_size = image1.size
print(imag1_size)
image1.save('./static/image/littledeep_illustration_flower_style1.png')

from time import sleep
import psutil

conns = psutil.net_connections()
for conn in conns:
    if conn.status == 'ESTABLISHED' :
        print(conn.pid, conn.raddr)

procs = psutil.process_iter(['pid', 'name', 'username'])
for p in procs:
    print(p.info)


def net_io():
    net = psutil.net_io_counters()
    sent = net.bytes_sent/1024**2
    recv = net.bytes_recv/1024**2
    return round(sent, 2), round(recv, 2)

while True:    
    net = psutil.net_io_counters()
    sent = net.bytes_sent/1024**2
    recv = net.bytes_recv/1024**2
    print('sent: {:.3f} MB / recv: {:.3f} MB'.format(sent, recv))
    sleep(2)