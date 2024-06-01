import asyncio
import websockets
import os
import json
import base64


async def send_audio_request():
    uri = "ws://localhost:3000"
    file_path = "C:\\Users\\kilia\\Music\\01_She_Couldn_t.mp3"

    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
        "operation": "file_transfer",
        "file": encoded_string
    }))


asyncio.run(send_audio_request())