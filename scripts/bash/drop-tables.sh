#!/bin/bash
source .env

PGPASSWORD=$POSTGRES_PASSWORD psql -h $HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $PORT -f ./data/topology/clear-data.sql