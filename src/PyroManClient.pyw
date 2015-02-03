#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Code for the PyroMan Client + GUI. 
This is a fork where all Pyro4 dependencies are removed.
This File is meant to be called manually, it is the main entry point of the Chat program
¸Anybody who wants to chat or host a chat must run this file
"""
from tkinter import *
from tkinter import font
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import socket
import base64
from threading import Thread
from serverTest import *


__author__ = "fireraccoon"
__copyright__ = "Copyright 2014, Team GOAT"
__credits__ = ["fireraccoon"]
__license__ = "MIT"
__version__ = '14.09.16.1'
__maintainer__ = "fireraccoon"
__email__ = ""
__status__ = "Production"

VERSION = '14.09.16.1-b'



class PMClient():
    """ The Client object
    """

    class Code:
        """ Return codes the client generates
        in certain situations
        """
        NAME_TAKEN = 0
        CONNECTION_SUCCESSFUL = 1
        COMMAND_HELP = 2
        COMMAND_USERS = 3
        MESSAGE = 4

    def __init__(self):
        self.username = ""
        self.uri = ""
        self.host = ""
        self.server = None
        self.clientId = -1

    class Host(object):
        """docstring for Host"""
        def __init__(self):
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        def connect(self,target_host,target_port):
            print("Connecting to "+str(target_host))
            self.connection.connect((target_host,target_port))
            print("Connected")

        def sendPacket(self,msg):
            self.connection.send(self.wrap(msg))

        def receivePacket(self):

            print("receiving")
            file_buffer = b""

            buffer_len = 1
            while buffer_len:
                data = self.connection.recv(4096)
                if not data:
                    break
                else:
                    file_buffer += data
                    if len(data) < 4096:
                        break
            print("End")
            print(file_buffer[2:len(file_buffer)-1].decode("UTF-8"))

            return file_buffer[2:len(file_buffer)-1].decode("UTF-8")

        def wrap(self,msg):
            enc = ""
            print(msg)
            for plain in msg:
                enc += str(base64.b64encode(plain.encode('ascii')))+str("*")
            return bytes(enc, 'UTF-8')

        def unwrap(self,enc):
            encoded_ans = enc.split("*")
            plain_ans = []
            for item in encoded_ans:
                if item[0:2] == "b'":
                    item = item[2:]
                plain_ans.append(base64.b64decode(item).decode("utf-8"))
            print(plain_ans)
            return plain_ans

        def getUsers(self):
            msg = ["getUsers"]
            self.sendPacket(msg)
            return self.unwrap(self.receivePacket())

        def joinRoom(self,username):
            msg = ["joinRoom",username]
            self.sendPacket(msg)
            return self.unwrap(self.receivePacket())[0]

        def getNewRoomID(self):
            msg = ["getNewRoomID"]
            self.sendPacket(msg)
            return int(self.unwrap(self.receivePacket())[0])


        def getLastMessage(self, clientId):
            msg = ["getLastMessage", str(clientId)]
            self.sendPacket(msg)
            last = self.unwrap(self.receivePacket())
            print(last)
            if last[0] != "":
                return ''.join(last)

        def sendMessage(self, username, userInput):
            msg = ["sendMessage", str(username), str(userInput)]
            self.sendPacket(msg)
            return self.unwrap(self.receivePacket())

        def leaveRoom(self, username):
            msg = ["leaveRoom", str(username)]
            self.sendPacket(msg)
            ans = self.unwrap(self.receivePacket())
            self.connection.close()
            return ans

    @staticmethod
    def getIP():
        """  Returns the ip address of the client
        :return: ip string
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('google.com', 0))
        return s.getsockname()[0]

    def connect(self, host, port, name):
        """
        Connects the client to a host on a port with a username
        :param host:
        :param port:
        :param name:
        :return:
        """
        try:            
            self.host = self.Host()
            self.host.connect(host,int(port))

        except:
            ChatWindow.showMessageBox('error', "Error while connecting")
            #will need new error code
            return PMClient.Code.NAME_TAKEN

        users = self.host.getUsers()
        if users:
            if name in users:
                ChatWindow.showMessageBox('warning', "That homie is already in tha hood choose another homie name!")
                return PMClient.Code.NAME_TAKEN

        self.username = name
        self.host.joinRoom(self.username)

        self.clientId = self.host.getNewRoomID()
        print(self.clientId)
        return PMClient.Code.CONNECTION_SUCCESSFUL


    def fetchMessages(self):
        """ Fetch the messages that room has not seen yet
        :return: Last Messages (list(string))
        """
        if self.host:
            response = self.host.getLastMessage(self.clientId)
        if response:
            message = response
            return message
        else:
            return None

    def processInput(self, userInput):
        """ Processes the user input and take action accordingly
        :param userInput: the text the user has entered
        :return: PCMClient.Code
        """
        if userInput.strip() == '/help':
            return PMClient.Code.COMMAND_HELP
        elif userInput.strip() == '/users':
            return PMClient.Code.COMMAND_USERS
        else:
            self.host.sendMessage(self.username, userInput)
            return PMClient.Code.MESSAGE


    def leaveRoom(self):
        """ Lets the user leave the room
        """
        self.host.leaveRoom(self.username)
        self.host = None


    def startServerThread(self):
        serverThread = Thread(target=self.startServer)
        serverThread.start()

    def startServer(self):
        print("starting server...")
        self.server = Server()
        self.server.start()

    def stopServer(self):
        pass
        #self.server.shutdown()



class ChatWindow():
    """ THE PROGRAM GUI
    """
    def __init__(self, clientControl):
        """
        :param clientControl: A PCMClient object
        """
        self.root = Tk()
        self.clientControl = clientControl
        self.root.wm_title("PyroMan Client v." + str(VERSION))
        self.mainFrame = Frame(self.root)
        self.mainFrame.pack(fill=BOTH)
        self.initUi()


    def initUi(self):
        # Panel Settings
        self.panelSettings = Frame(self.mainFrame)

        labelStatus = Label(self.panelSettings, text="Status:")
        labelStatus.grid(row=0, column=0)
        self.labelStatus = Label(self.panelSettings, text="Offline", foreground="red")
        self.labelStatus.grid(row=0, column=1)

        labelServerIP = Label(self.panelSettings, text="Server IP:")
        labelServerIP.grid(row=1, column=0)
        self.serverIP = Entry(self.panelSettings)
        self.serverIP.grid(row=1, column=1)

        labelServerPort = Label(self.panelSettings, text="Server Port:")
        labelServerPort.grid(row=2, column=0)
        self.serverPort = Entry(self.panelSettings)
        self.serverPort.grid(row=2, column=1)

        labelUserName = Label(self.panelSettings, text="Username:")
        labelUserName.grid(row=3, column=0)
        self.username = Entry(self.panelSettings)
        self.username.grid(row=3, column=1)

        self.btnConnect = Button(self.panelSettings, text="Connect", command=self.onConnect)
        self.btnConnect.grid(row=4, column=0, columnspan=2, sticky=N + E + W, pady=5)

        labelMyIP = Label(self.panelSettings, text="Your IP Adress")
        labelMyIP.grid(row=5, column=0, columnspan=2, sticky=N + E + W, pady=5)

        myIPAddress = self.clientControl.getIP()
        self.myIP = Entry(self.panelSettings, justify=CENTER, disabledforeground="red")
        self.myIP.grid(row=6, column=0, columnspan=2, sticky=N + E + W, pady=5)
        self.myIP.insert(END, myIPAddress)
        self.myIP.config(state=DISABLED)

        self.btnServer = Button(self.panelSettings, text="Start server", command=self.onStartServer)
        self.btnServer.grid(row=7, column=0, columnspan=2, sticky=N + E + W, pady=5)

        self.panelSettings.grid(row=0, column=0, sticky=N, padx=5)


        # Panel Chat
        self.panelChat = Frame(self.mainFrame)

        self.chat = Text(self.panelChat)
        self.chat.config(state=DISABLED)
        self.chat.grid(row=0, column=0)

        self.input = Entry(self.panelChat)
        self.input.grid(row=1, column=0, sticky=N + E + W, pady=5)
        self.input.bind('<Return>', self.onSendMessage)

        self.panelChat.grid(row=0, column=1, padx=4, pady=3)


    def show(self):
        self.root.mainloop()

    def updateAsConnected(self):
        self.btnConnect.config(text="Disconnect", command=self.onDisconnect)
        self.labelStatus.config(text="Online", foreground="green")

        self.serverIP.configure(state='disabled')
        self.serverPort.configure(state='disabled')
        self.username.configure(state='disabled')

    def updateAsDisconnected(self):
        self.btnConnect.config(text="Connect", command=self.onConnect)
        self.labelStatus.config(text="Offline", foreground="red")

    def onConnect(self):
        host = self.serverIP.get()
        port = self.serverPort.get()
        username = self.username.get()

        if not host or not port or not username:
            self.showMessageBox('error', "One of the field is empty, please fill in all of the fields.")
            return

        response = self.clientControl.connect(host, port, username)
        if response == PMClient.Code.NAME_TAKEN:
            return
        elif response == PMClient.Code.CONNECTION_SUCCESSFUL:
            ChatWindow.showMessageBox('info', "Connection successful! Motherfucker!")
            self.updateAsConnected()
            self.checkMessagesLoop()

    def onDisconnect(self):
        self.clientControl.leaveRoom()
        self.updateAsDisconnected()

    def onSendMessage(self, ev):
        response = self.clientControl.processInput(self.input.get())
        if response == PMClient.Code.COMMAND_USERS:
            self.printUsersList()
        elif response == PMClient.Code.COMMAND_HELP:
            self.printHelpMenu()

    def onStartServer(self):
        try:
            self.clientControl.startServerThread()
            ChatWindow.showMessageBox('info', "Server Started")
        except Exception as e:
            ChatWindow.showMessageBox('error', "[ERROR]" + str(e))

    def checkMessagesLoop(self):
        """ Checks on the server periodically
        if there are any new message
        """
        msg = self.clientControl.fetchMessages()
        if msg:
            self.insertChatLine(msg)
        self.root.after(20, self.checkMessagesLoop)

    def printUsersList(self):
        users = self.server.getUsers()
        self.insertChatLine("==============================================")
        self.insertChatLine("Connected users (%s):" % len(users))
        for user in users:
            if user == self.username:
                self.insertChatLine("*" + user)
            else:
                self.insertChatLine(user)
        self.insertChatLine("==============================================")

    def printHelpMenu(self):
        self.insertChatLine("==============================================")
        self.insertChatLine("/help prints the help menu")
        self.insertChatLine("/users prints the list of users")
        self.insertChatLine("/quit quits the chat")
        self.insertChatLine("==============================================")

    def insertChatLine(self, line):
        """ Inserts a new line in the chat window
        :param line: the line to display
        """

        
        line += "\n"

        self.chat.config(state=NORMAL)

        username, message = line.split(':')
        if(username and message):
            self.chat.insert(END, "\n")
            color = self.colorUsername(username)
            self.chat.insert(END, username, username)
            self.chat.tag_config(username, foreground=color, font=font.Font(weight='bold'))
            self.chat.insert(END, " : " + message)
        else:
            self.chat.insert(END, line)

        self.chat.config(state=DISABLED)
        self.input.delete(0, END)

        





    def colorUsername(self, userName):
        return "#" + "".join("{:02x}".format(ord(c)) for c in userName)[:6]



    @staticmethod
    def showMessageBox(msgType, msg):
        """  A helper method creating dialog messages based on type
        :param msgType: the type of message dialog
        :param msg: the message to display in the dialogue
        """
        if msgType == 'info':
            messagebox.showinfo("Chat", msg)
        elif msgType == 'error':
            messagebox.showerror("Chat", msg)
        elif msgType == 'warning':
            messagebox.showwarning("Chat", msg)


def main():
    c = PMClient()
    w = ChatWindow(c)
    w.show()

if __name__ == '__main__':
    main()
