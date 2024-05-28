#!/bin/bash

if [ -z "$1" ]; then
    echo "Error - Falta el parametro: <directorio de la funcion>"
    echo "[Ejemplo: framework-func ./funciones/prueba/algoritmo_1.py]"
    exit 1
fi

docker exec python_container python $1
