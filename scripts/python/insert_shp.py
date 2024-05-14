import subprocess
import os
from insert_geojson import insert_geojson

def insert_shp(file):
    file_path = os.path.dirname(file)
    file_name = os.path.splitext(os.path.basename(file))[0]
    if os.path.exists(f'{file_path}/{file_name}.geojson'):
        print(f'Ya existe el archivo Geojson para {file_name}.shp')
        return 1
    command = (f'ogr2ogr -f GeoJSON -t_srs crs:84 {file_path}/{file_name}.geojson {file}')
    try:
        subprocess.check_output(command, shell=True,  executable="/bin/bash", text=True)
        print(f'Transformado archivo [{file}] a [{file_path}/{file_name}.geojson] ')
        insert_geojson(f'{file_path}/{file_name}.geojson')
        return 1
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")
        return 0