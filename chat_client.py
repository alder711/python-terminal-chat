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
# import curses windowing system
import curses


# class for a thread to listen for messages
class ListenThread(threading.Thread):
    def __init__(self, threadID, name, socket, input_window, display_window):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket
        self.display_window = display_window
        self.input_window = input_window

    def run(self):
        # get max coordinates of display window
        self.DISP_Y, self.DISP_X = self.display_window.getmaxyx()
        while True:
            # get new message from socket
            new_message = self.socket.recv(1024).decode('ascii')
            # for each previous line in the display window,
            for i in range(2,self.DISP_Y-1):
                # store line
                old_strs = self.display_window.instr(i,1,self.DISP_X)
                # rewrite previous line with next line
                self.display_window.addstr(i-1,1,old_strs)
            # move cursor to bottom of display window
            self.display_window.move(self.DISP_Y-2,1)
            # clear old message here
            self.display_window.addstr(self.DISP_Y-2,1," "*(self.DISP_X-1))
            # place new message here
            self.display_window.addstr(self.DISP_Y-2,1,new_message)
            # redraw border for diplay window
            self.display_window.border()
            # refresh display window
            self.display_window.refresh(0,0,0,0,self.DISP_Y,self.DISP_X)

            #new_msg = self.socket.recv(1024).decode('ascii')
            #print(new_msg)

# class for a thread to send messages
class SendThread(threading.Thread):
    def __init__(self, threadID, name, socket, input_window, display_window):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket
        self.display_window = display_window
        self.input_window = input_window
        

    def run(self):
        # get max coordinates of display window
        self.DISP_Y, self.DISP_X = self.display_window.getmaxyx()
        while True:
            # get user input at prompt (wait for return key)
            self.input_window.getstr(1,1)
            # store message
            message = self.input_window.instr(1,1,self.DISP_X)
            # clear prompt
            self.input_window.clear()
            # redraw input window border
            self.input_window.border()
            # replace cursor at prompt
            self.input_window.move(1,1)
            # refresh input window
            self.input_window.refresh()
            # for each previous line in the display window,
            for i in range(2,self.DISP_Y-1):
                # store line
                old_strs = self.display_window.instr(i,1,self.DISP_X)
                # rewrite previous line with next line
                self.display_window.addstr(i-1,1,old_strs)
            # move cursor to bottom of display window
            self.display_window.move(self.DISP_Y-2,1)
            # place new message here
            self.display_window.addstr(self.DISP_Y-2,1,message)
            # redraw border for diplay window
            self.display_window.border()
            # refresh display window
            self.display_window.refresh(0,0,0,0,self.DISP_Y,self.DISP_X)
            # send message
            self.socket.send(message)



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

    

    # # forever,
    # while True:
    #     # get user input at prompt (wait for return key)
    #     input_win.getstr(1,1)
    #     # store message
    #     message = input_win.instr(1,1,X)
    #     # clear prompt
    #     input_win.clear()
    #     # redraw input window border
    #     input_win.border()
    #     # replace cursor at prompt
    #     input_win.move(1,1)
    #     # refresh input window
    #     input_win.refresh()
    #     # for each previous line in the display window,
    #     for i in range(2,DISP_Y-1):
    #         # store line
    #         old_strs = disp_win.instr(i,1,X)
    #         # rewrite previous line with next line
    #         disp_win.addstr(i-1,1,old_strs)
    #     # move cursor to bottom of display window
    #     disp_win.move(DISP_Y-2,1)
    #     # place new message here
    #     disp_win.addstr(DISP_Y-2,1,message)
    #     # refresh display window
    #     disp_win.refresh(0,0,0,0,Y-3,X-2)



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

            # create new main window
            stdscr = curses.initscr()
            # get max coordinates of main window
            Y,X = stdscr.getmaxyx()
            # create window to display chat content
            disp_win = curses.newpad(Y-3,X)
            # get max coordinates of display window
            DISP_Y, DISP_X = disp_win.getmaxyx()
            # draw border around display window
            disp_win.border()
            # create input window for inputting chat
            input_win = curses.newwin(3,X,Y-3,0)
            # get max coordinates of input window
            INPUT_Y, INPUT_X = input_win.getmaxyx()
            # draw border around input window
            input_win.border()
            # move cursor to prompt of input window
            input_win.move(1,1)
            # refresh display window
            disp_win.refresh(0,0,0,0,DISP_Y,DISP_X)
            # refresh input window
            input_win.refresh()

            # create send and receive threads
            send_thread = SendThread(1, "Send-Thread", clientsocket,input_win, disp_win)
            listen_thread = ListenThread(2, "Listen-Thread", clientsocket,input_win, disp_win)
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

