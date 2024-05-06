import json
import asyncio
import time
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["game_name"]
        self.room_group_name = f"game_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        #iniciar el loop del juego
        asyncio.ensure_future(self.playGame())
     

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        game_data_json = json.loads(text_data)
        
        
    async def playGame(self):
        while True:
            #bucle del juego
            #await self.send(text_data=json.dumps({"message": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}))
            await asyncio.sleep(1 / 60)

