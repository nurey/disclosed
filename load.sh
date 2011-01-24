#!/bin/bash

#FILE can be "all" or a specific file
FILE=$1
KIND=$2 # eg. Contract

function load_one {
    ONE=$1
    echo "loading $ONE"
    
    appcfg.py upload_data \
        --config_file=app2/contract_loader.py \
        --filename="$ONE" \
        --kind=$KIND \
        app2

	##simulate success
	#yes --version > /dev/null
	##simulate failure
	#fail
	if [ $? -eq 0 ]; then
		echo "Successfully imported $i, moving to uploaded"
        #mv $i scraper/data/uploaded
	else
		echo "Failed to import $i"
	fi
}

if [ "$FILE" = "all" ]; then
    # load in order from oldest to newest
    for i in `ls -1tr scraper/data/*.csv`; do
        load_one $i
    done
else
    load_one $FILE
fi
