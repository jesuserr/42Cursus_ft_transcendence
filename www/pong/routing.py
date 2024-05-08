from django.urls import re_path

from chat import chatconsumers
from game import gameconsumers

websocket_urlpatterns = [
    re_path(r"ws/chat/", chatconsumers.ChatConsumer.as_asgi()),
	re_path(r"ws/game/(?P<game_name>\w+)/$", gameconsumers.GameConsumer.as_asgi()),
]