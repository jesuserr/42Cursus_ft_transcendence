# Generated by Django 4.2.14 on 2024-07-19 14:48

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityCode',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('password', models.CharField(max_length=500, verbose_name='Password')),
                ('displayname', models.CharField(max_length=50, unique=True, verbose_name='Display Name')),
                ('avatar', models.ImageField(blank=True, upload_to='static/avatars/', verbose_name='Avatar')),
                ('tokenid', models.CharField(blank=True, max_length=5000)),
                ('fourtytwo', models.BooleanField(default=False)),
                ('tfa', models.BooleanField(default=False, verbose_name='Two Factor Authentication')),
                ('tfa_type', models.IntegerField(choices=[(1, 'EMAIL'), (2, 'SMS'), (3, 'APP')], default=1)),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('totp_secret', models.CharField(blank=True, max_length=200)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]