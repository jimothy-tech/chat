
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
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from kivy.event import EventDispatcher
from queue import Queue
from kivy.clock import Clock
from kivy.core.window import Window
import random
from kivy.graphics import Color
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

##For reference:
#class MessageEventDispatcher(EventDispatcher):
    #def __init__(self, **kwargs):
        #self.register_event_type('on_message')
        #super(MessageEventDispatcher, self).__init__(**kwargs)

   # def dispatch_message(self, value):
    #    self.dispatch('on_message', value)

  #  def on_message(self, message):
   #     pass

q = Queue()

class ScreenManagement(ScreenManager):
    pass

class NickPageBackGround(Widget):
    def __init__(self, **kwargs):
        super(NickPageBackGround, self).__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 1, mode='rgb')

class NickPage(Screen):
    def __init__(self, **kwargs):
        super(NickPage, self).__init__(**kwargs)
        self.add_widget(NickPageBackGround(size_hint=(1, 1)))
        self.nick_text_field = MDTextField(pos_hint={"center_x": .5, "center_y": .5},
        on_text_validate=self.submit_button,
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
        byjimothy = MDLabel(text="Brought to you by jimothy.tech\nPowered by Python", 
        pos_hint={"center_x": .5, "center_y": .3}, 
        halign="center", valign="center",
        text_color=(0, 0, 0, .25))
        self.add_widget(byjimothy)
        title = MDLabel(text="JChat", font_style="H1",
        pos_hint={"center_x": .5, "center_y": .8},
        halign="center", valign="center")
        self.add_widget(title)

    def submit_button(self, value):
        thread = threading.Thread(target=ChatPage().display_messages)
        thread.start()
        nickname = self.nick_text_field.text
        Main.nickname = nickname
        send(nickname)
        self.manager.current = "Chat"

class MessageScrollArea(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll_area = ScrollView(do_scroll_y=True, do_scroll_x=False)
        self.layout = GridLayout(cols=1, size_hint_y=None, size_hint_x=1, spacing=10)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll_area.add_widget(self.layout)
        self.add_widget(self.scroll_area)

class ChatPage(Screen):
    def __init__(self, **kwargs):
        super(ChatPage, self).__init__(**kwargs)
        self.scroll_area = ScrollView(do_scroll_y=True, do_scroll_x=False)
        self.layout1 = BoxLayout(orientation="vertical", size_hint_y=None, size_hint_x=1, spacing=10)
        self.layout1.bind(minimum_height=self.layout1.setter('height'))
        self.scroll_area.add_widget(self.layout1)
        #MAIN LAYOUT
        self.layout2 = GridLayout(cols=1, rows=2, size_hint=(1, 1), rows_minimum={0: Window.height * .9, 1: Window.height * .1})
        self.layout2.add_widget(self.scroll_area)
        self.text_and_send_area = GridLayout(cols=2, spacing=10, cols_minimum={0: Window.width*.8})
        self.anchor_button = AnchorLayout(size_hint=(1, 1))
        self.anchor_text_input = AnchorLayout(size_hint=(1, 1))
        self.chat_inputtext_field = MDTextField(multiline=False,
        mode="fill",
        on_text_validate=self.buttonpress,
        hint_text="Message",
        icon_right="language-python")
        self.send_button = MDFlatButton(text="Send",
        height=100,
        width=100,
        theme_text_color="Custom",
        text_color=(0, 0, 1, 1))
        self.send_button.bind(on_press=self.buttonpress)
        self.anchor_text_input.add_widget(self.chat_inputtext_field)
        self.anchor_button.add_widget(self.send_button)
        self.text_and_send_area.add_widget(self.anchor_text_input)
        self.text_and_send_area.add_widget(self.anchor_button)
        self.layout2.add_widget(self.text_and_send_area)
        self.add_widget(self.layout2)
        Window.bind(on_resize=self.resize_layout)
        Clock.schedule_interval(self.add_new_message, 0)

    def resize_layout(self, width, height, *args):
        self.text_and_send_area.cols_minimum = {0: Window.width * .8}
        self.layout2.rows_minimum = {0: Window.height * .9, 1: Window.height * .1}

    def add_new_message(self, dt):
        message = None
        try:
            message = q.get_nowait()
            extract_nickname = (message.split("]")[0]).split("[")[1]
            if extract_nickname == Main.nickname:
                pos = {"left": 1}
            else: pos = {"right": 1}
            q.task_done()
            self.layout1.add_widget(MDFillRoundFlatIconButton(md_bg_color=Main.chat_color, text=message, size_hint_y=.1, pos_hint=pos))
            print(f"[Message] {message}")
        except:
            pass
    
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
                    Main.chat_color = (msg.split(" #")[0]).split(" ")
                    print(f"[Main.chat_color] {Main.chat_color}")
                    print(msg.split(" #"))
                    msg = (msg.split(" #")[1])
                    print(f"[Message after split] {msg}")
                    q.put(msg)
                else: #breaks the display message loop when the disconnect message is sent back to the self.client 
                    print("display_messages thread stopped!")
                    break


class Main(MDApp):
    HEADER = 64
    PORT = 5050
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "CyaHoe"
    SERVER = "192.168.0.136"
    ADDR = (SERVER, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = True
    nickname = "" #client's set nickname
    mail = ""
    chat_color = []

    def __init__(self, **kwargs):
        self.title = "JChat"
        super(Main, self).__init__(**kwargs)

    def build(self):
        #self.builder = Builder.load_string(sm)
        Clock.max_iteration = 1000
        Window.clearcolor = (1, 0, 0, 1)
        sm = ScreenManagement()
        sm.add_widget(NickPage(name="Nick"))
        sm.add_widget(ChatPage(name="Chat"))
        self.client.connect(self.ADDR)
        Window.bind(on_request_close=self.close_window)
        return sm
        
            
    def close_window(self, value):
        send(self.DISCONNECT_MESSAGE)

    def msg_send_handling(msg, self):
        length = str(len(msg.encode(self.FORMAT))).encode(self.FORMAT) + b' ' * (self.HEADER - len(msg.encode(self.FORMAT)))
        self.client.send(length)
        time.sleep(1)
        self.client.send(msg.encode(self.FORMAT))

    def msg_recieve_handling(self):
        length = int(self.client.recv(self.HEADER).decode(self.FORMAT))
        if length:
            return self.client.recv(length)

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



