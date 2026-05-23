import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create or update an admin user from DJANGO_SUPERUSER_* environment variables.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            raise CommandError(
                'Set DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD.'
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
                'role': 'admin',
            },
        )

        fields_to_update = []
        if user.email != email:
            user.email = email
            fields_to_update.append('email')
        if not user.is_staff:
            user.is_staff = True
            fields_to_update.append('is_staff')
        if not user.is_superuser:
            user.is_superuser = True
            fields_to_update.append('is_superuser')
        if getattr(user, 'role', None) != 'admin':
            user.role = 'admin'
            fields_to_update.append('role')

        user.set_password(password)
        fields_to_update.append('password')
        user.save(update_fields=fields_to_update)

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} admin user: {username}'))
