# Deployment Notes

## Environment variables

Set these on your hosting provider:

```text
SECRET_KEY=change-this-to-a-long-random-secret
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
CORS_ALLOW_ALL_ORIGINS=False
```

## Build command

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

## Start command

```bash
gunicorn core.wsgi:application
```

## Important

SQLite is fine for demos, but for a real hosted site use your provider's PostgreSQL/MySQL database and update `DATABASES` before going live with real users.
