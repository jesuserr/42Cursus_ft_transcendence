# Generated by Django 4.2.13 on 2024-07-10 13:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game3', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='left_player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game3_stats', to=settings.AUTH_USER_MODEL),
        ),
    ]