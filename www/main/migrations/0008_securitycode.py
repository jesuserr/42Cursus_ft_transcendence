# Generated by Django 4.2.11 on 2024-04-25 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_user_avatar'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityCode',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=10)),
            ],
        ),
    ]