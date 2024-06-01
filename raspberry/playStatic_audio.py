import asyncio
import websockets

async def send_audio_request():
    uri = "ws://localhost:3000"
    async with websockets.connect(uri) as websocket:
        # JSON Nachricht mit dem Pfad zur Audiodatei
        await websocket.send('{"play_audio": "C:\\\\Users\\\\kilia\\\\Music\\\\car-horn-beep-beep-two-beeps-honk-honk-6188.mp3"}')
        response = await websocket.recv()
        print(response)

asyncio.run(send_audio_request())