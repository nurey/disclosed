#!/bin/bash

#FILE can be "all" or a specific file
FILE=$1
KIND=$2 # eg. Contract
BULKLOAD=/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/bulkload_client.py
URL=http://govtenders-aep.appspot.com/load

BATCH_SIZE=3 # how many rows to upload at a time
COOKIE="ACSID=AJKiYcENlwBHzAH-C_563hxQOTdrk_X_Y4pryiyqdkXX9Kcb3wq1L_os1OAYkT8UeO9Y-MhJ4pgRSh252RhEh5Qe0v0QkfD-s8MkUz9HMldy2clJWdxblikDnxdN8fPFh8ftuXh7uSrgEESVIUVAvGOQy_jR5YRcXE6tSNWa0KQmwEaytk-EjSfro7Ch-SidKIHjJ9jxoPr-PrVZd2l6mQdDtyt5r-reZLfDPqBONWbOpQaEmMrp_y6G8HS62mMBME1wUdk29hMLRcJ-HNdxhJAhUCm9ozOpOYD8ZtKn3EyXFopBKJ3MC2-DPo71Io37XfKNMVQxVG8I3RNKirE43WFeTar65068cFvBNs28r69x6dkhCW3dIYk1lWEZxSJUULgh1dUMl9E3atPWgEshlX5Tl64MiIpqyw"

function load_one {
    ONE=$1
    echo "loading $ONE"
    
    $BULKLOAD \
        --filename $ONE \
        --batch_size=$BATCH_SIZE \
        --kind=$KIND \
        --url $URL \
        --cookie=$COOKIE
}

if [ "$FILE" = "all" ]; then
    # load in order from oldest to newest
    for i in `ls -1tr scraper/csv/*.csv`; do
        load_one $i
    done
else
    load_one $FILE
fi
