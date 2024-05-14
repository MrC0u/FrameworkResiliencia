import os
import psycopg2
import time

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(dotenv_path='../../.env')

db_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': "postgis",
    'port': os.getenv('PORT') 
}

def check_db():
    # Intentar conectarse hasta que PostgreSQL esté disponible
    while True:
        try:
            conn = psycopg2.connect(**db_params)
            conn.close()
            break
        except psycopg2.OperationalError:
            print('PostgreSQL is down - retrying in 2 sec.')
            time.sleep(2)
    
    print('PostgreSQL is up - executing init')
