#!/bin/bash
docker exec python_container sh -c 'python /scripts/python/init.py > /proc/1/fd/1 2> /proc/1/fd/2'