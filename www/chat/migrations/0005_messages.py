# Generated by Django 4.2.11 on 2024-05-10 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_blocked_users'),
    ]

    operations = [
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('displayname', models.CharField(max_length=50)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('room_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.chatrooms')),
            ],
        ),
    ]
