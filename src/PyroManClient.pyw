#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Code for the PyroMan Client + GUI
This File is meant to be called manually, it is the main entry point of the Chat program
¸Anybody who wants to chat or host a chat must run this file
"""
import Pyro4
from tkinter import *
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import socket
from threading import Thread
from PyroManServer import PMServer


__author__ = "fireraccoon"
__copyright__ = "Copyright 2014, Team GOAT"
__credits__ = ["fireraccoon"]
__license__ = "MIT"
__version__ = '14.09.16.1'
__maintainer__ = "fireraccoon"
__email__ = ""
__status__ = "Production"

VERSION = '14.09.16.1'



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

    @staticmethod
    def getIP():
        """  Returns the ip address of the client
        :return: ip string
        """
        return socket.gethostbyname(socket.gethostname())

    def connect(self, host, port, name):
        """
        Connects the client to a host on a port with a username
        :param host:
        :param port:
        :param name:
        :return:
        """
        try:
            self.uri = "PYRO:foo@%s:%s" % (host, port)
            self.host = Pyro4.Proxy(self.uri)
        except Pyro4.errors.CommunicationError:
            ChatWindow.showMessageBox('error', "o")

        if name in self.host.getUsers():
            ChatWindow.showMessageBox('warning', "That homie is already in tha hood choose another homie name!")
            return PMClient.Code.NAME_TAKEN

        self.username = name
        self.host.joinRoom(self.username)

        self.clientId = self.host.getNewRoomID()
        return PMClient.Code.CONNECTION_SUCCESSFUL

    def fetchMessages(self):
        """ Fetch the messages that room has not seen yet
        :return: Last Messages (list(string))
        """
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


    def startServerThread(self):
        serverThread = Thread(target=self.startServer)
        serverThread.start()

    def startServer(self):
        print("starting server...")
        self.server = PMServer(self.getIP())
        self.server.start()

    def stopServer(self):
        self.server.shutdown()



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
        self.chat.insert(END, line)
        self.chat.config(state=DISABLED)
        self.input.delete(0, END)

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
