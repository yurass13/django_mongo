#!/bin/sh

echo "Waiting for DB..."

while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
  sleep 0.1
done

echo "Mongo started"

# Wipe data for changed models on each restart
python manage.py flush --no-input
python manage.py makemigrations custom_forms
python manage.py makemigrations
python manage.py migrate

exec "$@"