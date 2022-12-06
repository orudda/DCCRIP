import sys
import socket
import json
import time

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        inputs = input().split()
        if (inputs[2] == "S"):
            time.sleep(int(inputs[4]))
        else:
            parameter1 = ""
            parameter2 = ""
            parameter3 = ""
            router = inputs[0]
            port = inputs[1]
            command = inputs[2]
            if command == "C":
                id = 1
                parameter1 = inputs[3]
                parameter2 = inputs[4]
                parameter3 = inputs[5]
            elif command == "D":
                id = 2
                parameter1 = inputs[3]
                parameter2 = inputs[4]
                parameter3 = ""
            elif   command == "I":
                id = 3
            elif command == "F":
                id = 4
            elif command not in ["C","D","E","F", "I", "S"]:
                id = 5
            elif command == "E":
                id = 6
                parameter1 = inputs[3] 
                parameter2 = inputs[4]
                parameter3 = ""
            message = {
                "id": id,
                "command": command,
                "parameter1": parameter1,
                "parameter2": parameter2,
                "parameter3": parameter3
            }
            s.sendto(json.dumps(message).encode('utf-8'), 0, (router,int(port)))
        
except:
    print("Caught keyboard interrupt or error in interface, program stoped")