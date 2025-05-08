# rm -v db/migrations/00*.py

brew services stop postgresql
brew services start postgresql
sleep 2

psql postgres -c "drop database jump_development;"
psql postgres -c "create database jump_development;"

python manage.py makemigrations
python manage.py migrate
