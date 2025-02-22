# Generated by Django 4.2.4 on 2024-01-23 16:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0015_faq_alter_session_date_added'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivacyPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='TermsAndConditons',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='session',
            name='mood',
            field=models.CharField(choices=[('Calm', 'Calm'), ('Happy', 'Happy'), ('Excited', 'Excited'), ('Grateful', 'Grateful'), ('Angry', 'Angry'), ('Sad', 'Sad'), ('Confused', 'Confused'), ('Tired', 'Tired'), ('Neutral', 'Neutral')], default='Neutral', max_length=20),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer',
            field=models.TextField(),
        ),
        migrations.CreateModel(
            name='UserMood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mood', models.CharField(choices=[('Calm', 'Calm'), ('Happy', 'Happy'), ('Excited', 'Excited'), ('Grateful', 'Grateful'), ('Angry', 'Angry'), ('Sad', 'Sad'), ('Confused', 'Confused'), ('Tired', 'Tired'), ('Neutral', 'Neutral')], default='Neutral', max_length=20)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
