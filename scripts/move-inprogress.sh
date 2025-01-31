#!/bin/bash

for NR in $(find ./inprogress -type d -maxdepth 1 | sed -e 's|./inprogress/md||')
do
	echo "RECORD[$NR]"
	cp ./inprogress/md${NR}/metadata/record.cmdi ./record-${NR}.xml
done
