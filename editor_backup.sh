#!/bin/bash

B="$BACKUP_NAME-`date +%y%m%d%H%M`"
mkdir -p /opt/local-backup/$B
cd /opt/local-backup/$B
cp -rp /data/* .
tar cvfz $BACKUP_FILE .