import json
import math
from qgis.core import QgsGeometry, QgsPointXY

# Cargar el archivo JSON con los datos de los terremotos
with open('earthquake_polygons.json', 'r') as file:
    earthquake_data = json.load(file)

# Simulación de nodos cargados (estos deberían venir de tu capa de nodos)
nodes = [
    {'id': 1, 'coordinates': (20.5, 145.0)},
    {'id': 2, 'coordinates': (21.0, 145.5)},
    # Agrega más nodos según sea necesario
]

# Definir anillos concéntricos y sus probabilidades de fallo
anillos = [
    {'radio': 10, 'probabilidad': 0.9},
    {'radio': 20, 'probabilidad': 0.7},
    {'radio': 30, 'probabilidad': 0.5},
    {'radio': 40, 'probabilidad': 0.3},
    {'radio': 50, 'probabilidad': 0.1}
]
xi = 10  # Longitud de segmento simplificado

# Función para crear geometría de polígono
def create_polygon_geometry(polygon_coords):
    points = [QgsPointXY(coord[0], coord[1]) for coord in polygon_coords]
    return QgsGeometry.fromPolygonXY([points])

# Modelo probabilístico
earthquake_probabilities = []

for node in nodes:
    node_geom = QgsGeometry.fromPointXY(QgsPointXY(node['coordinates'][0], node['coordinates'][1]))
    min_distance = float('inf')
    total_prob = 1  # Iniciar con 1 para multiplicación

    # Determinar en qué anillo cae cada nodo y calcular la probabilidad de fallo
    for earthquake in earthquake_data:
        polygon_geom = create_polygon_geometry(earthquake['polygon'])
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
    earthquake_probabilities.append((node['id'], probability))

# Imprimir resultados
for node_id, prob in earthquake_probabilities:
    print(f"Node ID: {node_id}, Earthquake Probability: {prob}")
