from add_data import add_data
from check_db import check_db
import hashlib
import os

# Ruta del directorio a monitorear
MONITOR_DIR = "/data"

# Archivos de registro
LAST_HASH = "/scripts/hash/file_state.log"
CURRENT_HASH = "/scripts/hash/current_state.log"

os.makedirs(os.path.dirname(LAST_HASH), exist_ok=True)

# Actualizar el registro
def update_log():
    os.system(f"cp {CURRENT_HASH} {LAST_HASH}")

# Generar el estado actual de los archivos
def generate_current_state():
    with open(CURRENT_HASH, "w") as current_state_file:
        for root, _, files in os.walk(MONITOR_DIR):
            for filename in files:
                filepath = os.path.join(root, filename)
                with open(filepath, "rb") as file:
                    # Temporalmente deshabilitado -- Verificar si los archivos han cambiado (en archivos pesados puede tomar mucho)
                    # file_hash = hashlib.md5(file.read()).hexdigest()
                    file_hash = 0
                    current_state_file.write(f"{file_hash} {filepath}\n")

# Comparar el estado actual con el registro
def compare_states():
    print(f'Buscando archivos nuevos en carpeta /data/.')
    if os.path.isfile(LAST_HASH):
        with open(LAST_HASH) as last_hash:
            previous_state = set(line.strip() for line in last_hash)
        with open(CURRENT_HASH) as current_state_file:
            current_state = set(line.strip() for line in current_state_file)

        # Encuentra archivos nuevos o modificados
        new_or_modified_files = current_state - previous_state
        for line in new_or_modified_files:
            file_hash, file_path = line.split(" ", 1)
            print(f"Archivo nuevo o modificado: {file_path}")
            add_data(file_path)

        # Encuentra archivos eliminados
        deleted_files = previous_state - current_state
        for line in deleted_files:
            _, file_path = line.split(" ", 1)
            print(f"Archivo eliminado: {file_path}")
    else:
        print("No hay registro anterior. Asumiendo primera ejecución.")
        # Lista todos los archivos como nuevos
        for root, _, files in os.walk(MONITOR_DIR):
            for filename in files:
                filepath = os.path.join(root, filename)
                print(f"Archivo nuevo: {filepath}")
                add_data(filepath)

check_db()
generate_current_state()
compare_states()
update_log()

print (f'Busqueda de data finalizada.')