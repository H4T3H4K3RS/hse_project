
python manage.py loaddata -e contenttypes fixtures/default.json
python manage.py dumpdata --exclude=contenttypes --exclude=auth.Permission > fixtures/default.json