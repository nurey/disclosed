verify:
	for i in $$GOAT_HOME/data/*.csv; do ./verify_csv.pl < "$${i}"; done
count:
	find csv/ -name *.csv -exec wc -l {} \; |grep -v uploaded

uniq:
	for i in csv/*.csv; do uniq "$${i}" $${i}.uniq; done
