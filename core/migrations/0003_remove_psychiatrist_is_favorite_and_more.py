# Generated by Django 4.2.4 on 2023-12-24 06:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_session_segments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='psychiatrist',
            name='is_favorite',
        ),
        migrations.RemoveField(
            model_name='session',
            name='is_favorite',
        ),
        migrations.RemoveField(
            model_name='sessionpart',
            name='is_favorite',
        ),
    ]
