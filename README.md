
python manage.py loaddata -e contenttypes fixtures/default.json

python manage.py dumpdata --exclude=contenttypes --exclude=auth.Permission > fixtures/default.json

web python manage.py runserver 0.0.0.0:$PORT

web python app/bot.py