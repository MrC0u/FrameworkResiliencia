import json
import numpy as np
import math
from qgis.core import QgsGeometry, QgsPointXY

# Cargar el archivo JSON con los datos de los huracanes
with open('huracan_historicos_polygons.json', 'r') as file:
    huracan_data = json.load(file)

# Simulación de nodos cargados (estos deberían venir de tu capa de nodos)
nodes = [
    {'id': 1, 'coordinates': (27.5, -96.0)},
    {'id': 2, 'coordinates': (28.0, -96.5)},
    # Agrega más nodos según sea necesario
]

# Constante que representa la tasa de disminución de la intensidad del huracán
D = 100  # Ajusta este valor según sea necesario

# Función para calcular la probabilidad de fallo
def calcular_probabilidad_fallo(distancia, D):
    return 1 - math.exp(-distancia / D)

# Modelo de amenazas de huracanes
huracan_probabilities = []

for node in nodes:
    node_geom = QgsGeometry.fromPointXY(QgsPointXY(node['coordinates'][0], node['coordinates'][1]))
    min_distance = float('inf')
    max_wind_speed = 0

    for huracan in huracan_data:
        epicenter = QgsPointXY(huracan['epicenter'][0], huracan['epicenter'][1])
        wind_speed = huracan['wind_speed']
        distance = node_geom.distance(QgsGeometry.fromPointXY(epicenter))

        if distance < min_distance:
            min_distance = distance
            max_wind_speed = wind_speed

    # Calcular la probabilidad de fallo según la distancia mínima al ojo del huracán
    probabilidad_fallo = calcular_probabilidad_fallo(min_distance, D)
    huracan_probabilities.append((node['id'], probabilidad_fallo))

# Imprimir resultados
for node_id, prob in huracan_probabilities:
    print(f"Node ID: {node_id}, Hurricane Failure Probability: {prob}")
