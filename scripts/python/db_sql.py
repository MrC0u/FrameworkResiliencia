import os
import psycopg2

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(dotenv_path='../../.env')

# Conexion a DB PostgreSQL
db_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': "postgis",
    'port': os.getenv('PORT') 
}

def psql(sentencia):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    #print(f'Sentencia: {sentencia}')
    cur.execute(sentencia)
    if ('INSERT INTO' in sentencia) or ('CREATE' in sentencia):
        conn.commit()
    else:
        response = cur.fetchall()

    cur.close()
    conn.close()
    
    if ('INSERT INTO' in sentencia) or ('CREATE' in sentencia):
        return 1
    else:
        return response

    
