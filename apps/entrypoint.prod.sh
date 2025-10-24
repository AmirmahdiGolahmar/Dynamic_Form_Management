#!/bin/bash
echo "Waiting for database..."
while ! nc -z db 5432; do
    sleep 0.1
done
echo "Database ready!"

python manage.py collectstatic --noinput
python manage.py migrate
gunicorn core.wsgi:application --bind 0.0.0.0:8000
