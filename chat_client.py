#!/usr/bin/python3

# This is a simple socket experiment 
# chat client.
#
# Version 0.1 as of 26 September 2017
#
# Created by Trevor Bautista
#
#########################################

# import the socket module 
import socket
# import system and getopt module for parsing arguments in CLI
import sys
import getopt
# import threading tools for multithreading
import threading


# class for a thread to listen for messages
class ListenThread(threading.Thread):
    def __init__(self, threadID, name, socket):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket

    def run(self):
        while True:
            new_msg = self.socket.recv(1024).decode('ascii')
            print(new_msg)

# class for a thread to send messages
class SendThread(threading.Thread):
    def __init__(self, threadID, name, socket):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket

    def run(self):
        while True:
            msg = input()
            self.socket.send(msg.encode('ascii'))



def main(argv):

    # text to display if wrong parameters
    usage = """
    Usage: python chat_client [-h] [HOST PORT] 

        Parameters:
        ------------------------------------
        -h  display this help
        -n, --name= name of client
        -t, --type= connection type
    """

    # exit codes
    SUCCESS           = 0
    GENERAL_FAILURE   = 1
    INVALID_PARAMETER = 2
    CONNECTION_ERROR  = 3

    # host (set to default localhost)
    HOST="localhost"
    # port (set to default)
    PORT = 12345
    # protocol (TCP or UDP)
    PROTOCOL="tcp"
    # name for client
    NAME="Anonymous"


    # if no parameters or the '-h' parameter, print the usage
    if (len(sys.argv)<=1 or sys.argv[1]=="-h"):
        print(usage)
    else:
        # try to assign host and port parameters
        try:
            HOST = sys.argv[1]
            PORT = int(sys.argv[2])
        # if type exception, let user know and exit with exit code for invalid parameter
        except (TypeError, ValueError):
            print("Invalid host/port.")
            print(usage)
            sys.exit(INVALID_PARAMETER)

        # try to get argument list
        try:
            opts, args = getopt.getopt(argv[2:],"n:t:",["name=","type="])
        # if error in getting arguments,
        except getopt.GetoptError:
            # print usage and exit with exit code for general failure
            print(usage)
            sys.exit(GENERAL_FAILURE)

        # for each option in option list,
        for opt, arg in opts:
            # if help option,
            # if name option,
            if (opt in ("-n","--name")):
                # set name to argument
                NAME = arg
            # if protocol option
            elif (opt in ("-t", "--type")):
                # if type is 'tcp', use type tcp
                if (arg.lower() == "tcp"):
                    PROTOCOL="tcp"
                # if type is 'udp', use type udp
                elif (arg.lower() == "udp"):
                    PROTOCOL="udp"
                # if anything else, notify of error and exit with exit code for invalid parameter
                else:
                    print("Invalid protocol type:", arg)
                    print(usage)
                    sys.exit(INVALID_PARAMETER)
            # if anything else,
            else:
                # let user know and exit with exit code for invalid parameter
                print("Invalid argument(s):", arg)
                sys.exit(INVALID_PARAMETER)

        print("Host:", HOST, "Port:", PORT, "Protocol:", PROTOCOL, "Name:", NAME, opts, args)

        if (PROTOCOL == "tcp"):
            # try to initialize socket
            try:
                # socket initialization
                print("\nCreating socket...")
                clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # create a socket object
                print("Connecting to host", HOST, "with port", PORT, "...")
                clientsocket.connect( (HOST,PORT) )                                 # actively initiate TCP connection with host and port
            except (OSError):
                print("Error in connecting.")
                sys.exit(CONNECTION_ERROR)

            while True:
                # get server's response
                print("Listening to server...")
                msg = clientsocket.recv(1024)                                       #receive 1024 bytes from server (TCP)
                print(msg.decode('ascii'))

                # send name to server
                print("Sending name to server...")
                msg = NAME
                clientsocket.send(msg.encode('ascii'))

                # close connection
                #clientsocket.close()
                #print("Connection closed")
                break

            # create send and receive threads
            send_thread = SendThread(1, "Send-Thread", clientsocket)
            listen_thread = ListenThread(2, "Listen-Thread", clientsocket)
            # start threads
            send_thread.start()
            listen_thread.start()
            #msg = input()
            #clientsocket.send(msg.encode('ascii'))
            #new_msg = clientsocket.recv(1024).decode('ascii')
            #print(new_msg)



        elif (PROTOCOL == "udp"):
            print("udp")






if __name__ == "__main__":
    main(sys.argv[1:])

