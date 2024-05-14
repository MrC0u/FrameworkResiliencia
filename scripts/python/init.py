from add_data import add_data
from check_db import check_db
import hashlib
import os

# Ruta del directorio a monitorear
MONITOR_DIR = "/data"

# Archivo de registro para almacenar el estado anterior
LOG_FILE = "/scripts/hash/file_state.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Función para generar el estado actual de los archivos
def generate_current_state():
    with open("/scripts/hash/current_state.log", "w") as current_state_file:
        for root, _, files in os.walk(MONITOR_DIR):
            for filename in files:
                filepath = os.path.join(root, filename)
                with open(filepath, "rb") as file:
                    file_hash = hashlib.sha256(file.read()).hexdigest()
                    current_state_file.write(f"{file_hash} {filepath}\n")

# Función para comparar el estado actual con el registro
def compare_states():
    if os.path.isfile(LOG_FILE):
        with open(LOG_FILE) as log_file:
            previous_state = set(line.strip() for line in log_file)
        with open("/scripts/hash/current_state.log") as current_state_file:
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

# Función para actualizar el registro con el estado actual
def update_log():
    os.system(f"cp /scripts/hash/current_state.log {LOG_FILE}")

generate_current_state()
compare_states()
update_log()
