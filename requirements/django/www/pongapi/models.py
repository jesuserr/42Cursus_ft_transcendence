from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
import uuid


class UserManager(BaseUserManager):
    def get_by_natural_key(self, email):
        return self.get(email=email)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name = "Email", unique=True)
    password = models.CharField(max_length=500, verbose_name = "Password")
    displayname = models.CharField(max_length=50, verbose_name = "Display Name", unique=True)
    avatar = models.ImageField(verbose_name= "Avatar", blank=True, upload_to = 'static/avatars/',)
    tokenid = models.CharField(max_length=5000, blank=True)
    fourtytwo = models.BooleanField(default=False)
    tfa = models.BooleanField(default=False, verbose_name = "Two Factor Authentication")
    USER_TYPE_CHOICES = (
        (1, 'EMAIL'),
        (2, 'SMS'),
        (3, 'APP'),
    )
    tfa_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=1)
    phone_number = models.CharField(max_length=15, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    totp_secret = models.CharField(max_length=200, blank=True)
    objects = UserManager()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return self.email
    
        
class SecurityCode(models.Model):
    email = models.EmailField(primary_key=True)
    code = models.CharField(max_length=10)

    
  
