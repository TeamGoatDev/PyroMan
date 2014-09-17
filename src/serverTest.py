import socket, base64, threading


class Server(object):
    """Server"""
    def __init__(self):

        self.users = []  # The list of users connected
        self.messages = [" "]  # The list of the sent messages
        self.idIndex = 0  # This is the index for the id given to the clients
        self.roomWatch = {}  # This is a list of rooms i.e. clients calling the server for new messages


        target = "0.0.0.0"
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.bind((target,3333))

        self.connection.listen(5)

        while True:
                client_socket, addr = self.connection.accept()
                # spin off a thread to handle our new client
                client_thread = threading.Thread(target=self.client_handler, args=(client_socket,))
                client_thread.start()

    def sendPacket(self,msg, client_socket):
        print("[+] sending packet")
        client_socket.send(self.wrap(msg))

    def receivePacket(self, client_socket):
        file_buffer = b""

        buffer_len = 1
        while buffer_len:
            data = client_socket.recv(4096)
            if not data:
                break
            else:
                file_buffer += data
                if len(data) < 4096:
                    break
        return file_buffer[2:len(file_buffer)-1].decode("UTF-8")

    def wrap(self,msg):
        enc = ""
        for plain in msg:
            enc += str(base64.b64encode(plain.encode('ascii')))+str("*")
        enc += "#"
        return bytes(enc, 'UTF-8')

    def unwrap(self,enc):
        encoded_ans = enc.split("*")
        plain_ans = []
        for item in encoded_ans:
            if item[0:2] == "b'":
                item = item[2:]
            #print(item)
            plain_ans.append(base64.b64decode(item).decode("utf-8"))
        return plain_ans

    def client_handler(self,client_socket):
        print("[+] Received connection")
        while True:
            packet = self.receivePacket(client_socket)
            if packet != '':
                msg = self.unwrap(packet)
                command = msg[0]
                print(command)

                if command == "getUsers":
                    self.sendPacket(self.getUsers(),client_socket)

                elif command == "joinRoom":
                    val = []
                    val.append(self.joinRoom(msg[1]))
                    self.sendPacket(val,client_socket)

                elif command == "getNewRoomID":
                    val = []
                    val.append(str(self.getNewRoomID()))
                    print(val)
                    self.sendPacket(val,client_socket)

                elif command == "getLastMessage":
                    self.sendPacket(self.getLastMessage(msg[1]), client_socket)

                elif command == "sendMessage":
                    self.sendPacket(self.getLastMessage(msg[1],msg[2]), client_socket)

                elif command == "leaveRoom":
                    val = []
                    val.append(self.leaveRoom(msg[1]))
                    self.sendPacket(val, client_socket)

            else:
                print("Quitting thread")
                break

    def joinRoom(self, name):
        """ Adds a new user to the Chat Room
        :param name: the name of the user willing to join
        :return:
        """
        print("%s connected" % name)
        self.sendMessage("SERVER", "'%s' IS IN THA HOOD" % name)
        self.users.append(name)
        return name + " you are connected!"

    def getUsers(self):
        """ Returns the list of users in the chat room
        :return: the list of connected users
        """
        return self.users

    def getNewRoomID(self):
        """ Used by clients to have a unique id
        :int : returns a new unique id
        """
        retid = self.idIndex
        self.idIndex += 1
        self.roomWatch[retid] = False
        return retid

    def sendMessage(self, user, msg):
        """
        :param user: the name of the user sending the message
        :param msg: the message to send
        """
        msg = user + ': ' + msg
        self.messages.append(msg)
        for room in self.roomWatch:
            self.roomWatch[room] = True

    def leaveRoom(self, user):
        """ Makes a user leave the room
        :param user: the user leaving the room
        :return:
        """
        self.users.remove(user)
        self.sendMessage('SERVER', "'%s' HAS LEFT" % user)

    def getLastMessage(self, roomID):
        """
        Returns a list of the last messages sent on the server
        :param roomID: the unique id of the room trying to get the last new messages
        :return: list of new messages
        """
        if self.roomWatch[roomID]:
            self.roomWatch[roomID] = False
            return self.messages[-1]

    def getMessages(self):
        """
        Returns the list of all the messages sent on the server
        :return: list of all the messages
        """
        return self.messages

    def getInfo(self):
        """  Returns useful information about the server
        :return: info dict{}
        """
        info = {'NAME': "PyroMan SERVER",
                'IP': socket.gethostbyname(socket.gethostname()),
                'VERSION': VERSION,
                'DEBUG': DEBUG_VERBOSE,
                'NB_CLIENTS': len(self.users)
                }
        return info

def main():
    server = Server()
if __name__ == '__main__':
    main()





