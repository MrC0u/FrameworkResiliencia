#!/bin/bash

if [ -z "$1" ]; then
    echo "Error - Faltan el parametro: <ID>"
    echo "[Ejemplo: gdrive-download <id>]"
    exit 1
fi

FILE_ID="$1"

axel -o "$FILENAME" --insecure "https://docs.google.com/uc?export=download&id=$FILE_ID"

echo "Archivo guardado en: $(pwd)/"
