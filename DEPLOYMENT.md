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
```

`DATABASE_URL` should point to your hosted PostgreSQL database. If it is not set,
the app falls back to the local `db.sqlite3` file, which is not reliable on most
deployment platforms because the filesystem may be rebuilt or reset.

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
