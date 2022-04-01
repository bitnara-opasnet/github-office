import os
import sys
import csv
from smp.models import PortProtocol

# current_directory_path = os.getcwd()
# csv_file_name = 'service-names-port-numbers.csv'
# current_file_path = f'{current_directory_path}{os.sep}{csv_file_name}'
# df = pd.read_csv(filepath_or_buffer= current_file_path, sep=",")
# df = df.iloc[:, 0:4]
# transport_df = df.dropna(subset=["Service Name", "Port Number", "Transport Protocol"])
# transport_df = transport_df[~transport_df['Port Number'].str.contains('-')]


sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

class CSVFileIO(object):
    def __init__(self, filename, delimiter):
        self.filename = filename
        self.delimiter = delimiter

    def get_csv_reader(self): 
        results = [] 
        try:
            csvfile = open(self.filename, "r", encoding='utf-8') 
            results = list(csv.DictReader(csvfile, delimiter=self.delimiter)) 
        except FileNotFoundError as err:
            print(err)
        return results

    # def insert_category(self):    
    #     dictlist = self.get_csv_reader()
    #     for row in dictlist:
    #         if not PortProtocol.objects.filter(name=row['servicename']).exists():
    #             service_name = PortProtocol.objects.create(
    #                 servicename = row['Service Name'] )
    #     print('CATEGORY DATA UPLOADED SUCCESSFULY!')  

    def transfer_portname(self):
        dictlist = self.get_csv_reader()

        port_list = []
        for i in list(dictlist):
            if i.get('Service Name') != '' and i.get('Port Number') != '':
                port_list.append(i) 
                
        results = {}
        for i in port_list:
            # results.append({i.get('Port Number'): [i.get('Transport Protocol'), i.get('Service Name'), i.get('Description')]})
            results[i.get('Port Number') + i.get('Transport Protocol')] = i.get('Service Name')
        return results
    
    def export_flag_url(self):
        dictlist = self.get_csv_reader()
        for i in list(dictlist):
            i['flag'] = i['AP2'].lower() + '.png'

        fieldnames = list(dictlist[0].keys())
        f = open('country_code_flags.csv', 'w')
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(list(dictlist))
        f.close()
    
    def get_flag_url(self):
        dictlist = self.get_csv_reader()

        results={}
        for i in list(dictlist):
            results[i.get('AP2')] = i.get('flag')
        return results
    