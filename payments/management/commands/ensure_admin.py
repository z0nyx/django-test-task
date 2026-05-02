import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


TRUE_VALUES = {"1", "true", "yes", "on"}


class Command(BaseCommand):
    help = "Creates or updates admin user from environment"

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        reset_password = os.environ.get("DJANGO_SUPERUSER_RESET_PASSWORD", "").lower() in TRUE_VALUES

        if not username or not email or not password:
            self.stdout.write("Admin user environment variables are not fully set")
            return

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created or reset_password:
            user.set_password(password)

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write("Admin user is ready")
