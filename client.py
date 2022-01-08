
import socket
import threading 
import time

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "CyaHoe"
SERVER = "192.168.0.12"
ADDR = (SERVER, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = True
client.connect(ADDR)
nickname = ""

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def inputmsg():
    print("inputmsg running...")
    global connected
    while connected:
        parcel = input() 
        if parcel == "exit":
            connected = False
            print('inputmsg stopped!')
            send(DISCONNECT_MESSAGE)
        send(parcel)

def display_messages():
    print("display_messages thread running...")
    new_messages = []
    while True:
        message = int(client.recv(HEADER).decode(FORMAT))
        if message:
            msg = client.recv(message).decode(FORMAT)
            if msg != f"[{nickname}] CyaHoe":
                new_messages.append(msg)
                print(msg)
            else:
                print("display_messages thread stopped!")
                break
        
def msg_send_handling(msg):
    length = str(len(msg.encode(FORMAT))).encode(FORMAT) + b' ' * (HEADER - len(msg.encode(FORMAT)))
    client.send(length)
    time.sleep(1)
    client.send(msg.encode(FORMAT))

def msg_recieve_handling():
    length = int(client.recv(HEADER).decode(FORMAT))
    if length:
        return client.recv(length)

def choose_nickname():
    global nickname
    nick_question = msg_recieve_handling().decode(FORMAT)
    nickname = input(nick_question + "\n Nickname:")
    msg_send_handling(nickname)

choose_nickname()
thread = threading.Thread(target=display_messages)
thread.start() 
inputmsg()


