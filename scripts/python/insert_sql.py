import re
from db_sql import psql

# Función para extraer el nombre de la tabla del archivo SQL
def extraer_nombre_tabla(archivo):
    with open(archivo, 'r') as file:
        content = file.read()
    return re.findall(r'INSERT INTO (\w+)', content)[0]

# Función para extraer los nombres de las columnas
def extraer_columnas(archivo):
    with open(archivo, 'r') as file:
        for line in file:
            if 'INSERT INTO' in line:
                return re.search(r'\((.*?)\)', line).group(1)

# Función para extraer los datos
def extraer_datos(archivo):
    with open(archivo, 'r') as file:
        content = file.read()
    return re.findall(r'VALUES\s*\((.*?)\);', content, re.DOTALL)[0]

# Función para separar los datos
def separar_datos(datos):
    nuevos_datos = ""
    contador = 0
    for char in datos:
        if char == '(':
            contador += 1
        elif char == ')':
            contador -= 1
        if char == ',' and contador == 0:
            char = '|'
        nuevos_datos += char
    return nuevos_datos

# Función para seleccionar el tipo de dato
def seleccionar_tipo_dato(valor, columna):
    if valor.isdigit() or (valor.startswith('-') and valor[1:].isdigit()):
        if 'id' in columna.lower():
            return "SERIAL"
        else:
            return "INTEGER"
    elif re.match(r'^-?\d+\.\d+$', valor):
        return "FLOAT"
    elif re.search(r'point|multipoint|linestring|multilinestring|polygon|multipolygon|geometrycollection', valor, re.IGNORECASE):
        return "GEOMETRY"
    else:
        return "VARCHAR"

# Función para crear la sentencia CREATE TABLE
def crear_sentencia_create_table(tabla, archivo):
    columnas = extraer_columnas(archivo)
    #print(f'columnas: {columnas}')
    datos = extraer_datos(archivo)
    sentencia_create = f"CREATE TABLE IF NOT EXISTS {tabla} ("
    cols = columnas.split(',')
    #print(f'cols: {cols}')
    datos_sep = separar_datos(datos)
    #print(f'datos_sep: {datos_sep}')
    vals = datos_sep.split('|')
    #print(f'vals: {vals}')

    '''
    if len(cols) != len(vals):
        print("Error: El número de columnas y datos no coincide.")
        return None
    '''

    for i in range(len(cols)):
        col = cols[i].strip().replace('"','')
        val = vals[i].strip()
        nombre_columna = col.split(' ')[0]
        tipo_dato = seleccionar_tipo_dato(val, nombre_columna)
        sentencia_create += f"{nombre_columna} {tipo_dato}, "

    sentencia_create = sentencia_create.rstrip(', ')
    sentencia_create += ");"
    return sentencia_create



def insert_sql(archivo_sql):

    tabla = extraer_nombre_tabla(archivo_sql)
    #print(tabla)
    
    check_table_sentence = (f"SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{tabla}')")

    check_table = psql(check_table_sentence)

    if not check_table[0][0]:
        print(f"La tabla [{tabla}] no existe, creando tabla...")
        sentence = crear_sentencia_create_table(tabla, archivo_sql)
        print(f"Table: [{sentence}]")
        
        create_table = psql(sentence)
        if (create_table == 1):
            print(f'Table [{tabla}] creada con exito.')

        with open(archivo_sql, 'r') as sql_file:
            sql_commands = sql_file.read().split(');')  # Dividir los comandos
        for command in sql_commands:
            if command.strip():  # Ignorar líneas vacías
                psql(f'{command});')
        print(f"Datos cargados en tabla [{tabla}].")

    else:

        with open(archivo_sql, 'r') as sql_file:
            sql_commands = sql_file.read().split(');')  # Dividir los comandos
        for command in sql_commands:
            if command.strip():  # Ignorar líneas vacías
                psql(f'{command});')
        print(f"Datos cargados en tabla [{tabla}].")
