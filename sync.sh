#!/bin/bash
TEMP_FILE=$(mktemp)
curl https://goodarticlebot.toolforge.org/download -o $TEMP_FILE
mv $TEMP_FILE data.db 
echo $TEMP_FILE
rm $TEMP_FILE -f