# Generated manually for Client / ClientPublic tables

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_billinginvoice_invoice_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('client_id', models.AutoField(primary_key=True, serialize=False)),
                ('client_name', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone_number', models.CharField(blank=True, max_length=50)),
                ('client_company_name', models.CharField(blank=True, max_length=255)),
                ('address', models.TextField(blank=True)),
                ('date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'client',
                'ordering': ['client_id'],
            },
        ),
        migrations.CreateModel(
            name='ClientPublic',
            fields=[
                (
                    'client',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name='public_snapshot',
                        serialize=False,
                        to='users.client',
                    ),
                ),
                ('client_name', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone_number', models.CharField(blank=True, max_length=50)),
                ('client_company_name', models.CharField(blank=True, max_length=255)),
                ('address', models.TextField(blank=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('synced_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'client_public',
                'ordering': ['client'],
            },
        ),
    ]
