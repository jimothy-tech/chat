import socket 
import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "CyaHoe"
server.bind(ADDR)

message_list = []
def handle_client(conn, addr):
    global message_list
    message_list = []
    print(f"[New Connection] {addr}")
    mail = message_list
    mailman = threading.Thread(target=mailmain, args=(mail, conn, addr))
    mailman.start()
    connected = True
    client_name = socket.gethostbyaddr(addr[0])[0]  
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
                message_list = []
            print(f"[{addr}] {msg}")
            message_list.append(f"[{client_name}] {msg}")
        mailmain(message_list, conn, addr)
                

def mailmain(mail, conn, addr):
    for messages in mail:
        print(messages)
        message = messages.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        conn.send(send_length)
        conn.send(message)


def start():
    server.listen()
    print(f"[Listening] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[Active Connections] {threading.activeCount() - 1}")
print("socket server is starting...")
start()