import json
import math
from qgis.core import QgsGeometry, QgsPointXY

# Cargar el archivo JSON con los datos de los tornados
with open('tornado_historicos_polygons.json', 'r') as file:
    tornado_data = json.load(file)

# Simulación de nodos cargados (estos deberían venir de tu capa de nodos)
nodes = [
    {'id': 1, 'coordinates': (32.5, -87.5)},
    {'id': 2, 'coordinates': (33.0, -87.0)},
    # Agrega más nodos según sea necesario
]

# Constante que representa la tasa de disminución de la intensidad del tornado
D = 100  # Ajusta este valor según sea necesario

# Función para calcular la probabilidad de fallo
def calcular_probabilidad_fallo(distancia, D):
    return 1 - math.exp(-distancia / D)

# Modelo de amenazas de tornados
tornado_probabilities = []

for node in nodes:
    node_geom = QgsGeometry.fromPointXY(QgsPointXY(node['coordinates'][0], node['coordinates'][1]))
    min_distance = float('inf')
    tornado_intensity = 0

    for tornado in tornado_data:
        start_location = QgsPointXY(tornado['start_location'][0], tornado['start_location'][1])
        end_location = QgsPointXY(tornado['end_location'][0], tornado['end_location'][1])
        tornado_path = QgsGeometry.fromPolylineXY([start_location, end_location])

        distance = node_geom.distance(tornado_path)

        if distance < min_distance:
            min_distance = distance
            tornado_intensity = tornado['width_yards']  # Suponemos que la intensidad está relacionada con el ancho del tornado

    # Calcular la probabilidad de fallo según la distancia mínima al centro del tornado
    probabilidad_fallo = calcular_probabilidad_fallo(min_distance, D)
    tornado_probabilities.append((node['id'], probabilidad_fallo))

# Imprimir resultados
for node_id, prob in tornado_probabilities:
    print(f"Node ID: {node_id}, Tornado Failure Probability: {prob}")
