#!/usr/bin/python
# -*- coding: ascii -*-
"""
Code for the PyroMan server
This File is not meant to be called manually, it should only be importefd by the client
"""
import socket

import Pyro4


__author__ = 'fireraccoon'
__copyright__ = "Copyright 2014, Team GOAT"
__credits__ = ['fireraccoon', ]
__license__ = 'MIT'
__version__ = '14.09.16.1'
__maintainer__ = 'fireraccoon'
__email__ = ""
__status__ = 'Production'


# CONSTANTS
VERSION = '14.09.16.1'
DEBUG_VERBOSE = True


class PMServer(object):
    """ The server object"""

    def __init__(self, host, port=9988):
        """
        :param host: The ip address of the host
        :param port: The port on which the server should be ran
        """
        super(PMServer, self).__init__()
        self.host = host
        self.port = port
        self.daemon = Pyro4.Daemon(host=self.host, port=self.port)  # PyroDaemon
        self.uri = ""
        self.registerController()

    def registerController(self):
        """ Register the controller object the server will be using
            to the Daemon
        """
        self.uri = self.daemon.register(Controller(), "foo")

    def start(self):
        """
            Starts the server
        """
        if DEBUG_VERBOSE:
            print("Server ready at %s on port %s with URI=%s" % (self.host, self.port, self.uri))
        self.daemon.requestLoop()


class Controller(object):
    """the Main Server Controller
        This contains the methods that a client will call
        to get information
    """

    def __init__(self):
        self.users = []  # The list of users connected
        self.messages = [" "]  # The list of the sent messages
        self.idIndex = 0  # This is the index for the id given to the clients
        self.roomWatch = {}  # This is a list of rooms i.e. clients calling the server for new messages

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
    input("THIS FILE CANNOT BE LAUNCHED MANUALLY USE 'PyroManClient.py' INSTEAD...")


if __name__ == '__main__':
    main()