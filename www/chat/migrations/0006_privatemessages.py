# Generated by Django 4.2.11 on 2024-05-13 07:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_alter_user_displayname'),
        ('chat', '0005_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('displayname', models.CharField(max_length=50)),
                ('emailfrom', models.EmailField(max_length=254)),
                ('displaynamefrom', models.CharField(max_length=50)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('room_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.chatrooms')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.user')),
            ],
        ),
    ]
