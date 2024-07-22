import json
import math
import os
import psycopg2
from dotenv import load_dotenv
from shapely.geometry import Point, Polygon
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

def get_earthquake_data(cursor):
    cursor.execute("""
        SELECT id, ST_AsText(wkb_geometry) AS geom, mag FROM earthquake WHERE mag > 6.5;
    """)
    return cursor.fetchall()

# Obtener datos de los nodos y de los terremotos desde la base de datos
nodes = get_all_node_positions(cursor)
earthquake_data = get_earthquake_data(cursor)

# Umbral de intensidad para considerar un nodo como fallido
intensity_threshold = 0.7

def calculate_intensity(distance, magnitude):
    # Suponemos que la intensidad disminuye linealmente con la distancia hasta un límite de 100 km
    if distance > 100:
        return 0
    return magnitude * (1 - distance / 100)

earthquake_intensities = []
for node in nodes:
    node_id, lon, lat = node
    min_distance = float('inf')
    associated_magnitude = 0
    node_geom = Point(lon, lat)

    for earthquake in earthquake_data:
        earthquake_id, wkt_geometry, magnitude = earthquake
        try:
            polygon_geom = wkt_loads(wkt_geometry)
        except Exception as e:
            print(f"Error loading WKT geometry for earthquake {earthquake_id}: {e}")
            continue

        if isinstance(polygon_geom, Polygon):
            distance = node_geom.distance(polygon_geom)
            if distance < min_distance:
                min_distance = distance
                associated_magnitude = magnitude

    # Calcula la intensidad en el nodo dado
    intensity = calculate_intensity(min_distance, associated_magnitude)
    earthquake_intensities.append((node_id, intensity))

# Imprimir los resultados
for node_id, intensity in earthquake_intensities:
    status = "fallido" if intensity > intensity_threshold else "seguro"
    print(f"Node ID: {node_id}, Estado: {status}, Intensidad de terremoto: {intensity}")

# Cerrar la conexión a la base de datos
cursor.close()
conn.close()
