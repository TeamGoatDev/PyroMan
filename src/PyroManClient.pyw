import Pyro4
from tkinter import *
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import socket
from threading import Thread
from PyroManServer import *




class ClientCode:
    NAME_TAKEN = 0
    CONNECTION_SUCCESSFUL = 1
    COMMAND_HELP = 2
    COMMAND_USERS = 3
    MESSAGE = 4


class Client():
        def __init__(self):
                self.username = ""
                self.uri = ""
                self.server = ""
                self.clientId = ""
                
        def getIP(self):
            return socket.gethostbyname(socket.gethostname())
                
        def connect(self, host, port, name):
                try:
                    self.uri="PYRO:foo@%s:%s"%(host,port)
                    self.server=Pyro4.Proxy(self.uri)
                except Pyro4.errors.CommunicationError:
                    ChatWindow.showMessageBox('error', "o")

                if name in self.server.getUsers():
                    ChatWindow.showMessageBox('warning', "That homie is already in tha hood choose another homie name!")
                    return ClientCode.NAME_TAKEN
                    
                self.username = name
                response=self.server.joinRoom(self.username)
                
                
                self.clientId = self.server.getNewRoomID()
                return ClientCode.CONNECTION_SUCCESSFUL


        def fetchMessages(self):
            response = self.server.getLastMessage(self.clientId)
            if response:
                message = response
                return message
            else:
                return None



        def processInput(self, userInput):
            if userInput.strip() == '/help':
                return ClientCode.COMMAND_HELP
            elif userInput.strip() == '/users':
                return ClientCode.COMMAND_USERS
            else:
                self.server.sendMessage(self.username, userInput)
                return ClientCode.MESSAGE


        

        def leaveRoom(self):
            self.server.leaveRoom(self.username)









class ChatWindow():
    def __init__(self, clientControl):
        self.root = Tk()
        self.clientControl = clientControl
        #self.root.title() # = "GoatChat"
        self.mainFrame = Frame(self.root)
        self.mainFrame.pack(fill=BOTH)
        self.initUi()
        self.root.mainloop()

  
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


        self.btnConnect = Button(self.panelSettings, text="Connect", command=self.actionConnect)
        self.btnConnect.grid(row=4, column=0, columnspan=2, sticky=N+E+W, pady=5)

        

        labelMyIP = Label(self.panelSettings, text="Your IP Adress")
        labelMyIP.grid(row=5, column=0, columnspan=2, sticky=N+E+W, pady=5)

        myIPAddress = self.clientControl.getIP()
        self.myIP = Entry(self.panelSettings, justify=CENTER, disabledforeground="red")
        self.myIP.grid(row=6, column=0, columnspan=2, sticky=N+E+W, pady=5)
        self.myIP.insert(END, myIPAddress)
        self.myIP.config(state=DISABLED)


        self.btnServer = Button(self.panelSettings, text="Start server", command=self.startServerThread)
        self.btnServer.grid(row=7, column=0, columnspan=2, sticky=N+E+W, pady=5)


        self.panelSettings.grid(row=0, column=0, sticky=N, padx=5)
        


        # Panel Chat
        self.panelChat = Frame(self.mainFrame)
        
        self.chat = Text(self.panelChat)
        self.chat.config(state=DISABLED)
        self.chat.grid(row=0, column=0)

        self.input = Entry(self.panelChat)
        self.input.grid(row=1,column=0, sticky=N+E+W, pady=5)
        self.input.bind('<Return>', self.actionSendMessage)
        
        self.panelChat.grid(row=0, column=1, padx=4, pady=3)
        
    def updateAsConnected(self):
        self.btnConnect.config(text="Disconnect", command=self.actionDisconnect)
        self.labelStatus.config(text="Online", foreground="green")

        self.serverIP.configure(state='disabled')
        self.serverPort.configure(state='disabled')
        self.username.configure(state='disabled')


    def updateAsDisconnected(self):
        self.btnConnect.config(text="Connect", command=self.actionConnect)
        self.labelStatus.config(text="Offline", foreground="red")


    def actionConnect(self) :       
        host = self.serverIP.get()
        port = self.serverPort.get()
        username = self.username.get()

        if not host or not port or not username:
            self.showMessageBox('error', "One of the field is empty, please fill in all of the fields.")
            return
        
            
        response = self.clientControl.connect(host, port, username)
        if response == ClientCode.NAME_TAKEN:
            return
        elif response == ClientCode.CONNECTION_SUCCESSFUL:
            ChatWindow.showMessageBox('info', "Connection successful! Motherfucker!")
            self.updateAsConnected() 
            self.checkMessagesLoop()

    def actionDisconnect(self):
        self.clientControl.leaveRoom()
        self.updateAsDisconnected()


    def actionSendMessage(self, ev):
        response = self.clientControl.processInput(self.input.get())
        if response == ClientCode.COMMAND_USERS:
            self.printUsersList()
        elif response == ClientCode.COMMAND_HELP:
            self.printHelpMenu()


    def startServerThread(self):
        serverThread = Thread(target=self.startServer)
        ChatWindow.showMessageBox('info', "Server Started")
        serverThread.start()

    def startServer(self):
        print("starting server...")
        self.server = PyServer(self.myIP.get())
        self.server.start()
        

    def actionStopServer(self):
        self.server.shutdown()





    def  checkMessagesLoop(self):
        msg = self.clientControl.fetchMessages()
        if msg:
            self.insertChatLine(msg)
        self.root.after(20, self.checkMessagesLoop)





    def printUsersList(self):
        users = self.server.getUsers()
        self.insertChatLine("==============================================")
        self.insertChatLine("Connected users (%s):"%len(users))
        for user in users:
            if user == self.username:
                self.insertChatLine("*"+user)
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
        line = line + "\n"
        self.chat.config(state=NORMAL)
        self.chat.insert(END, line)
        self.chat.config(state=DISABLED)
        self.input.delete(0, END)



        
    @staticmethod
    def showMessageBox(msgType, msg):
        if msgType == 'info':
            messagebox.showinfo("Chat", msg)
        elif msgType == 'error':
            messagebox.showerror("Chat", msg)
        elif msgType == 'warning':
            messagebox.showwarning("Chat", msg)
        







def main():
    c = Client()
    w = ChatWindow(c)








if __name__ == '__main__':
    main()
