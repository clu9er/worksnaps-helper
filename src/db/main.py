import psycopg2
import os

from config_reader import config

def migrate_database() -> None:
    conn = psycopg2.connect(config.database.connection_string)
    cur = conn.cursor()
    
    script_dir = os.path.dirname(__file__)
    sql_file_path = os.path.join(script_dir, 'migrations', 'init.sql')
    
    cur.execute(open(sql_file_path, 'r').read())
    conn.commit()
    conn.close()
