#!/usr/bin/python3

# This is a simple TCP socket experiment 
# chat server.
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


def main(argv):

    # text to display if wrong parameters
    usage = """
    Usage: python chat_server [-h][-p PORT]

        Parameters:
        ------------------------------------
        -c, --clients=  number of clients to allow connection (default 5)
        -h  display this help
        -p, --port=     specify a port to use
        -t, --type=     specify a protocol to use
    """

    # exit codes
    SUCCESS           = 0
    GENERAL_FAILURE   = 1
    INVALID_PARAMETER = 2

    # port (set to default)
    PORT = 12345
    # protocol (TCP or UDP)
    PROTOCOL="TCP"
    # number of clients to allow connection
    CLIENTS=5

    # try to get argument list
    try:
        opts, args = getopt.getopt(argv,"c:hp:t:",["clients=","port=","type="])
    # if error in getting arguments,
    except getopt.GetoptError:
        # print usage and exit with exit code for general failure
        print(usage)
        sys.exit(GENERAL_FAILURE)

    # for each option in option list,
    for opt, arg in opts:
        # if help option,
        if (opt == '-h'):
            # print usage and exit successfuly
            print(usage)
            sys.exit(SUCCESS)
        # if clients option,
        elif (opt in ("-c","--clients")):
            # test if integer
            try:
                val = int(arg)
            # if not integer,
            except ValueError:
                # notify user and exit with exit code for invalid parameter
                print("Invalid client number:", arg)
                print(usage)
                sys.exit(INVALID_PARAMETER)
            # set port
            CLIENTS = int(arg) 

        # if port option,
        elif (opt in ("-p","--port")):
            # test if integer
            try:
                val = int(arg)
            # if not integer,
            except ValueError:
                # notify user and exit with exit code for invalid parameter
                print("Invalid port", arg)
                print(usage)
                sys.exit(INVALID_PARAMETER)
            # set port
            PORT = int(arg) 
        # if protocol option,
        elif (opt in ("-t","--protocol")):
            # if 'tcp' option, set protocol to tcp
            if (arg.lower() == "tcp"):
                PROTOCOL="tcp"
            # if 'udp' option, set protocol to udp
            elif (arg.lower() == "udp"):
                PROTOCOL="udp"
            # if invalid option, print usage and exit with exit code for invalid parameter
            else:
                print("Invalid protocol:", arg)
                print(usage)
                sys.exit(INVALID_PARAMETER) 
        # if anything else,
        else:
            # let user know and exit with exit code for invalid parameter
            print("Invalid argument(s):", arg)
            sys.exit(INVALID_PARAMETER)

    print("Port:", PORT, "Protocol:", PROTOCOL, "Max Clients:", CLIENTS)

    # socket initialization
    print("\nCreating socket...")
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # create a socket object
    print("Getting hostname...")
    HOST = socket.gethostname()                                         # get local machine name
    print("Hostname", HOST)
    print("Binding to port", PORT, "...")
    serversocket.bind( (HOST,PORT) )                                    # bind to the port
    print("Server:\t", HOST, "\nPort:\t", PORT)

    # listen for client connection (up to 5 requests)
    print("Listening for client (max " + str(CLIENTS) + ")...")
    serversocket.listen(CLIENTS)

    while True:
        # establish connection to client
        clientsocket, addr = serversocket.accept()
        print("Connection established to", addr)
        # send message to client
        msg = "Connection to server established."
        clientsocket.send(msg.encode('ascii'))
        # close connection to client
        clientsocket.close()
        print("Connection closed")





if __name__ == "__main__":
    main(sys.argv[1:])

