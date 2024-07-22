import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
import os
from dotenv import load_dotenv
from scipy.optimize import least_squares

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

def get_specific_node_positions(cursor, node_ids):
    """Fetch positions for specific nodes based on their IDs."""
    if not node_ids:
        raise ValueError("The list of node IDs is empty.")
    node_ids_tuple = tuple(node_ids)
    query = """
        SELECT id_node, ST_X(point) AS lon, ST_Y(point) AS lat FROM public_nodes4
        WHERE id_node IN %s;
    """
    cursor.execute(query, (node_ids_tuple,))
    return cursor.fetchall()

def residuals(params, points):
    """Calculate the Euclidean distance from each point to the guess point."""
    x, y = params
    return np.sqrt((points[:, 0] - x)**2 + (points[:, 1] - y)**2)

def calculate_new_node_position(nodes):
    """Calculate a new node position using least squares based on existing node positions."""
    points = np.array([[node['lon'], node['lat']] for node in nodes])
    x0 = np.mean(points, axis=0)
    result = least_squares(residuals, x0, args=(points,))
    return result.x

def insert_new_node(cursor, lat, lon, topology_id=1):
    """Insert a new node into the database with the calculated position."""
    
    # Crear la tabla new_nodes_min_cua si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS new_nodes_min_cua (
            id_node SERIAL PRIMARY KEY,
            id_topology INTEGER,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION,
            point GEOMETRY(Point, 4326)
        );
    """)
    
    # Insertar el nuevo nodo
    cursor.execute("""
        INSERT INTO new_nodes_min_cua (id_topology, lat, lon, point)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
    """, (topology_id, lat, lon, lon, lat))

def insert_new_link(cursor, source_node_id, new_node_id, topology_id=1):
    """Insert a new link between two nodes in the database."""
    
    # Crear la tabla new_links_min_cua si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS new_links_min_cua (
            id SERIAL PRIMARY KEY,
            id_topology INTEGER,
            source INTEGER,
            target INTEGER,
            geom GEOMETRY(LineString, 4326)
        );
    """)
    
    # Insertar el nuevo enlace
    cursor.execute("""
        INSERT INTO new_links_min_cua (id_topology, source, target, geom)
        VALUES (%s, %s, %s, ST_MakeLine(
            (SELECT point FROM public_nodes4 WHERE id_node = %s),
            (SELECT point FROM new_nodes_min_cua WHERE id_node = %s)
        ));
    """, (topology_id, source_node_id, new_node_id, source_node_id, new_node_id))

import traceback  # Importa el módulo traceback

def main():
    """Main function to execute the process."""
    specific_node_ids = [1,2,3]  # Modifica esta lista según sea necesario
    target_node_id = 15  # El ID del nodo con el que quieres conectar el nuevo nodo
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            nodes = get_specific_node_positions(cursor, specific_node_ids)
            if nodes:
                print(f"Calculating the position of the new node based on nodes with IDs {specific_node_ids}.")
                new_position = calculate_new_node_position(nodes)
                insert_new_node(cursor, new_position[1], new_position[0])
                cursor.execute("""
                    SELECT id_node FROM new_nodes_min_cua WHERE lat = %s AND lon = %s ORDER BY id_node DESC LIMIT 1;
                """, (new_position[1], new_position[0]))
                new_node_id = cursor.fetchone()['id_node']
                conn.commit()
                print("New node added at latitude:", new_position[1], "longitude:", new_position[0], "with ID:", new_node_id)
                
                # Inserta el enlace entre el nuevo nodo y un nodo existente (ej., nodo 12)
                insert_new_link(cursor, target_node_id, new_node_id)
                conn.commit()
                print(f"Link created between node {target_node_id} and new node {new_node_id}.")
            else:
                print("No nodes found with the specified IDs.")
    except Exception as e:
        print("An error occurred:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()