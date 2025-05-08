#!/bin/bash

cd /code

/wait
/wait
/wait
python manage.py makemigrations
python manage.py migrate

python manage.py runserver 0.0.0.0:$PORT
# gunicorn pca_calc.wsgi --workers=2
# gunicorn pca_calc.wsgi
