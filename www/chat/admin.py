from django.contrib import admin
from .models import Connected_Users, ChatRooms, Blocked_Users, Messages, PrivateMessages

admin.site.register(Connected_Users)
admin.site.register(ChatRooms)
admin.site.register(Blocked_Users)
admin.site.register(Messages)
admin.site.register(PrivateMessages)

