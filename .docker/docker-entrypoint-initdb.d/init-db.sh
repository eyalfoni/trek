#!/bin/bash
set -e

psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
psql -U postgres -c "DROP ROLE IF EXISTS $DB_USER;"
psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
psql -U postgres -c "ALTER USER $DB_USER WITH SUPERUSER;"
psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to $DB_USER;"

if [ -f "/tmp/dump.sql" ]; then
	pg_restore -U $DB_USER -d $DB_NAME  /tmp/dump.sql
fi