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