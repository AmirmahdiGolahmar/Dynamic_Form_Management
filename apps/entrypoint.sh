#!/bin/sh
# exit on error
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Django API server..."
exec python manage.py runserver 0.0.0.0:8000
