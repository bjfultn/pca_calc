#!/bin/bash

cd /code

rm -rfv /code/static/*

/wait
/wait
/wait
sleep 2
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

python manage.py runserver 0.0.0.0:8008
