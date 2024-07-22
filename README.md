# Framework

-- En Construccion --

### Como guardar data / scripts
La Metadata / Amenazas / Topologias se deben guardar en la carpeta "data" (se pueden crear subcarpetas para organizar mejor el contenido).
Hasta ahora soporta archivos de tipo: "geojson, shp, sql y tif". Automaticamente deberia crear las tablas y el contenido de estos, con solo almacenar los archivos en esta carpeta.

El resto de funcionalidades o scripts se deben guardar en la caperta "funciones" (tambien se pueden crear subcarpetas para organizar mejor el contenido).

---
### Antes de ejecutar

Es necesario crear un archivo con nombre ".env" en el directorio base del respositorio (donde se encuentra el docker-compose.yml). Este archivo debe tener:

```
POSTGRES_PASSWORD=
POSTGRES_USER=
POSTGRES_DB=
HOST=
PORT=
DBPORT=
```
por ejemplo los valores podrian ser:
```
POSTGRES_PASSWORD=postgres
POSTGRES_USER=postgres
POSTGRES_DB=gis
HOST=localhost
PORT=5432
DBPORT=5433
```
En este ejemplo, para visualizar los datos a traves de QGIS y conectarse a la base de datos se debe usar el puerto 5433.
---

### Correr contenedor

Se utiliza el comando:
```
docker compose up
```
___
### Entrar a la base de datos

Luego se entra al contenedor y la base de datos con:
```
docker exec -it postgis_container psql -h localhost -U postgres -d gis
```

Del mismo modo te puedes conectar al contenedor de python:
```
docker exec -it python_container bin/bash
```
---
### Correr funciones en el contenedor de python (sin entrar al contendor):
```
docker exec python_container python '/funciones/Ruta_De_La_Funcion.py'
```
Para que se imprima el resultado en el log de docker:
```
docker exec python_container sh -c 'python /funciones/Ruta_De_La_Funcion.py > /proc/1/fd/1 2> /proc/1/fd/2'
```



Cualquier error notifiquenmelo pls 🥺. \
Aun estoy implementando/arreglando las funcionalidades.

