# Generated by Django 4.2.4 on 2023-12-30 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0012_remove_event_notified_completedtaskcount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='completedtaskcount',
            name='numberOfTasks',
            field=models.IntegerField(default=0),
        ),
    ]
