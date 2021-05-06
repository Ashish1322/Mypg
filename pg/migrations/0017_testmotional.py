# Generated by Django 3.2 on 2021-05-06 12:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pg', '0016_auto_20210506_1648'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testmotional',
            fields=[
                ('sno', models.AutoField(primary_key=True, serialize=False)),
                ('test', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
