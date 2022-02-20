# Generated by Django 3.2 on 2022-02-19 20:19

import django.contrib.auth.models
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django_lifecycle.mixins
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.user')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False, editable=False)),
            ],
            options={
                'verbose_name': 'Company User',
                'verbose_name_plural': 'Company Users',
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, 'auth.user', models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='SpeedReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False, editable=False)),
                ('location_start', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('location_end', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('route', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
                ('speed_avg', models.PositiveIntegerField()),
                ('max_speed', models.PositiveIntegerField()),
                ('history', models.JSONField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='auth2.companyuser')),
            ],
            options={
                'verbose_name': 'Speed Report',
                'verbose_name_plural': 'Speed Reports',
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
        ),
    ]
