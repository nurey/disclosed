verify:
	for i in csv/*.csv; do ./verify_csv.pl < "$${i}"; done
count:
	find csv/ -name *.csv -exec wc -l {} \; |grep -v uploaded

clean-empty:
	find csv/ -empty -name *.csv -exec rm {} \;
