#!/bin/bash

PATH="/opt/dkrawler/db_backups/$(date +'%Y%m%d_%H%M')"
echo "Creating DB backup in $PATH"

/usr/bin/mongodump -d dkrawler -o $PATH