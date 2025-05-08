rm -v db/migrations/00*.py

# To stop the postgres server run
pg_ctl -D jump-database stop

# Initialize databse
initdb -D jump-database # initialize database, will create a jump-database directory
pg_ctl -D jump-database -l logfile start # start the postgres server

# Drop the database & recreate
psql postgres -c "drop database jump_development;"
psql postgres -c "create database jump_development;"
