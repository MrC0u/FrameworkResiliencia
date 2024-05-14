#!/usr/bin/env bash
source .env

# Nombre del archivo SQL
archivo_sql="$1"

# Función para extraer el nombre de la tabla del archivo SQL
extraer_nombre_tabla() {
    grep -oE 'INSERT INTO \w+' "$1" | sed 's/INSERT INTO //g' | sort -u
}

# Función para extraer los nombres de las columnas
extraer_columnas() {
    sed -n -e '/INSERT INTO/ {s/.*(\(.*\)).*/\1/p; q;}' "$1"
}

extraer_datos() {
    awk -F, 'BEGIN { RS="),"; FS="," } NR==1 { print $0")" }' "$1" | sed 's/.*VALUES//' | sed 's/^[[:space:]]*//' | sed 's/^(\(.*\))$/\1/' | sed 's/^(\(.*\));$/\1/'
}

separar_datos(){
    local nuevos_datos=""
    local contador=0
    while IFS= read -r -n1 char; do
        if [[ $char == "(" ]]; then
            ((contador++))
        elif [[ $char == ")" ]]; then
            ((contador--))
        fi

        if [[ $char == "," && contador -eq 0 ]]; then
            char="|"
        fi
        nuevos_datos+="$char"
    done <<< "$1"

    echo "$nuevos_datos"
}

seleccionar_tipo_dato() {
    local valor=$1
    local columna=$2
    local tipo_dato

    # Comprueba si el valor es un número entero y si tipo ID
    if [[ $valor =~ ^-?[0-9]+$ ]]; then
        if echo "$columna" | tr '[:upper:]' '[:lower:]' | grep -iq 'id'; then 
            tipo_dato="SERIAL"
        else
            tipo_dato="INTEGER"
        fi

    # Comprueba si el valor es un número de punto flotante
    elif [[ $valor =~ ^-?[0-9]+\.[0-9]+$ ]]; then
        tipo_dato="FLOAT"

    # Si no es ni entero ni flotante, asume que es un string
    else
        # Convierte el valor a minúsculas y comprueba si coincide con tipos geométricos
        if echo "$valor" | tr '[:upper:]' '[:lower:]' | grep -Eiwq 'point|multipoint|linestring|multilinestring|polygon|multipolygon|geometrycollection'; then 
            tipo_dato="GEOMETRY"
        else
            tipo_dato="VARCHAR"
        fi
    fi

    # Imprime el tipo de dato
    echo $tipo_dato
}

# Función para crear la sentencia CREATE TABLE
crear_sentencia_create_table() {
    local tabla=$1
    local columnas=$(extraer_columnas "$archivo_sql")
    local datos=$(extraer_datos "$archivo_sql")
    local sentencia_create="CREATE TABLE IF NOT EXISTS $tabla ("
    echo "columnas: [$columnas]" >&2
    echo "datos: [$datos]" >&2
    echo "------ o ------" >&2

    # Convertir las cadenas de columnas y datos en arrays
    IFS=',' read -ra cols <<< "$columnas"

    datos_sep=$(separar_datos "$datos")
    echo "datos sep: [$datos_sep]" >&2
    IFS='|' read -ra vals <<< "$datos_sep"


    # Asegurarse de que ambos arrays tienen la misma longitud
    if [ "${#cols[@]}" -ne "${#vals[@]}" ]; then
        echo "Error: El número de columnas y datos no coincide." >&2
        return 1
    fi

    # Iterar sobre los arrays
    for ((i=0; i<${#cols[@]}; i++)); do
        # Elimina espacios en blanco y divide en nombre y tipo
        col=$(echo "${cols[i]}" | xargs)
        val=$(echo "${vals[i]}" | xargs)
        echo "Columna [$col] - Dato [$val]" >&2
        nombre_columna=$(echo $col | cut -d ' ' -f 1)
        tipo_dato=$(seleccionar_tipo_dato "$val" 2>&1)
        echo "Tipo: [$tipo_dato]" >&2
        
        # Construir la sentencia CREATE TABLE
        sentencia_create+="$nombre_columna $tipo_dato, "
        
        # Aquí puedes hacer algo con valor_dato si es necesario
    done

    # Elimina la última coma y cierra la sentencia
    sentencia_create=${sentencia_create%, }
    sentencia_create+=");"

    echo "$sentencia_create"
}


# Intenta ejecutar el archivo SQL
tabla=$(extraer_nombre_tabla "$archivo_sql")
check=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h postgis -U $POSTGRES_USER -d $POSTGRES_DB -p $PORT -c "SELECT EXISTS (
   SELECT 1
   FROM pg_tables
   WHERE schemaname = 'public'
   AND tablename = '$tabla'
);")

#echo "Respuesta: [$check]"

if echo "$check" | grep -iqw "exists"; then
    echo "La tabla [$tabla] no existe, creando tabla..."
    sentencia=$(crear_sentencia_create_table "$tabla")
    echo "Table: [$sentencia]"
    PGPASSWORD=$POSTGRES_PASSWORD psql -h postgis -U $POSTGRES_USER -d $POSTGRES_DB -p $PORT -c "$sentencia"
    PGPASSWORD=$POSTGRES_PASSWORD psql -h postgis -U $POSTGRES_USER -d $POSTGRES_DB -p $PORT -f "$archivo_sql"
    echo "Datos cargados en tabla [$tabla]."
else
    output=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h postgis -U $POSTGRES_USER -d $POSTGRES_DB -p $PORT -f "$archivo_sql" 2>&1)
    echo "Datos cargados en tabla [$tabla]."
    
fi

