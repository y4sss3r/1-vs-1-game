import pygame
import socket
import threading
from utils.CommunicationProtocol import Protocol
from utils.Game import GameClient

host="127.0.0.1"
port=8000


client=socket.socket()
client.connect((host, port))
stream=Protocol(client)

def receive_data():
    while True:
        packet=stream.recv_msg()
        protocol=packet["protocol"]
        data=packet["data"]
        if protocol=="msg":
            print(data)
        elif protocol=="name":
            enemy_name=data
        elif protocol=="game":
            if data=="started":
                print("game started")
                game=GameClient(client, name, enemy_name)
                threading.Thread(target=game.start, daemon=False).start()
                break
            



threading.Thread(target=receive_data, daemon=False).start()

name=str(input("[+] inserisci il tuo nome nuckname: "))
stream.send_msg({
    "protocol":"conn",
    "data":name
})
print("[+] matchmaking...")
