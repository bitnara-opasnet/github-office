import xlsxwriter 

def make_workbook(name, table_col, table_data):
  workbook = xlsxwriter.Workbook(name)
  worksheet = workbook.add_worksheet()
  bold = workbook.add_format({'bold':True})
  worksheet.write_row(0, 0, table_col, bold) 
  row = 1 
  for i in table_data:
    worksheet.write_row(row, 0, i)
    row += 1
  workbook.close() 

def make_workbook_chart(name, table_col, table_data, chart_col, chart_data, chart_start_num, chart_end_num, type, chart_title, chart_position):
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