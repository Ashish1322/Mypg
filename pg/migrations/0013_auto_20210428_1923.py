# Generated by Django 3.1.5 on 2021-04-28 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pg', '0012_booking'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='zip',
            new_name='zip_code',
        ),
    ]
