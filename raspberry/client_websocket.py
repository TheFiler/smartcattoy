import asyncio
import websockets
import json
import serial
import threading
import time
import random

#Serial Connection to Arduino
#ser = serial.Serial('/dev/ttyACM0', baudrate = 9600, timeout = 0.05)
ser = serial.Serial('COM3', baudrate = 9600, timeout = 0.05)
ser.reset_input_buffer()
global autopilotstatus
autopilotstatus = False
autopilot = None
tof_distance = ""

def findCommandInString(text):
    if "motor1PW" in text:
        return True
    if "motor1D" in text:
        return True
    if "motor2PW" in text:
        return True
    if "motor2D" in text:
        return True

def autopilotMode():
    print("before going into loop")
    while autopilotstatus:
        print(autopilotstatus)
        print("Sending Autopilot command")
        if not tof_distance and int(tof_distance) > 150:
            ser.write(("55," + str(1)  + ",55," + str(1)  + ",\n").encode("UTF-8"))
        else:
            leftD = round(random.random())
            rightD = round(random.random())
            ser.write(("55," + str(leftD)  + ",55," + str(rightD)  + ",\n").encode("UTF-8"))
        
        time.sleep(2)

def updateAutopilot(content_obj):
    if content_obj["autopilot"]:
        print("autopilot enabled")
        global autopilotstatus
        autopilotstatus = True
        autopilot = threading.Thread(name="autopilot", target=autopilotMode, args=())
        autopilot.start()
    else:
        print("Setting autopilot status to false")
        autopilotstatus = False

def createMotorString(content_obj):
 return str(content_obj["motor1PW"]) + "," + str(content_obj["motor1D"]) + "," + str(content_obj["motor2PW"]) + "," + str(content_obj["motor2D"]) + "," + "\n"

# create handler for each connection
async def handler():
    uri = "ws://localhost:3000"
    async with websockets.connect(uri) as websocket:
        await websocket.send("{\"request\": \"message from raspberry\"}")
        done = False
        while not done:
            line = ser.readline()
            tof_distance = line.decode('utf-8')
            #print(tof_distance)
            time.sleep(10/1000)
            message = await websocket.recv()
            print(message)
            if "{" in message:
                positionOfContent = message.index("{")
                jsonContent = message[positionOfContent:]
                content_obj = json.loads(jsonContent)
                print(jsonContent)
                if "autopilot" in message:
                    updateAutopilot(content_obj)

                if not autopilotstatus and findCommandInString(message):
                    serialCommand = createMotorString(content_obj)
                    print("SerialCommand: " + serialCommand)
                    ser.write(str(serialCommand).encode("UTF-8"))

asyncio.run(handler())
