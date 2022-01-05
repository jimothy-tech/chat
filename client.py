
import socket
import threading 
import time

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "CyaHoe"
SERVER = "75.170.207.41"
ADDR = (SERVER, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = True
Client_name = socket.gethostbyaddr(SERVER)[0]
client.connect(ADDR)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def inputmsg():
    print("inputmsg running...")
    print(f"[Client name] {Client_name}")
    global connected
    while connected:
        time.sleep(.5)
        parcel = input("Message:") 
        if parcel == "exit":
            connected = False
            print('inputmsg stopped!')
            send(DISCONNECT_MESSAGE)
        send(parcel)

def display_messages():
    print("display_messages thread running...")
    new_messages = []
    while True:
        message_list_length = int(client.recv(HEADER).decode(FORMAT))
        if message_list_length:
            msg = client.recv(message_list_length).decode(FORMAT)
            if msg != f"[{Client_name}] CyaHoe":
                new_messages.append(msg)
                print(msg)
            else:
                pass
            if msg == f"[{Client_name}] CyaHoe":
                print("display_messages thread stopped!")
                break
        #for message in new_messages:
            #try:
                #if message != messages[new_messages.index(message)]:
                    #pass
            #except IndexError:
                #print(message)
                #messages.append(message)
        
thread = threading.Thread(target=display_messages)
thread.start() 
inputmsg()


