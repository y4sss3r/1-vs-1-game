import socket
import threading
import time
from utils.Game import GameServer
from utils.CommunicationProtocol import Protocol

host="127.0.0.1"
port=8000

server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((host, port))

server.listen()

players={}
waiting_queue={}

def check_for_start():
    if len(waiting_queue.keys())>=2:
        player_1=list(waiting_queue.keys())[0]
        player_2=list(waiting_queue.keys())[1]
        send_msg_to(waiting_queue[player_1], "msg", f"Battaglia avviata con {player_2}")
        send_msg_to(waiting_queue[player_1], "name", f"{player_2}")
        send_msg_to(waiting_queue[player_2], "msg", f"Battaglia avviata con {player_1}")
        send_msg_to(waiting_queue[player_2], "name", f"{player_1}")
        game=GameServer(player_1, waiting_queue[player_1], player_2,  waiting_queue[player_2])
        del waiting_queue[player_1]
        del waiting_queue[player_2]
        threading.Thread(target=game.start, daemon=True).start()
        return True

def broadcast(dataset:dict, protocol, data):
    for user in dataset:
        conn:socket.socket=dataset[user]
        
        Protocol(conn).send_msg({
            "protocol": protocol,
            "data":data
        })

def send_msg_to(conn:socket.socket, protocol, data):
    Protocol(conn).send_msg({
        "protocol": protocol,
        "data":data
    })

def manage_client(conn:socket.socket, addr):
    # try:
        packet=Protocol(conn).recv_msg()
        protocol=packet["protocol"]
        if protocol=="conn":
            player_name=packet["data"]
            players[player_name]=conn
            waiting_queue[player_name]=conn
            print(f"{player_name} si è connesso al gioco.")
            broadcast(waiting_queue, "msg", f"{player_name} si è unito alla coda")
            check_for_start()

    # except Exception as e:
    #     print(f"eccezione in manage_client(): {e}")

while True:
    conn, addr=server.accept()
    threading.Thread(target=manage_client, args=(conn, addr), daemon=True).start()
    



