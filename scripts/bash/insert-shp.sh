#!/usr/bin/env bash
source .env


ogr2ogr -f PostgreSQL PG:"host=$HOST user=$POSTGRES_USER password=$POSTGRES_PASSWORD dbname=$POSTGRES_DB port=$PORT" ./data/ciclovias/Ciclovías_2Semestre_2022_snc.shp -lco PRECISION=NO -nlt MULTILINESTRING -nln ciclovias_all -lco GEOMETRY_NAME=geom -lco FID=ID -dim 3