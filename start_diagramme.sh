#!/bin/bash

if [[ "$(ps -N -p $$ -o comm,pid)" =~ $'\n'"${0##*/}"[[:space:]] ]]; then
    echo "aready running!"
    exit 1
fi
/home/danst/Wetterstation/wetterstation.py --diagramme
