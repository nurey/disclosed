#!/bin/bash

#FILE can be "all" or a specific file
FILE=$1
KIND=$2 # eg. Contract
SKIP_LINES=$3
#BULKLOAD=/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/bulkload_client.py
BULKLOAD=/usr/src/google_appengine/bulkload_client.py
URL=http://govtenders2.appspot.com/load

BATCH_SIZE=1 # how many rows to upload at a time
COOKIE="ACSID=AJKiYcEcQI1b_ay9nX4gimBhgg-xWnKzdvmyIc-2Jb4tgsVBuDG6wXDmSKu1fyvPpVcmFxBXBGy2nSUfJxG8E1dfHhlne-Yepb9csuMocgUt5J1g-soF9AYmLeSxoQ6ycRx7WJ3ii_ZfXUd9jikpB0CiLv4k2JG0LXAOdpI7BL0yrBMGKoHtvUFcb-OzA4QznkORrQhhaZzgAyr00g5z-ooLUBuaqIV93Iaa2iXW0klb4CxnUD8NPLuIAivNZJxf8vVZTPU394ar9EacN7IyTcWRwFEhiybOKlSjnLm833Vx4kxwT7g7KopNhn7QDzvPT7SbuJf9qh0xhdutDXMi715DaSNqwDgGw365nvX1qU27MN0pSHx9ay1FovPqolW60kDewDmgbASckw_D8ZBt3ULyHpMGDFkNfj_vaYRkPoWDa9SSKtASJN0"

function load_one {
    ONE=$1
    echo "loading $ONE"
    
    $BULKLOAD \
        --filename $ONE \
        --batch_size=$BATCH_SIZE \
		--skip_lines=$SKIP_LINES \
        --kind=$KIND \
        --url $URL \
        --cookie=$COOKIE

	##simulate success
	#yes --version > /dev/null
	##simulate failure
	#fail
	if [ $? -eq 0 ]; then
		echo "Successfully imported $i, moving to uploaded"
		mv $i scraper/csv/uploaded
	else
		echo "Failed to import $i"
	fi
}

if [ "$FILE" = "all" ]; then
    # load in order from oldest to newest
    for i in `ls -1tr scraper/csv/*.csv`; do
        load_one $i
    done
else
    load_one $FILE
fi
