#!/usr/local/bin/bash

# Ruta del directorio a monitorear
MONITOR_DIR="/data"

# Archivo de registro para almacenar el estado anterior
LOG_FILE="/scripts/hash/file_state.log"

# Función para generar el estado actual de los archivos
generate_current_state() {
  find "$MONITOR_DIR" -type f -exec sha256sum {} \; > "/scripts/hash/current_state.log"
}


# Función para comparar el estado actual con el registro
compare_states() {
    if [ -f "$LOG_FILE" ]; then
        # Genera listas de archivos actuales y anteriores
        sort "$LOG_FILE" > /scripts/hash/sorted_previous.log
        sort "/scripts/hash/current_state.log" > /scripts/hash/sorted_current.log

        # Encuentra archivos nuevos o modificados
        comm -13 /scripts/hash/sorted_previous.log /scripts/hash/sorted_current.log | while IFS= read -r line; do
            hash=$(echo "$line" | cut -d ' ' -f1)
            file=$(echo "$line" | cut -d ' ' -f2-)
            echo "Archivo nuevo o modificado: $file"
            /scripts/add-data.sh "$file" || echo "Error al ejecutar add_data.sh con el archivo $file"
        done

        # Encuentra archivos eliminados
        comm -23 /scripts/hash/sorted_previous.log /scripts/hash/sorted_current.log | while read hash file; do
            echo "Archivo eliminado: $file"
        done

        # Encuentra archivos sin cambios
        #comm -12 /scripts/hash/sorted_previous.log /scripts/hash/sorted_current.log | while read hash file; do
        #echo "Archivo sin cambios: $file"
        #done
    else
        echo "No hay registro anterior. Asumiendo primera ejecución."
        # Lista todos los archivos como nuevos
        find "$MONITOR_DIR" -type f | while read file; do
            echo "Archivo nuevo: $file"
            /scripts/add-data.sh "$file" 2>&1
        done
    fi
}


# Función para actualizar el registro con el estado actual
update_log() {
  cp "/scripts/hash/current_state.log" "$LOG_FILE"
}

# Genera el estado actual de los archivos
generate_current_state

# Compara el estado actual con el registro
compare_states

# Ejecuta tus scripts adicionales aquí

# Actualiza el registro con el estado actual
update_log