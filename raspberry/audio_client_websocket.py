import websockets
import pygame
import asyncio
import json
import time
import os
import tempfile
import base64


pygame.mixer.init()
loop = asyncio.get_event_loop()

def play_audio(audio_file_path):
    pygame.mixer.music.load(audio_file_path)
    pygame.mixer.music.play()

async def unload_audio():
    while True:
        await asyncio.sleep(1)
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.unload()
                print("Audio unloaded")
                break
            except Exception as e:
                print(f"Error unloading audio: {e}")
                break

async def receive_file(fileName, fileData):
    if os.path.exists(fileName):
        os.remove(fileName)

    with open(fileName, "wb") as file:
        file.write(base64.b64decode(fileData))
        print(f"File received: {fileName}")

def handle_audio_command(content_obj):
    if "play_audio" in content_obj:
        try:
            audio_FileName = sanitize_filename(content_obj["play_audio"])
            print(f"Received audio file: {audio_FileName}")
            audio_path = os.path.join(os.curdir, audio_FileName)
            if os.path.exists(audio_path):
                play_audio(audio_path)
                print(f"Playing audio: {audio_path}")
        except ValueError as e:
            print(f"Error: {e}")

def get_rotating_filename(base_path, base_name, extension, limit=10):
    index_file_path = os.path.join(base_path, f"{base_name}_index.txt")
    
    if os.path.exists(index_file_path):
        with open(index_file_path, 'r') as file:
            last_index = int(file.read().strip())
    else:
        last_index = 0

    next_index = (last_index % limit) + 1

    with open(index_file_path, 'w') as file:
        file.write(str(next_index))

    filename = f"{base_name}_{next_index}.{extension}"
    return os.path.join(base_path, filename)


def sanitize_filename(filename):
    allowed_extensions = {'.mp3', '.wav'}
    
    filename = filename.strip()
    filename = filename.replace('/', '').replace('\\', '').replace('\0', '')
    filename = os.path.basename(filename)
    
    root, ext = os.path.splitext(filename)
    if ext.lower() not in allowed_extensions:
        raise ValueError(f"Unauthorized file extension: {ext}")
    
    max_length = 50
    if len(filename) > max_length:
        raise ValueError(f"Filename too long. Max length is {max_length} characters.")
    
    return filename

async def handler():
    uri = "ws://localhost:3000"
    async with websockets.connect(uri, max_size=20000000) as websocket:
        await websocket.send("{\"request\": \"message from raspberry audio client\"}")
        done = False
        while not done:
            time.sleep(10/1000)
            message = await websocket.recv()
            print(message)
            if isinstance(message, str):
                try:  
                    parsed_message = json.loads(message)
                    if "play_audio" in parsed_message:
                        handle_audio_command(parsed_message)
                        asyncio.create_task(unload_audio())
                    elif "operation" in parsed_message and parsed_message["operation"] == "file_transfer":
                        file_name = get_rotating_filename(os.curdir, "audioFile", "mp3")
                        await receive_file(file_name, parsed_message["file"])
                        play_audio(file_name)
                        asyncio.create_task(unload_audio())
                    elif "stop_audio" in parsed_message:
                        pygame.mixer.music.stop()
                        print("Audio stopped")
                except ValueError:
                    print("Could not parse message")
                    continue

asyncio.run(handler())