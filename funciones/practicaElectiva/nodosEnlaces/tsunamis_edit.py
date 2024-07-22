import numpy as np
import scipy.stats as stats
import os
import psycopg2
from dotenv import load_dotenv
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

def get_earthquake_data(cursor):
    cursor.execute("""
        SELECT id, ST_AsText(wkb_geometry) AS geom, mag FROM earthquake WHERE mag > 6.5;
    """)
    return cursor.fetchall()

# Obtener datos de los nodos y de los terremotos desde la base de datos
nodes = get_all_node_positions(cursor)
earthquakes = get_earthquake_data(cursor)

# Parámetros de la simulación
num_simulaciones = 1000
magnitudes = stats.norm(8, 1)  # Suponer magnitudes altas para tsunamis
distancia_max_impacto = 5000  # Máxima distancia de impacto significativo

# Función para calcular la intensidad del impacto en un nodo
def calcular_intensidad(distancia, magnitud):
    if distancia > distancia_max_impacto:
        return 0
    return magnitud * (1 - distancia / distancia_max_impacto)  # Modelo de disipación para tsunamis

# Simulación de Monte Carlo
resultados = np.zeros((num_simulaciones, len(nodes)))

for i in range(num_simulaciones):
    magnitudes_simuladas = magnitudes.rvs(size=len(earthquakes))
    for j, node in enumerate(nodes):
        node_id, lon, lat = node
        node_geom = Point(lon, lat)
        impacto_maximo = 0
        for earthquake, magnitud in zip(earthquakes, magnitudes_simuladas):
            earthquake_id, geom, earthquake_magnitude = earthquake
            epicenter = wkt_loads(geom)
            distancia = node_geom.distance(epicenter)
            impacto = calcular_intensidad(distancia, magnitud)
            if impacto > impacto_maximo:
                impacto_maximo = impacto
        resultados[i, j] = impacto_maximo

# Estadísticas de resultados
intensidades_promedio = np.mean(resultados, axis=0)
print("Intensidades promedio por nodo:", intensidades_promedio)

# Cerrar la conexión a la base de datos
cursor.close()
conn.close()
