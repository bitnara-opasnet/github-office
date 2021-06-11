#!/usr/bin/env python
import psycopg2
from lib.getapi import get_api_data, get_auth_token, make_workbook

if __name__ == '__main__' :
    is_token = get_auth_token()['Token']
    device_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')

    column_list = ['managementIpAddress', 'macAddress', 'role',  'family', 'platformId', 'hostname']
    data_list = []
    for i in device_data.get('response'):
        imsi_list = []
        for j in column_list:
            imsi_list.append(i.get(j))
        data_list.append(imsi_list)
    data_list = tuple(data_list)

    #db로 저장
    host_name = '127.0.0.1'
    db_name = 'testdb'
    user_name = 'testuser'
    password = '1q2w3'
    table_name = 'network_device'
    create_query = """create table network_device (management_ip varchar(255), macAddress varchar(255), role varchar(255), 
                                                  family varchar(255), platform_name varchar(255), device_name varchar(255));"""
    insert_query = """insert into network_device (management_ip, macAddress, role, family, platform_name, device_name) 
                      values(%s, %s, %s, %s, %s, %s);"""        

    try:
        conn = psycopg2.connect(host = host_name, dbname = db_name, user = user_name, password = password)
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS {};'.format(table_name))
        cur.execute(create_query)
        cur.executemany(insert_query, data_list)
        conn.commit()

        cur.execute('select * from {};'.format(table_name))
        table_col = [desc[0] for desc in cur.description]
        cur.execute('select platform_name, count(platform_name) as count from network_device group by platform_name;')
        chart_col = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        chart_data = []
        for i in rows:
            chart_data.append(list(i))
        chart_data = tuple(chart_data)
        
        cur.close()
        conn.close()  
    except psycopg2.DatabaseError as db_err:
        print(db_err)

    make_workbook('network_device1.xlsx', table_col, data_list, chart_col, chart_data, 11, 19, 'column', 'network device count_bar','H1')
