import os

from django.core.management.base import BaseCommand

from accounts.models import User, VolunteerProfile


class Command(BaseCommand):
    help = 'Create or reset the default admin account'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default=os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@zanchangemakers.co.tz'),
        )
        parser.add_argument(
            '--password',
            default=os.environ.get('DEFAULT_ADMIN_PASSWORD', 'Admin@Zcm2026'),
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset password if the admin account already exists',
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'Admin',
                'last_name': 'Zanchangemakers',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'accepted_terms': True,
                'accepted_privacy_policy': True,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            VolunteerProfile.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created admin: {email}'))
        elif options['reset']:
            user.role = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Reset admin password: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin already exists: {email} (use --reset to update password)'))
