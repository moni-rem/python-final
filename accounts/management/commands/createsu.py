import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create a superuser from DJANGO_SUPERUSER_* environment variables.'

    def handle(self, *args, **kwargs):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', '')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            raise CommandError(
                'Set DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD.'
            )

        User = get_user_model()

        if not User.objects.filter(username=username).exists():
            extra_fields = {}
            if any(field.name == 'role' for field in User._meta.fields):
                extra_fields['role'] = 'admin'

            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                **extra_fields,
            )
            self.stdout.write(self.style.SUCCESS('Superuser created'))
        else:
            self.stdout.write('Superuser already exists')
