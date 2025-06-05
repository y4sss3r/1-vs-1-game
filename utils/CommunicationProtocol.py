import socket
import json

class Protocol:
    def __init__(self, conn: socket.socket):
        self.conn = conn
        self.BLOCK_SIZE = 32  # Non usato in questo esempio, ma ok tenerlo

    def send_msg(self, data):
        msg = json.dumps(data).encode()
        total_len = len(msg)
        header = total_len.to_bytes(4, byteorder='big')
        self.conn.sendall(header)
        self.conn.sendall(msg)

    def recv_exact(self, size):
        data = b''
        while len(data) < size:
            chunk = self.conn.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def recv_msg(self):
        header = self.recv_exact(4)
        if not header:
            raise Exception("header vuoto")
        msg_length = int.from_bytes(header, byteorder='big')
        data = self.recv_exact(msg_length).decode()
        #print(data)
        return json.loads(data)
