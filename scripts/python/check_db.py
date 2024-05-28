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
    # Intentar conexion a PostgreSQL
    while True:
        try:
            conn = psycopg2.connect(**db_params)
            conn.close()
            break
        except psycopg2.OperationalError:
            print('PostgreSQL is down - reintentando en 5 segundos...')
            time.sleep(5)
    
    print('PostgreSQL is up - ejecutando init')
