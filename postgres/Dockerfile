FROM postgres:14-alpine3.14

COPY ./init_db.sh /docker-entrypoint-initdb.d/01-db-setup.sh
COPY ./give_access.sh /docker-entrypoint-initdb.d/02-db-access.sh