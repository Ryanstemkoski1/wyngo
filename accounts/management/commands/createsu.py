from os import getenv
from accounts.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a superuser without prompt.'

    def handle(self, *args, **options):
        super_email = getenv('SUPERUSER_EMAIL', default='admin@mail.com')
        super_pass = getenv('SUPERUSER_PASSWORD', default='complexpassword123')

        if not User.objects.filter(email=super_email).exists():
            User.objects.create_superuser(
                email=super_email,
                password=super_pass
            )
            print('Superuser has been created.')