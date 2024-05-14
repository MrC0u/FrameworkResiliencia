#!/usr/local/bin/bash

add_data(){
    if echo "$1" | grep -qE "\.sql$"; then
        #echo "Detectado archivo [.sql]" >&2    
        /scripts/insert-sql.sh "$1" 2>&1
    elif if echo "$1" | grep -qE "\.shp$"; then
        /scripts/insert-shp.sh "$1" 2>&1
    fi
}

add_data "$1"
