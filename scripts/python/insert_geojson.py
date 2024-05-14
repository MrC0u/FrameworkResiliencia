import subprocess
import os

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(dotenv_path='../../.env')

def insert_geojson(file):
    file_path = os.path.dirname(file)
    file_name = os.path.splitext(os.path.basename(file))[0]
    command = (f'ogr2ogr -f "PostgreSQL" PG:"host=postgis port={os.getenv("PORT")} dbname={os.getenv("POSTGRES_DB")} user={os.getenv("POSTGRES_USER")} password={os.getenv("POSTGRES_PASSWORD")}" "{file}" -nln {file_name} -overwrite')
    try:
        respuesta = subprocess.check_output(command, shell=True,  executable="/bin/bash", text=True)
        print(f'{respuesta}')
        return 1
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")
        return 0

