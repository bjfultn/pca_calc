#!/bin/sh

export PGPASSWORD=${POSTGRES_PASSWORD}

# Grant access to existing tables
psql -c "GRANT USAGE ON SCHEMA public TO readaccess;"
psql -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO readaccess;"
