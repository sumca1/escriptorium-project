#!/bin/sh

# Create logs directory if it doesn't exist
mkdir -p /usr/src/app/escriptorium/logs

echo "Waiting for postgres..."
while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

# Compile messages and remove duplicates
echo "Compiling translation messages..."
python manage.py compilemessages -l he -l fr
echo "Deduplicating PO files..."
python manage.py dedupe_po_messages --inplace --backup

python manage.py collectstatic --no-input
python manage.py migrate
exec "$@"
