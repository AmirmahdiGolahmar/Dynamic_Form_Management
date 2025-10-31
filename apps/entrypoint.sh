#!/bin/sh
# entrypoint.sh
set -e

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate --noinput

echo "Starting Django API server..."
exec python manage.py runserver 0.0.0.0:8000

