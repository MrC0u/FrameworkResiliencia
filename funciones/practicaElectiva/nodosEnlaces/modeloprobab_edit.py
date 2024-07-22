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

# Definir anillos concéntricos y sus probabilidades de fallo
anillos = [
    {'radio': 10, 'probabilidad': 0.9},
    {'radio': 20, 'probabilidad': 0.7},
    {'radio': 30, 'probabilidad': 0.5},
    {'radio': 40, 'probabilidad': 0.3},
    {'radio': 50, 'probabilidad': 0.1}
]
xi = 10  # Longitud de segmento simplificado

# Modelo probabilístico
earthquake_probabilities = []

for node in nodes:
    node_id, lon, lat = node
    node_geom = Point(lon, lat)
    min_distance = float('inf')
    total_prob = 1  # Iniciar con 1 para multiplicación

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

    # Calcular la probabilidad de fallo según el anillo
    for anillo in anillos:
        if min_distance <= anillo['radio']:
            segmento_prob = 1 - math.pow((1 - anillo['probabilidad']), 1 / xi)
            total_prob *= (1 - segmento_prob)

    # Calcular la probabilidad total de fallo del nodo
    probability = 1 - total_prob
    earthquake_probabilities.append((node_id, probability))

# Imprimir resultados
for node_id, prob in earthquake_probabilities:
    print(f"Node ID: {node_id}, Earthquake Probability: {prob}")

# Cerrar la conexión a la base de datos
cursor.close()
conn.close()
