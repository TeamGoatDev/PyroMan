import Pyro4







class PyServer(object):
    """The server"""
    def __init__(self, host, port=998):

        super(PyServer, self).__init__()
        self.DEBUG_VERBOSE = True

        self.host=host
        self.port=port

        self.idIndex = 0

        self.daemon=Pyro4.Daemon(host=self.host,port=self.port)

        self.registerController()



    def registerController(self):
        self.uri = self.daemon.register(Controller(),"foo") 


    def start(self):
        if self.DEBUG_VERBOSE:
            print("Server ready at %s on port %s with URI=%s"%(self.host, self.port, self.uri))
        self.daemon.requestLoop()
        


class Controller(object):
    """docstring for Controller"""
    def __init__(self):
        self.users = []
        self.messages = [" "]
        self.idIndex = 0
        self.roomWatch = {}
        
    def joinRoom(self, name):
        print("%s connected"%(name))
        self.sendMessage("SERVER", "'%s' IS IN THA HOOD"%(name))
        self.users.append(name)
        return name + " you are connected!"


    def getUsers(self):
        return self.users

    def getNewRoomID(self):
        retid = self.idIndex
        self.idIndex += 1
        self.roomWatch[retid] = False
        return retid


    def sendMessage(self, user, msg):
            m = user + ": " + msg
            self.messages.append(m)
            for room in self.roomWatch:
                self.roomWatch[room] = True

    def leaveRoom(self, user):
        self.users.remove(user)
        self.sendMessage("SERVER",  "'%s' HAS LEFT"%(user))


    def getLastMessage(self, roomID):
        if self.roomWatch[roomID]:
            self.roomWatch[roomID] = False
            return self.messages[-1]
            

    def getMessages(self):
        return self.messages


    def existe(self):
        return True





def main():
    input("THIS FILE CANNOT BE LAUNCHED MANUALLY USE 'PyroManClient.py' INSTEAD...")


if __name__ == '__main__':
    main()





