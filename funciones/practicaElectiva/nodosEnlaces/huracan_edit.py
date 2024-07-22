import json
import numpy as np
import math
import os
from dotenv import load_dotenv
import psycopg2
from shapely.geometry import Point
from shapely.wkt import loads as wkt_loads

# Load environment variables
load_dotenv(dotenv_path='../../.env')

db_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': "postgis",
    'port': os.getenv('PORT') 
}

conn = psycopg2.connect(**db_params)
cursor = conn.cursor()


def get_all_node_positions(cursor):
    cursor.execute("""
        SELECT id_node, ST_X(point) AS lon, ST_Y(point) AS lat FROM public_nodes;
    """)
    return cursor.fetchall()


def get_huracan_data(cursor):
    cursor.execute("""
        SELECT ogc_fid, wind_speed, ST_AsText(wkb_geometry) AS geom FROM huracan_historicos_polygons2;
    """)
    return cursor.fetchall()


# Obtener datos de los nodos y de los huracanes desde la base de datos
nodes = get_all_node_positions(cursor)
huracan_data = get_huracan_data(cursor)

# Constante que representa la tasa de disminución de la intensidad del huracán
D = 100  # Ajusta este valor según sea necesario

# Función para calcular la probabilidad de fallo
def calcular_probabilidad_fallo(distancia, D):
    return 1 - math.exp(-distancia / D)

# Modelo de amenazas de huracanes
huracan_probabilities = []

for node in nodes:
    node_id, lon, lat = node
    node_geom = Point(lon, lat)
    min_distance = float('inf')
    max_wind_speed = 0

    for huracan in huracan_data:
        ogc_fid, wind_speed, geom = huracan
        epicenter = wkt_loads(geom)
        distance = node_geom.distance(epicenter)

        if distance < min_distance:
            min_distance = distance
            max_wind_speed = wind_speed

    # Calcular la probabilidad de fallo según la distancia mínima al ojo del huracán
    probabilidad_fallo = calcular_probabilidad_fallo(min_distance, D)
    huracan_probabilities.append((node_id, probabilidad_fallo))

# Imprimir resultados
for node_id, prob in huracan_probabilities:
    print(f"Node ID: {node_id}, Hurricane Failure Probability: {prob}")

# Cerrar la conexión a la base de datos
cursor.close()
conn.close()
