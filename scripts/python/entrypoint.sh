#!/bin/sh
current_pip_version=$(pip --version | awk '{print $2}')
desired_pip_version="24.0"

# Comparar y actualizar la version de pip
if [ "$current_pip_version" != "$desired_pip_version" ]; then
    pip install --upgrade pip==$desired_pip_version
fi

pip install -r /scripts/python/requirements.txt
python /scripts/python/init.py &

# Mantener el contenedor abierto
while true; do
  sleep 1
done
