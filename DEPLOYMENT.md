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
SERVE_MEDIA_FILES=True
MEDIA_ROOT=/opt/render/project/src/media
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@gmail.com
DJANGO_SUPERUSER_PASSWORD=change-this-admin-password
```

`DATABASE_URL` should point to your hosted PostgreSQL database. If it is not set,
the app can also use `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.
Set `REQUIRE_DATABASE_URL=True` on production if you want the app to fail clearly
when the hosted database is missing instead of falling back to local SQLite.

`SERVE_MEDIA_FILES=True` lets the deployed Django app serve uploaded course
images, videos, and PDFs from `/media/`. This is fine for demos and class
projects. For a real production deployment, use persistent storage such as S3,
Cloudinary, or your host's mounted disk; otherwise uploaded files can disappear
when the service is redeployed or restarted.

If your hosting provider supports persistent disks, mount the disk to a folder
and set `MEDIA_ROOT` to that exact folder. On Render, for example, create a
persistent disk and use its mount path as `MEDIA_ROOT`.

For Render, Railway, and Vercel-style deployments, the app now also reads
`RENDER_EXTERNAL_HOSTNAME`, `RAILWAY_PUBLIC_DOMAIN`, and `VERCEL_URL` into
`ALLOWED_HOSTS` automatically. You can still set `ALLOWED_HOSTS` and
`CSRF_TRUSTED_ORIGINS` yourself for custom domains.

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

If the home page shows "No featured courses yet", the hosted database is empty.
Create courses from the admin/instructor pages, import your local data, or seed
starter content:

```bash
python manage.py seed_demo_data
```

The seed command creates a demo instructor named `demo_instructor`. Change its
password in the admin before using it on a public site.

## Start command

```bash
python manage.py migrate && python manage.py createsu && gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000}
```

The explicit bind matters on hosts that provide the web port through the
`PORT` environment variable.

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
