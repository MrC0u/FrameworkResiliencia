import json
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

# Umbral de intensidad para considerar un nodo como fallido
intensity_threshold = 0.7

def calculate_intensity(distance, magnitude):
    # Suponemos que la intensidad disminuye linealmente con la distancia hasta un límite de 100 km
    if distance > 100:
        return 0
    return magnitude * (1 - distance / 100)

def create_polygon_geometry(polygon_coords):
    points = [QgsPointXY(coord[0], coord[1]) for coord in polygon_coords]
    return QgsGeometry.fromPolygonXY([points])

earthquake_intensities = []
for node in nodes:
    min_distance = float('inf')
    associated_magnitude = 0
    node_geom = QgsGeometry.fromPointXY(QgsPointXY(node['coordinates'][0], node['coordinates'][1]))

    for earthquake in earthquake_data:
        polygon_geom = create_polygon_geometry(earthquake['polygon'])
        distance = node_geom.distance(polygon_geom)
        magnitude = earthquake['magnitude']
        if distance < min_distance:
            min_distance = distance
            associated_magnitude = magnitude

    # Calcula la intensidad en el nodo dado
    intensity = calculate_intensity(min_distance, associated_magnitude)
    earthquake_intensities.append((node['id'], intensity))

# Imprimir los resultados
for node_id, intensity in earthquake_intensities:
    status = "fallido" if intensity > intensity_threshold else "seguro"
    print(f"Node ID: {node_id}, Estado: {status}, Intensidad de terremoto: {intensity}")
