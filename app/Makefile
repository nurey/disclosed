app.yaml: app.yaml.in .svn
	./app_yaml.py < app.yaml.in > app.yaml

newrelease: app.yaml make_release.sh django/.svn
	sh make_release.sh

release: goat/* index.yaml main.py settings.py urls.py loader.py make_release.sh django/.svn
	sh make_release.sh

update:
	appcfg.py update release
