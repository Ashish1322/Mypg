# Generated by Django 3.2 on 2021-05-06 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pg', '0015_pg_recommended'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pg',
            name='recommended',
        ),
        migrations.CreateModel(
            name='recommended',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pg.pg')),
            ],
        ),
    ]
