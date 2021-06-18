import psycopg2
import random
import xmltodict

class active_DB:
    host_name = '127.0.0.1'
    db_name = 'testdb'
    user_name = 'testuser'
    password = '1q2w3'
    table_name = 'active_session_test'

    def active_insert_DB(active_data):
        active_Session = active_data.get('activeList').get('activeSession')
        column_list = ['user_name', 'calling_station_id', 'nas_ip_address', 'acct_session_id', 'audit_session_id', 'server', 'framed_ip_address', 'framed_ipv6_address']
        data_list = []
        for i in active_Session:
            imsi_list = []
            for j in column_list:
                imsi_list.append(i.get(j))
            data_list.append(imsi_list)  
        create_query = """create table active_session_test (user_name varchar(255), calling_station_id varchar(255), nas_ip_address varchar(255), 
                                                        acct_session_id varchar(255), audit_session_id varchar(255), server varchar(255),
                                                        framed_ip_address varchar(255), framed_ipv6_address varchar(255));"""
        insert_query = """insert into active_session_test (user_name, calling_station_id, nas_ip_address, acct_session_id, audit_session_id, 
                            server, framed_ip_address, framed_ipv6_address) values(%s, %s, %s, %s, %s, %s, %s, %s);"""   
        try:
            conn = psycopg2.connect(host = active_DB.host_name, dbname = active_DB.db_name, user = active_DB.user_name, password = active_DB.password)
            cur = conn.cursor()
            cur.execute('DROP TABLE IF EXISTS {};'.format(active_DB.table_name))
            cur.execute(create_query)
            cur.executemany(insert_query, data_list)
            conn.commit()
            cur.close()
            conn.close() 
        except psycopg2.DatabaseError as db_err:
                print(db_err)
        active_xml = xmltodict.unparse(active_data, full_document=False)
        active_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + active_xml
        return (active_xml)    

    def active_data_fromDB_random():
        conn = psycopg2.connect(host = active_DB.host_name, dbname = active_DB.db_name, user = active_DB.user_name, password = active_DB.password)
        cur = conn.cursor()
        cur.execute("select * from {} limit {};".format(active_DB.table_name, random.randint(1000, 1500)))
        table_col = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        active_data = []
        for i in rows:
            active_data.append(dict(zip(table_col,i)))
        cur.close()
        conn.close()
        return(active_data)

    def active_data_fromDB():
        conn = psycopg2.connect(host = active_DB.host_name, dbname = active_DB.db_name, user = active_DB.user_name, password = active_DB.password)
        cur = conn.cursor()
        cur.execute("select * from {};".format(active_DB.table_name))
        table_col = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        active_data = []
        for i in rows:
            active_data.append(dict(zip(table_col,i)))
        cur.close()
        conn.close()
        return(active_data)
    
    def active_data_fromDB_limit():
        conn = psycopg2.connect(host = active_DB.host_name, dbname = active_DB.db_name, user = active_DB.user_name, password = active_DB.password)
        cur = conn.cursor()
        cur.execute("select * from {} where user_name like 'wireless%' limit {};".format(active_DB.table_name, random.randint(1000, 1500)))
        table_col = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        active_data = []
        for i in rows:
            active_data.append(dict(zip(table_col,i)))
        cur.execute("select * from {} where user_name like 'wired%' limit {};".format(active_DB.table_name, random.randint(80, 100)))
        table_col = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        for i in rows:
            active_data.append(dict(zip(table_col,i)))
        cur.close()
        conn.close()
        return(active_data)    