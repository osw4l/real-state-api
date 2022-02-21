from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.auth2.models import CompanyUser
from apps.main.models import Property
from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = 'Create Data Automatically'

    def handle(self, *args, **kwargs):
        self.create_admin_user()
        self.create_company_user()
        self.create_properties()

    def warning_message(self, message):
        self.stdout.write(self.style.WARNING(message))

    def success_message(self, message):
        self.stdout.write(self.style.SUCCESS(message))

    def info_message(self, message):
        self.stdout.write(self.style.MIGRATE_HEADING(message))

    def create_admin_user(self):
        self.info_message('Creating Django User')
        username = 'admin'
        password = '123'

        user, created = User.objects.get_or_create({
            'username': username,
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        })
        if created:
            user.set_password(password)
            user.save()
            self.success_message('Django User created successfully')
        else:
            self.warning_message('Creation skipped, superuser already exists')

    def create_company_user(self):
        self.info_message('Creating Company User')
        username = 'test'
        password = '123'
        user, created = CompanyUser.objects.get_or_create({
            'username': username,
            'first_name': 'oswaldo',
            'last_name': 'rodriguez',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        })
        if created:
            user.set_password(password)
            user.save()
            self.success_message('Company User created successfully')
        else:
            self.warning_message('Creation skipped, user already exists')

    def create_properties(self):
        self.info_message('Creating Properties')
        if Property.objects.values_list('id', flat=True).count() == 0:
            properties = [
                {
                    'location': Point(-74.032578, 4.768804),
                    'address': 'Cra 11A # 191A - 52'
                },
                {
                    'location': Point(-74.032705, 4.725755),
                    'address': 'Str 147 # 9 - 60'
                },
                {
                    'location': Point(-74.052030, 4.693724),
                    'address': 'Str 106A # 19A - 37'
                },
            ]

            properties_insert = []
            for p in properties:
                properties_insert.append(Property(**p))

            Property.objects.bulk_create(properties_insert)
            self.success_message('The properties were successfully created')
        else:
            self.warning_message('Properties already exist, the command only works when none exist')

