from django.contrib import admin
from .models import Tournament_List, Tournament_Connected_Users, Tournament_Play, Tournament_Round

admin.site.register(Tournament_List)
admin.site.register(Tournament_Connected_Users)
admin.site.register(Tournament_Play)
admin.site.register(Tournament_Round)
