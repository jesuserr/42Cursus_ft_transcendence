from django.urls import re_path

from chat import consumers
from game import gameconsumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
	re_path(r"ws/game/(?P<game_name>\w+)/$", gameconsumers.ChatConsumer.as_asgi()),
]