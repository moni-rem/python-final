web: python manage.py migrate && python manage.py createsu && gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000}
