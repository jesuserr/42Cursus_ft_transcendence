from django.contrib import admin
from .models import User, SecurityCode

admin.site.register(User)
admin.site.register(SecurityCode)