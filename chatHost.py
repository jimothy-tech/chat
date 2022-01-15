import socket 
import threading
import time

HEADER = 64 #The set byte size for sending message-length messages 
PORT = 5050
SERVER = "192.168.0.136"
ADDR = (SERVER, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
FORMAT = 'utf-8' #format that the messages will be decoded and encoded in
DISCONNECT_MESSAGE = "CyaHoe" #Message sent from the client that indicates to the server that the client is exiting the app
try:
    server.bind(ADDR) 
except OSError:
    pass
clients = [] #list of clients that have connected 
nicknames = [] #list of corresponding nicknames

#start() function creates a thread for each new connection that targets this function
#which is responsible for handling the clients messages and decisions
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
        if msg == DISCONNECT_MESSAGE:    #protocol for when the the disconnect message is recieved by the server
            connected = False 
            msg = f"[{nicknames[clients.index(client)]}] {msg}"
            msg_send_handling(msg, client) #sends disconnect message back to the client in order to disable its display message functions
        else:
            print(f"[{nicknames[clients.index(client)]}] {msg}")
#mailman function sends a message to each client that is appended into the clients list                 
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
#starts the server, listening for incoming connections
def start():
    server.listen()
    print(f"[Listening] Server is listening on {SERVER}")
    while True:
        client, addr = server.accept() #When a clients connection is accepted, sets the tuple: client, addr, which are used later in the program 
        #worth noting that client is the socket object responsible for correspondence(sending and recieving messages) between the particular client and the server
        clients.append(client) #appends the socket object, which represents the client, to a list called clients
        msg_send_handling("What would you like your nickname to be?", client) #sends message to client that is intended for use in determining the clients nickname 
        nicknames.append(msg_recieve_handling(client).decode(FORMAT)) #recieves and decodes response from the client and appends chosen nickname to list nicknames
        thread = threading.Thread(target=handle_client, args=(client, addr)) #sets a thread object for handling the connecting client
        thread.start()
        print(f"[Active Connections] {threading.activeCount() - 1}")

#written for ease of use when sending messages to a particular client. Note a 'msg'(message) and 'client' parameter
# determines the length of an encoded message for use by client
# it's important to note that this line also adds as many byte-like 
# blank spaces as are needed to ensure that the length message is 64, the size of our HEADER variable
def msg_send_handling(msg, client): 
    length = str(len(msg.encode(FORMAT))).encode(FORMAT) + b' ' * (HEADER - len(msg.encode(FORMAT)))
    client.send(length) #sends length for use by client in recieving the following message
    time.sleep(1) #used in case of timing issues in recieving length-of-message and the actual message
    try:
        client.send(msg.encode(FORMAT))
    except ConnectionResetError:
        pass

#written for ease of use in recieving messages 
#length of the message being recieved for use in the socket object(client)'s attribute 'recv'
#note that in this case, the message length being passed in recv is the static length that was set 
#in the beginning of the file. This is use to ensure that we can recieve that message that tells use
#what length the following message will being
def msg_recieve_handling(client):
    length = int(client.recv(HEADER).decode(FORMAT))
    if length:
        return client.recv(length)

print("Starting socket server...")
start()
