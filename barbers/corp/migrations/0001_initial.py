# Generated by Django 5.0.3 on 2024-04-26 17:37

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_code', models.IntegerField(blank=True, default=0)),
                ('data', models.DateTimeField(blank=True)),
            ],
            options={
                'db_table': 'appointment',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Barbershop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(blank=True, null=True)),
                ('city', models.CharField(blank=True, null=True)),
                ('street', models.CharField(blank=True, null=True)),
                ('house', models.CharField(blank=True, null=True)),
                ('postal_code', models.IntegerField(blank=True, null=True, unique=True)),
                ('phone', models.BigIntegerField(blank=True, null=True, unique=True)),
                ('mail', models.CharField(unique=True)),
            ],
            options={
                'db_table': 'barbershop',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField()),
                ('surname', models.CharField()),
                ('phone', models.BigIntegerField()),
                ('mail', models.CharField(blank=True, null=True, unique=True, validators=[django.core.validators.EmailValidator()])),
            ],
            options={
                'db_table': 'client',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField()),
                ('surname', models.CharField()),
                ('patronymic', models.CharField(blank=True, null=True)),
                ('phone', models.BigIntegerField(unique=True)),
                ('mail', models.CharField(unique=True)),
            ],
            options={
                'db_table': 'staff',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MasterService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'master_service',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(unique=True)),
                ('has_accept_appointments', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'position',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField()),
                ('name', models.CharField()),
                ('description', models.CharField(blank=True, null=True)),
            ],
            options={
                'db_table': 'service',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('staff', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='corp.staff')),
                ('passport', models.BigIntegerField(unique=True)),
                ('employment_record_number', models.BigIntegerField(unique=True)),
                ('snils', models.BigIntegerField(unique=True)),
            ],
            options={
                'db_table': 'documents',
                'managed': False,
            },
        ),
    ]
