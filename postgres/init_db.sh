#!/bin/sh

export PGPASSWORD=${POSTGRES_PASSWORD}

psql -c "DROP DATABASE $POSTGRES_DB"
psql -c "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER"

psql -c "CREATE ROLE $DB_ROLE;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $DB_ROLE"

# create a read-only user
# Create a group
psql -c "CREATE ROLE readaccess;"

# Grant access to existing tables
psql -c "GRANT USAGE ON SCHEMA public TO readaccess;"
psql -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO readaccess;"

# Grant access to future tables
psql -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readaccess;"

# Create a final user with password
psql -c "CREATE USER readonly WITH PASSWORD '${POSTGRES_PASSWORD}';"
psql -c "GRANT readaccess TO readonly;"
