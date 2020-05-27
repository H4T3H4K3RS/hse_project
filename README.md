
python manage.py loaddata -e contenttypes fixtures/default.json To dump fixture execute:

python manage.py dumpdata --exclude=contenttypes --exclude=auth.Permission > fixtures/default.json