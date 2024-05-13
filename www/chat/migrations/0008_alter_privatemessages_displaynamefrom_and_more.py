# Generated by Django 4.2.11 on 2024-05-13 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0007_remove_privatemessages_displayname_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privatemessages',
            name='displaynamefrom',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='privatemessages',
            name='displaynameto',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='privatemessages',
            name='emailfrom',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='privatemessages',
            name='emailto',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='privatemessages',
            name='message',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='privatemessages',
            name='private_room_name',
            field=models.CharField(max_length=500, unique=True),
        ),
    ]