# Generated by Django 4.2.11 on 2024-05-09 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Connected_Users',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False, verbose_name='Email')),
                ('displayname', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]