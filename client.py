
import socket
import threading 
import time
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from kivy.event import EventDispatcher
from queue import Queue
from kivy.clock import Clock
sm = ('''
ScreenManagement:
    id: screen_manager
    NickPage:
        name: "Nick"
        id: nick
        manager: screen_manager
    ChatPage:
        name: "Chat"
        id: chat
        manager: screen_manager
<NickPage>
    MDTextField:
        id: text_field
        multiline: False
        mode: "fill"
        hint_text: "Nickname"
        valign: "center"
        halign: "center"
        pos_hint: {"center_x": .5, "center_y": .5}
        size_hint: (.5, .1)
    MDFlatButton:
        text: "Submit"
        theme_text_color: "Custom"
        text_color: 0, 0, 1, 1
        pos_hint: {"center_y": .5, "right": .9}
        on_press: root.submit_button()
<ChatMessages>
    GridLayout:
        id: grid
        size_hint_y: .9
        cols: 1
<ChatPage>
    MDTextField:
        id: chat_input
        multiline: False
        mode: "fill"
        hint_text: "Message"
        icon_right: "language-python"
        icon_right_color_focus: 0, 1, 0, 1
        size_hint: (.89, .10)
        pos_hint: {"left": 1}
    MDFlatButton:
        text: "Send"
        theme_text_color: "Custom"
        text_color: 0, 0, 1, 1
        pos_hint: {"right": 1}
        size_hint: (.11, .115)
        on_press: root.buttonpress()
    
'''
)

class MessageEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_message')
        super(MessageEventDispatcher, self).__init__(**kwargs)

    def dispatch_message(self, value):
        self.dispatch('on_message', value)

    def on_message(self, message):
        pass

class ScreenManagement(ScreenManager):
        pass

q = Queue()

class NickPage(Screen):
    def __init__(self, **kwargs):
        super(NickPage, self).__init__(**kwargs)
        self.nick_text_field = MDTextField(pos_hint={"center_x": .5, "center_y": .5}, 
        size_hint=(.5, .1), 
        hint_text="Nickname", 
        mode="fill",
        text_color=(0, 0, 1, 1))
        self.add_widget(self.nick_text_field)
        self.submit_btn = MDFlatButton(text="Submit",
        theme_text_color="Custom",
        pos_hint={"center_y": .5, "right": .9},
        text_color=(0, 0, 1, 1))
        self.submit_btn.bind(on_press=self.submit_button)
        self.add_widget(self.submit_btn)
    def submit_button(self, instance):
        nickname = self.nick_text_field.text
        Main.nickname = nickname
        send(nickname)
        self.manager.current = "Chat"

class ChatMessages(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, size_hint_y=.8)
        self.add_widget(self.layout)
        self.chat_history = ["These", "Are", "Tests", "These", "Are", "Tests", "These", "Are", "Tests", "These", "Are", "Tests"]
        for every_message in self.chat_history:
            self.layout.add_widget(MDFillRoundFlatIconButton(text=every_message, size_hint_y=.1))
        #self.scrollpoint = MDLabel()
        #self.layout.add_widget(self.scrollpoint)

class ChatPage(Screen):
    def __init__(self, **kwargs):
        super(ChatPage, self).__init__(**kwargs)
        self.ev = MessageEventDispatcher()
        self.ev.bind(on_message=self.add_new_message)
        scroll_area = ScrollView()
        self.layout = GridLayout(cols=1, size_hint_y=.8)
        scroll_area.add_widget(self.layout)
        self.add_widget(scroll_area)
        self.chat_inputtext_field = MDTextField(multiline=False,
        mode="fill",
        hint_text="Message",
        icon_right="language-python",
        size_hint=(.89, .10),
        pos_hint={"left": 1})
        self.add_widget(self.chat_inputtext_field)
        self.send_button = MDFlatButton(text="Send",
        theme_text_color="Custom",
        pos_hint={"right": 1},
        size_hint=(.11, .115),
        text_color=(0, 0, 1, 1))
        self.send_button.bind(on_press=self.buttonpress)
        self.add_widget(self.send_button)
        Clock.schedule_interval(self.dispatch_trigger, .5)

    def dispatch_trigger(self, dt):
        message = None
        try:
            message = q.get_nowait()
            self.ev.dispatch_message(message)
            print("message was dispatched")
        except:
            pass

    def add_new_message(self, value, message):
        self.layout.add_widget(MDFillRoundFlatIconButton(text=message, size_hint_y=.1))
        #print(f"[This is the message that's suppose to be added via add_new_message()] {message}")
        print('Message should have been displayed as' + message)

    def buttonpress(self, instance):
        print("button was pressed!")
        print(self.chat_inputtext_field.text)
        msg = self.chat_inputtext_field.text
        send(msg)
        self.chat_inputtext_field.text = ""
        #function for recieving messages from the mailman function found in host and then displaying them 
    def display_messages(self):
        print("display_messages thread running...")
        while True:
            message_length = int(Main.client.recv(Main.HEADER).decode(Main.FORMAT))
            if message_length:
                msg = Main.client.recv(message_length).decode(Main.FORMAT)
                print(Main.nickname)
                print(f"[Display message] {msg}")
                if msg != f"[{Main.nickname}] CyaHoe": #makes sure the disconnect message isn't displayed when it is recieved 
                    q.put(msg)
                    #print(f"[self.label.text] {self.label.text}")
                    if msg == "What would you like your nickname to be?":
                        Main.nickname = Main.client.recv(message_length).decode(Main.FORMAT)
                else: #breaks the display message loop when the disconnect message is sent back to the self.client 
                    print("display_messages thread stopped!")
                    break
        
    def msg_send_handling(msg, self):
        length = str(len(msg.encode(self.FORMAT))).encode(self.FORMAT) + b' ' * (self.HEADER - len(msg.encode(self.FORMAT)))
        self.client.send(length)
        time.sleep(1)
        self.client.send(msg.encode(self.FORMAT))

    def msg_recieve_handling(self):
        length = int(self.client.recv(self.HEADER).decode(self.FORMAT))
        if length:
            return self.client.recv(length)


class Main(MDApp):
    HEADER = 64
    PORT = 5050
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "CyaHoe"
    SERVER = "localhost"
    ADDR = (SERVER, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = True
    nickname = "" #client's set nickname
    mail = ""

    def __init__(self, **kwargs):
        self.title = "JChat"
        super(Main, self).__init__(**kwargs)

    def build(self):
        #self.builder = Builder.load_string(sm)
        sm = ScreenManagement()
        sm.add_widget(NickPage(name="Nick"))
        sm.add_widget(ChatPage(name="Chat"))
        self.client.connect(self.ADDR)
        thread = threading.Thread(target=ChatPage().display_messages)
        thread.start()
        return sm

#simply a function used to send a message to the server with the same concepts as used in the host file
def send(msg):
    message = msg.encode(Main.FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(Main.FORMAT)
    send_length += b' ' * (Main.HEADER - len(send_length))
    Main.client.send(send_length)
    Main.client.send(message)

if __name__ == '__main__':
    Main().run()



