# -*- coding: utf-8 -*-

import requests
import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
import sqlite3

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
stock_data = []
for stock in stock_list:
     if len(stock) > 1 :
          stock_data.append(stock.get_text().split())
stock_data_list=[]          
for i in stock_data:
    stock_data_list.append(tuple(i))

soup.find('td',{'class':'center'}).attrs['href']
links = soup.find("table", attrs={"class": "type_2"}).find("tbody").find_all("a")

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

cur.execute("select * from stock;")
rows = cur.fetchall()

import pandas as pd
url = 'https://finance.naver.com/item/sise.nhn?code=005930'

