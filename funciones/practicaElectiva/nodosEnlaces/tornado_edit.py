import json
import math
import os
import psycopg2
from dotenv import load_dotenv
from shapely.geometry import Point, LineString
from shapely.wkb import loads as wkb_loads
import binascii

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

def get_tornado_data(cursor):
    cursor.execute("""
        SELECT ogc_fid, wkb_geometry, width_yards FROM tornado_historicos_polygons;
    """)
    return cursor.fetchall()

# Obtener datos de los nodos y de los tornados desde la base de datos
nodes = get_all_node_positions(cursor)
tornado_data = get_tornado_data(cursor)

# Constante que representa la tasa de disminución de la intensidad del tornado
D = 100  # Ajusta este valor según sea necesario

# Función para calcular la probabilidad de fallo
def calcular_probabilidad_fallo(distancia, D):
    return 1 - math.exp(-distancia / D)

# Modelo de amenazas de tornados
tornado_probabilities = []

for node in nodes:
    node_id, lon, lat = node
    node_geom = Point(lon, lat)
    if not node_geom.is_valid:
        print(f"Invalid geometry for node {node_id}: {node_geom}")
        continue
    
    min_distance = float('inf')
    tornado_intensity = 0

    for tornado in tornado_data:
        tornado_id, wkb_geometry_hex, width_yards = tornado
        try:
            wkb_geometry = binascii.unhexlify(wkb_geometry_hex)
            tornado_path = wkb_loads(wkb_geometry)
        except Exception as e:
            print(f"Error loading WKB geometry for tornado {tornado_id}: {e}")
            continue
        
        if isinstance(tornado_path, LineString):
            start_location = tornado_path.coords[0]
            end_location = tornado_path.coords[-1]
            tornado_line = LineString([start_location, end_location])

            if not tornado_line.is_valid:
                print(f"Invalid geometry for tornado {tornado_id}: {tornado_line}")
                continue

            try:
                distance = node_geom.distance(tornado_line)
                if distance < min_distance:
                    min_distance = distance
                    tornado_intensity = width_yards  # Suponemos que la intensidad está relacionada con el ancho del tornado
            except Exception as e:
                print(f"Error calculating distance for node {node_id} and tornado {tornado_id}: {e}")
                continue

    # Calcular la probabilidad de fallo según la distancia mínima al centro del tornado
    if min_distance != float('inf'):
        probabilidad_fallo = calcular_probabilidad_fallo(min_distance, D)
        tornado_probabilities.append((node_id, probabilidad_fallo))

# Imprimir resultados
for node_id, prob in tornado_probabilities:
    print(f"Node ID: {node_id}, Tornado Failure Probability: {prob}")

# Cerrar la conexión a la base de datos
cursor.close()
conn.close()
