web: python manage.py migrate && python manage.py seed_demo_data && gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000}
