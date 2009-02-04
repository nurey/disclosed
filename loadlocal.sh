#!/bin/bash
FILE=$1
KIND=$2
BULKLOAD=/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/bulkload_client.py

$BULKLOAD --filename $FILE \
--kind=$KIND --url http://localhost:8000/load \
--cookie='dev_appserver_login="samogon@gmail.com:True"'
