import websockets
import pygame
import asyncio
import json
import time
import os
import tempfile
import base64


pygame.mixer.init()

def play_audio(audio_file_path):
    pygame.mixer.music.load(audio_file_path)
    pygame.mixer.music.play()

async def receive_file(fileName, fileData):
    if os.path.exists(fileName):
        os.remove(fileName)

    with open(fileName, "wb") as file:
        file.write(base64.b64decode(fileData))
        print(f"File received: {fileName}")

def handle_audio_command(content_obj):
    if "play_audio" in content_obj:
        audio_file_path = content_obj["play_audio"]
        play_audio(audio_file_path)
        print(f"Playing audio: {audio_file_path}")

def get_rotating_filename(base_path, base_name, extension, limit=10):
    """
    Generate a filename with a cycling number that rotates back to 1 after reaching the limit.

    Args:
    base_path (str): Directory path where the file will be saved.
    base_name (str): Base name of the file.
    extension (str): File extension.
    limit (int): The number at which the counter resets to 1.

    Returns:
    str: A file path with a cyclic rotating filename.
    """
    # File to store the last used index
    index_file_path = os.path.join(base_path, f"{base_name}_index.txt")
    
    # Read the last index used, if the file exists
    if os.path.exists(index_file_path):
        with open(index_file_path, 'r') as file:
            last_index = int(file.read().strip())
    else:
        last_index = 0

    # Compute the next index
    next_index = (last_index % limit) + 1

    # Write the new index back to the file
    with open(index_file_path, 'w') as file:
        file.write(str(next_index))

    # Generate the filename using the next index
    filename = f"{base_name}_{next_index}.{extension}"
    return os.path.join(base_path, filename)


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
                    elif "operation" in parsed_message and parsed_message["operation"] == "file_transfer":
                        file_name = get_rotating_filename(os.curdir, "audioFile", "mp3")
                        await receive_file(file_name, parsed_message["file"])
                        play_audio(file_name)
                except ValueError:
                    print("Could not parse message")
                    continue

asyncio.run(handler())