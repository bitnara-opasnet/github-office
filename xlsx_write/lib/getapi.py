#!/usr/bin/env python
import requests
import base64
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

def get_api_data(token, uri_addr):
  url = uri_addr
  headers = {
      'X-Auth-Token': '{}'.format(token),
      'content-type': 'application/json'
  }
  response = requests.get(url, headers=headers, verify=False)
  return response.json()

def make_workbook(name, table_col, table_data, chart_col, chart_data, chart_start_num, chart_end_num, type, chart_title, chart_position):
  workbook = xlsxwriter.Workbook(name)
  worksheet = workbook.add_worksheet()
  bold = workbook.add_format({'bold':True})
  worksheet.write_row(0, 0, table_col, bold) 
  row = 1
  for i in table_data:
    worksheet.write_row(row, 0, i)
    row += 1

  worksheet.write_row(chart_start_num, 0, chart_col, bold)
  row = chart_start_num +1
  for i in chart_data:
    worksheet.write_row(row, 0, i)
    row += 1

  chart1 = workbook.add_chart({'type': type})
  chart1.add_series({
    'name': ['sheet1', chart_start_num, 0],
    'categories' : '=Sheet1!$A${}:$A${}'.format(chart_start_num+2, chart_end_num),
    'values': '=Sheet1!$B${}:$B${}'.format(chart_start_num+2, chart_end_num)
    })
  chart1.set_title({'name': chart_title})
  worksheet.insert_chart(chart_position, chart1)

  workbook.close()  