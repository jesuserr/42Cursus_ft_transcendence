# Generated by Django 4.2.13 on 2024-05-28 14:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_user_groups_user_is_superuser_user_last_login_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_superuser',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_permissions',
        ),
    ]
