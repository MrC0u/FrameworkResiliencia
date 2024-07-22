import os
import psycopg2

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(dotenv_path='../../.env')

db_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': "postgis",
    'port': os.getenv('PORT') 
}

# Conectar a la base de datos PostGIS
conn = psycopg2.connect(**db_params)
cur = conn.cursor()
# gebco_2023_2


# Obtener la altitud mínima y máxima
cur.execute("SELECT MIN(dn), MAX(dn) FROM gebco_2023_2")
min_altitud, max_altitud = cur.fetchone()

# Cantidad de Intervalos
n_intervals = 6
intervals = []

amplitude = (max_altitud - min_altitud) // n_intervals
interval_min = 0
positive_interval = True

for i in range(n_intervals):
    # Intervalos positivos
    if(positive_interval):
        interval_max = (interval_min + amplitude)
        # Se llega al maximo
        if(interval_max + (amplitude//2) >= max_altitud):
            interval_max = max_altitud
            intervals.append((interval_min, interval_max))
            interval_max = 0
            positive_interval = False
        else:
            intervals.append((interval_min, interval_max))
            interval_min = interval_max
    # Intervalos Negativos
    else:
        interval_min = (interval_max - amplitude)
         # Se llega al minimo
        if(interval_min - (amplitude//2) <= min_altitud):
            interval_min = min_altitud
            intervals.insert(0,(interval_min, interval_max))
        else:
            intervals.insert(0,(interval_min, interval_max))
            interval_max = interval_min


print(f"Intervalos: {intervals}")

# Crear tabla cluster temporal
cur.execute("""
    DROP TABLE IF EXISTS temp_cluster_altitude;
    CREATE TABLE temp_cluster_altitude AS
    SELECT ogc_fid, dn, wkb_geometry
    FROM gebco_2023_2;
    ALTER TABLE temp_cluster_altitude ADD COLUMN Min_Altitude INTEGER;
""")
conn.commit()

# Añadir rango de amplitud perteneciente a cada fila
for i in intervals:
    cur.execute(f"""
    UPDATE temp_cluster_altitude
    SET Min_Altitude = {i[0]}
    WHERE dn BETWEEN {i[0]} AND {i[1]};
""")
conn.commit()

cur.execute(f""" ALTER TABLE temp_cluster_altitude DROP COLUMN dn;
 """)
conn.commit()

cur.execute(f""" 
    DROP TABLE IF EXISTS cluster_altitude;
    CREATE TABLE cluster_altitude (
    id serial PRIMARY KEY,
    Min_Altitude integer,
    wkb_geometry geometry(MultiPolygon)
);""")

cur.execute(f"""
    INSERT INTO cluster_altitude (Min_Altitude, wkb_geometry)
    SELECT Min_Altitude, ST_Union(ST_MakeValid(wkb_geometry)) AS wkb_geometry
    FROM temp_cluster_altitude
    GROUP BY Min_Altitude;
    DROP TABLE IF EXISTS temp_cluster_altitude;
""")
conn.commit()


# Cerrar la conexión
cur.close()
conn.close()