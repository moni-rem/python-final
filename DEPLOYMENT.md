# Deployment Notes

## Environment variables

Set these on your hosting provider:

```text
SECRET_KEY=change-this-to-a-long-random-secret
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
CORS_ALLOW_ALL_ORIGINS=False
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DB_NAME
DB_SSL_REQUIRE=True
REQUIRE_DATABASE_URL=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

`DATABASE_URL` should point to your hosted PostgreSQL database. If it is not set,
the app can also use `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.
Set `REQUIRE_DATABASE_URL=True` on production if you want the app to fail clearly
when the hosted database is missing instead of falling back to local SQLite.

If login fails with a CSRF error, make sure `CSRF_TRUSTED_ORIGINS` contains the
full deployed origin, for example `https://your-app.onrender.com`. If your host
terminates HTTPS before Django and session cookies are not being saved, confirm
it forwards `X-Forwarded-Proto: https`; otherwise temporarily set
`SESSION_COOKIE_SECURE=False` and `CSRF_COOKIE_SECURE=False` while debugging.

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

For existing local SQLite data, export it before switching production databases:

```bash
python manage.py dumpdata --exclude contenttypes --exclude auth.permission --indent 2 > data.json
```

After setting `DATABASE_URL` on the deployed app and running migrations, import it:

```bash
python manage.py loaddata data.json
```
