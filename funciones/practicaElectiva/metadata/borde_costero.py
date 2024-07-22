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

# Crear tabla temporal con Area de bordes
cur.execute("""
    DROP TABLE IF EXISTS temp_coastal_areas;
    CREATE TABLE temp_coastal_areas AS
    SELECT ogc_fid, dn, wkb_geometry
    FROM gebco_2023_2
    WHERE dn BETWEEN -200 AND 1;
""")
conn.commit()

# Encontrar los bordes costeros - Lineas
cur.execute("""
    DROP TABLE IF EXISTS temp_coastal_edges;
    CREATE TABLE temp_coastal_edges AS
    WITH land_water_boundaries AS (
        SELECT 
            ST_Intersection(l.wkb_geometry, w.wkb_geometry) AS geom
        FROM 
            gebco_2023_2 l,
            temp_coastal_areas w
        WHERE 
            l.dn > 0 AND
            w.dn BETWEEN -200 AND 1 AND
            ST_Intersects(l.wkb_geometry, w.wkb_geometry)
    )
    SELECT 
        ST_CollectionExtract(geom, 2) AS geom
    FROM 
        land_water_boundaries
    WHERE 
        ST_Dimension(geom) = 1;
""")
conn.commit()

# Almacenar los bordes 
cur.execute("""
    DROP TABLE IF EXISTS coastal_edges;
    CREATE TABLE coastal_edges (
        id SERIAL PRIMARY KEY,
        geom GEOMETRY(MultiLineString, 4326)
    );

    INSERT INTO coastal_edges (geom)
    SELECT geom FROM temp_coastal_edges;
""")
conn.commit()


cur.close()
conn.close()

print("Bordes costeros guardados en la base de datos.")