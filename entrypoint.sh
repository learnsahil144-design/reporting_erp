#!/bin/sh

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn media_reporting.wsgi:application \
    --bind 0.0.0.0:8900 \
    --workers 3