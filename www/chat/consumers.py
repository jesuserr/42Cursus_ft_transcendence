import json
import asyncio
import time
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #print("aqui")
        self.room_name = self.scope["url_route"]["kwargs"]
        self.room_group_name = f"chat"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        #iniciar el loop del juego
        asyncio.ensure_future(self.send_periodic_message())
       

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )
        
        
    async def send_periodic_message(self):
        while True:
            #bucle del juego
            await self.send(text_data=json.dumps({"message": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}))
            await asyncio.sleep(1 / 10)

    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))