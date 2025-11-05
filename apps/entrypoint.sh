#!/bin/sh
# entrypoint.sh
set -e


echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database ready!"

echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis ready!"


echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate --noinput

echo "Starting Django API server..."
exec python manage.py runserver 0.0.0.0:8000

