import asyncio
import websockets
import json

async def receive_ball_position():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            position = json.loads(message)
            print(f"Ball position: {position}")

asyncio.get_event_loop().run_until_complete(receive_ball_position())