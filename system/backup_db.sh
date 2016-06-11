#!/bin/bash

PATH="/data/db_backups/$(date +'%Y%m%d_%H%M')"
echo "Creating DB backup in $PATH"

/usr/bin/mongodump -d dionysus -o $PATH