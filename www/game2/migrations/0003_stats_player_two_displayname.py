# Generated by Django 4.2.13 on 2024-06-12 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game2', '0002_stats_player_one_win_stats_player_two_win'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='player_two_displayname',
            field=models.CharField(default='', max_length=50),
        ),
    ]