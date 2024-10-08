# Generated by Django 4.2.14 on 2024-07-19 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Friends_Connected_Users',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('displayname', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Friends_List',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('displayname', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]
