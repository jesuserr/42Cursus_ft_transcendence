# Generated by Django 4.2.13 on 2024-06-25 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0003_tournament_round'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament_list',
            name='status',
            field=models.CharField(default='PENDING', max_length=50),
        ),
    ]
