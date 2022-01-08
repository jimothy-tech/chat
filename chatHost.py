import socket 
import threading
import time

HEADER = 64
PORT = 5050
SERVER = "192.168.0.12"
ADDR = (SERVER, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "CyaHoe"
try:
    server.bind(ADDR)
except OSError:
    pass
clients = []
nicknames = []

def handle_client(client, addr):
    print(f"[New Connection] {addr}")
    connected = True
    #client_name = socket.gethostbyaddr(addr[0])[0]  
    while connected:
        try:
            msg = msg_recieve_handling(client).decode(FORMAT)
        except AttributeError:
            msg = " "
        mailman(f"[{nicknames[clients.index(client)]}] {msg}".encode(FORMAT))
        if msg == DISCONNECT_MESSAGE:
            connected = False 
            msg = f"[{nicknames[clients.index(client)]}] {msg}"
            msg_send_handling(msg, client)
        else:
            print(f"[{nicknames[clients.index(client)]}] {msg}")
                
def mailman(mail):
    for client in clients:
        #message = messages.encode(FORMAT)
        msg_length = len(mail)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        try: 
            client.send(send_length)
            client.send(mail)
        except BrokenPipeError:
            pass

def start():
    server.listen()
    print(f"[Listening] Server is listening on {SERVER}")
    while True:
        client, addr = server.accept()
        clients.append(client)
        msg_send_handling("What would you like your nickname to be?", client)
        nicknames.append(msg_recieve_handling(client).decode(FORMAT))
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()
        print(f"[Active Connections] {threading.activeCount() - 1}")

def msg_send_handling(msg, client):
    length = str(len(msg.encode(FORMAT))).encode(FORMAT) + b' ' * (HEADER - len(msg.encode(FORMAT)))
    client.send(length)
    time.sleep(1)
    try:
        client.send(msg.encode(FORMAT))
    except ConnectionResetError:
        pass
def msg_recieve_handling(client):
    length = int(client.recv(HEADER).decode(FORMAT))
    if length:
        return client.recv(length)

#msg_send_handling_thread = threading.Thread(target=msg_send_handling)
#msg_recieve_handling_thread = threading.Thread(target=msg_recieve_handling)
#msg_send_handling_thread.start()
#msg_recieve_handling_thread.start()
print("Starting socket server...")
start()