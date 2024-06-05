from django.urls import re_path

from chat import chatconsumers
from game import gameconsumers
from game2 import gameconsumers2
from game3 import gameconsumers3
from game4 import gameconsumers4
from friends import friendsconsumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", chatconsumers.ChatConsumer.as_asgi()),
	re_path(r"ws/friends", friendsconsumers.FriendsConsumer.as_asgi()),
	re_path(r"ws/game/(?P<game_name>\w+)/$", gameconsumers.GameConsumer.as_asgi()),
	re_path(r"ws/game2/(?P<game_name>\w+)/$", gameconsumers2.GameConsumer2.as_asgi()),
    re_path(r"ws/game3/(?P<game_name>\w+)/$", gameconsumers3.GameConsumer3.as_asgi()),
    re_path(r"ws/game4/(?P<game_name>\w+)/$", gameconsumers4.GameConsumer4.as_asgi()),
]