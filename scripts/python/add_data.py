from insert_sql import insert_sql
from insert_shp import insert_shp
from insert_geojson import insert_geojson
from insert_tif import insert_tif
from insert_json import insert_json
import os

def add_data(file_path):
    _, file_extension = os.path.splitext(file_path)
    
    file_extension = file_path.rsplit('.', 1)[-1].lower()

    if file_extension == "sql":
        print(f"Procesando archivo SQL: {file_path}")
        insert_sql(file_path)
    elif file_extension == "shp":
        print(f"Procesando archivo SHP: {file_path}")
        insert_shp(file_path)
    elif file_extension == "geojson":
        print(f"Procesando archivo GeoJSON: {file_path}")
        insert_geojson(file_path)
    elif file_extension == "json":
        print(f"Procesando archivo JSON: {file_path}")
        insert_json(file_path)
    elif file_extension == "tif":
        print(f"Procesando archivo TIF: {file_path}")
        insert_tif(file_path)
    else:
        print(f"Tipo de archivo no soportado: {file_extension}")
