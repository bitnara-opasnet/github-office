#!/usr/bin/env python
import requests
import base64
import psycopg2
import xlsxwriter

def get_auth_token():
  url = "https://100.64.0.101/dna/system/api/v1/auth/token"
  id = 'admin'
  pw = 'Cisco!23'
  cre = id+':'+pw
  credential_info = base64.b64encode(cre.encode('utf-8'))
  credential_info = 'Basic '+credential_info.decode('utf-8')
  payload = {}
  headers = {
    'content-type': 'application/json',
    'authorization': credential_info
  }
  x_auth_token = requests.request("POST", url, headers=headers, data=payload, verify=False)
  return(x_auth_token.json())

is_token = get_auth_token()['Token']

def get_api_data(token, uri_addr):
    url = uri_addr
    headers = {
        'X-Auth-Token': '{}'.format(token),
        'content-type': 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    return response.json()

devide_data = get_api_data(is_token, 'https://100.64.0.101/dna/intent/api/v1/network-device')

column_list = ['managementIpAddress', 'macAddress', 'role',  'platformId', 'hostname']
data_list = []
for i in devide_data.get('response'):
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
create_query = """create table network_device (management_ip varchar(255), macAddress varchar(255), role varchar(255), 
                                               platform_name varchar(255), device_name varchar(255));"""
insert_query = """insert into network_device (management_ip, macAddress, role, platform_name, device_name) 
                  values(%s, %s, %s, %s, %s);"""        

try:
  conn = psycopg2.connect(host = host_name, dbname = db_name, user = user_name, password = password)
  cur = conn.cursor()
  cur.execute('DROP TABLE IF EXISTS network_device;')
  cur.execute(create_query)
  cur.executemany(insert_query, data_list)
  conn.commit()

  cur.execute('select * from network_device;')
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

#엑셀로 출력
def make_workbook(name, table_col, table_data, chart_col, chart_data, chart_start_num):
  workbook = xlsxwriter.Workbook(name)
  worksheet = workbook.add_worksheet()
  bold = workbook.add_format({'bold':True})
  worksheet.write_row(0, 0, table_col, bold) 
  row = 1
  for i in range(len(table_data)):
    worksheet.write_row(row, 0, table_data[i])
    row += 1

  worksheet.write_row(chart_start_num, 0, chart_col, bold)
  row = chart_start_num +1
  for i in range(len(chart_data)):
    worksheet.write_row(row, 0, chart_data[i])
    row += 1

  def make_chart(type, chart_title, chart_start_num, chart_end_num, chart_position):
    chart1 = workbook.add_chart({'type': type})
    chart1.add_series({
      'name': ['sheet1', chart_start_num, 0],
      'categories' : '=Sheet1!$A${}:$A${}'.format(chart_start_num+2, chart_end_num),
      'values': '=Sheet1!$B${}:$B${}'.format(chart_start_num+2, chart_end_num)
    })
    chart1.set_title({'name': chart_title})
    worksheet.insert_chart(chart_position, chart1)
  make_chart('column', 'network device count_bar', 11, 19, 'H1')
  make_chart('pie', 'network device count_pie', 11, 19, 'H16')

  workbook.close()
  
make_workbook('network_device1.xlsx', table_col, data_list, chart_col, chart_data, 11)
