#!/usr/bin/env python3

# This is a simple socket experiment 
# chat for peer-to-peer.
#
# Version 0.2 as of 02 February 2018
#
# Created by Trevor Bautista
#
#########################################

# import the socket module 
import socket
from socket import error as socket_error
# import system and getopt module for parsing arguments in CLI
import sys
import getopt

# import threading tools for multithreading
import threading
# import curses windowing system
import curses
#import json for serializing messages
import json


class Chat():

	def __init__(self, argv):
		self.argv = argv
		# text to display if wrong parameters
		self.usage = """
	Usage: python chat_server [-h][-p PORT]

		Parameters:
		------------------------------------
		-c, --clients=  maximum number of peers to allow connection (default 5)
		-h              display this help
		-n, --name=     set name of local peer
		-q, --lhost=    local hostname/IP to connect with (default is 0.0.0.0)
		-p, --lport=    specify a local port to listen with (default 12345)
		-r, --rhost=    specify a remote hostname/IP to connect to
		-s, --rport=    specify a remote port to connect to
		-t, --type=     specify a protocol to use (default tcp) [tcp|udp]
	"""

		# exit codes
		self.SUCCESS           = 0
		self.GENERAL_FAILURE   = 1
		self.INVALID_PARAMETER = 2
		self.CONNECTION_ERROR  = 3

		# categories for info in chat window
		self.INFO = "[INFO]"
		self.ERR  = "[ERR] "

		# remote hostname/IP to connect to (set to nothing initially, since no initial server)
		self.REMOTEHOST = "" # optional: can be just server
		# local hostname/IP to connect with
		self.LOCALHOST = "0.0.0.0" # '0.0.0.0' binds to all interfaces
		# port to listen on (set to default)
		self.LISTENPORT = 12345
		# port to send to (set to invalid port initially, since no initial server)
		self.SENDPORT = 0
		# protocol to use (TCP or UDP) (default tcp)
		self.PROTOCOL="tcp"
		# name of local chat peer (for chat name)
		self.NAME="Anonymous"
		# number of peers to allow connection
		self.PEERS=5
		# sockets
		self.peersocket = None
		self.hostsocket = None

		# peer names
		self.peer_names = []

		# start main()
		self.main(self.argv)

	###################################################################################
	############### THREAD OBJECTS ####################################################
	###################################################################################

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
	            new_data = self.socket.recv(1024).decode('ascii')
	            new_data = json.loads(new_data)
	            new_prefix = "["+str(new_data['name'])+"] "
	            new_message = new_prefix+new_data["message"]
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
	            # replace cursor at prompt
	            self.input_window.move(1,1)
	            # refresh display window
	            self.display_window.refresh(0,0,0,0,self.DISP_Y,self.DISP_X)

	            #new_msg = self.socket.recv(1024).decode('ascii')
	            #print(new_msg)

	# class for a thread to send messages
	class SendThread(threading.Thread):
	    def __init__(self, threadID, name, socket, input_window, display_window, local_name):
	        threading.Thread.__init__(self)
	        self.threadID = threadID
	        self.name = name
	        self.socket = socket
	        self.display_window = display_window
	        self.input_window = input_window
	        self.local_name = local_name
	        

	    def run(self):
	        # get max coordinates of display window
	        self.DISP_Y, self.DISP_X = self.display_window.getmaxyx()
	        while True:
	            # get user input at prompt (wait for return key)
	            self.input_window.getstr(1,1)
	            # store message
	            message = self.input_window.instr(1,1,self.DISP_X).decode('utf-8')
	            data = "{"+"\"name\""+":"+"\""+str(self.local_name)+"\""+","+"\""+"message"+"\""+":"+"\""+str(message)+"\""+"}"
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
	            self.display_window.addstr(self.DISP_Y-2,1,"["+self.local_name.upper()+"] "+message)
	            # redraw border for diplay window
	            self.display_window.border()
	            # refresh display window
	            self.display_window.refresh(0,0,0,0,self.DISP_Y,self.DISP_X)
	            # send message
	            self.socket.send(data.encode('utf-8'))


	###################################################################################
	############### HELPER METHODS ####################################################
	###################################################################################


	# print text on display window
	def print_disp(self, window, content, prefix=""):
	    Y,X = window.getmaxyx()
	    # for each previous line in the display window,
	    for i in range(2,Y-1):
	        # store line
	        old_strs = window.instr(i,1,X)
	        # rewrite previous line with next line
	        window.addstr(i-1,1,old_strs)
	    # move cursor to bottom of display window
	    window.move(Y-2,1)
	    # place new content here
	    window.addstr(Y-2,1,prefix+" "+content)
	    # redraw border for diplay window
	    window.border()
	    window.refresh(0,0,0,0,Y,X)



	# clean up all sockets and windows
	def cleanup(self, sockets, windows=[]):
	    # for each socket,
	    for socket in sockets:
	    	# if socket is initialized,
	    	if (socket != None):
	    		# close socket
	        	socket.close()
	    # for each window,
	    for window in windows:
	        stdscr.keypad(False)
	    curses.echo()
	    curses.endwin()
	    curses.nocbreak()
	    #peersocket.close()
	    #print("Connection closed")



	###################################################################################
	############### MAIN EXECUTION ####################################################
	###################################################################################


	def main(self, argv):
	    # try to get argument list
	    try:
	        opts, args = getopt.getopt(argv,"c:hn:p:q:t:",["clients=","name=","lhost=","lport=","rhost=","rport=","type="])
	    # if error in getting arguments,
	    except getopt.GetoptError:
	        # print usage and exit with exit code for general failure
	        print(self.usage)
	        sys.exit(self.GENERAL_FAILURE)

	    # for each option in option list,
	    for opt, arg in opts:
	        # if help option,
	        if (opt == '-h'):
	            # print usage and exit successfuly
	            print(self.self.usage)
	            sys.exit(self.self.SUCCESS)
	        # if clients option,
	        elif (opt in ("-c","--clients")):
	            # test if integer
	            try:
	                val = int(arg)
	            # if not integer,
	            except ValueError:
	                # notify user and exit with exit code for invalid parameter
	                print("Invalid client number:", arg)
	                print(self.self.usage)
	                sys.exit(self.self.INVALID_PARAMETER)
	            # set port
	            self.self.PEERS = int(arg) 
	        # if name option,
	        elif (opt in ("-n","--name")):
	            # try to assign name
	            try:
	                self.self.NAME = arg
	            # if type exception, let user know and exit with exit code for invalid parameter
	            except (TypeError, ValueError):
	                print("Invalid name.")
	                print(self.self.usage)
	                sys.exit(self.self.INVALID_PARAMETER)
	        # if (listen) port option,
	        elif (opt in ("-p","--lport")):
	            # test if integer
	            try:
	                val = int(arg)
	            # if not integer,
	            except ValueError:
	                # notify user and exit with exit code for invalid parameter
	                print("Invalid listen port", arg)
	                print(self.usage)
	                sys.exit(self.INVALID_PARAMETER)
	            # set port
	            self.LISTENPORT = int(arg) 
	        # if local hostname/IP option,
	        elif (opt in ("-q","--lhost")):
	            # try to assign host
	            try:
	                self.LOCALHOST = arg
	            # if type exception, let user know and exit with exit code for invalid parameter
	            except (TypeError, ValueError):
	                print("Invalid local host.")
	                print(self.usage)
	                sys.exit(self.INVALID_PARAMETER)
	        # if remote hostname/IP option,
	        elif (opt in ("-r","--rhost")):
	            # try to assign host
	            try:
	                self.REMOTEHOST = arg
	            # if type exception, let user know and exit with exit code for invalid parameter
	            except (TypeError, ValueError):
	                print("Invalid remote host.")
	                print(self.usage)
	                sys.exit(self.INVALID_PARAMETER)
	        # if (remote) port option,
	        elif (opt in ("-s","--rport")):
	            # test if integer
	            try:
	                val = int(arg)
	            # if not integer,
	            except ValueError:
	                # notify user and exit with exit code for invalid parameter
	                print("Invalid remote port", arg)
	                print(self.usage)
	                sys.exit(self.INVALID_PARAMETER)
	            # set remote port
	            self.SENDPORT = int(arg) 
	        # if protocol option,
	        elif (opt in ("-t","--protocol")):
	            # if 'tcp' option, set protocol to tcp
	            if (arg.lower() == "tcp"):
	                self.PROTOCOL="tcp"
	            # if 'udp' option, set protocol to udp
	            elif (arg.lower() == "udp"):
	                self.PROTOCOL="udp"
	            # if invalid option, print usage and exit with exit code for invalid parameter
	            else:
	                print("Invalid protocol:", arg)
	                print(self.usage)
	                sys.exit(self.INVALID_PARAMETER) 
	        # if anything else,
	        else:
	            # let user know and exit with exit code for invalid parameter
	            print("Invalid argument(s):", arg)
	            sys.exit(self.INVALID_PARAMETER)

	    
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

	    self.print_disp(disp_win,"Local Host/Port: "+str(self.LOCALHOST)+":"+str(self.LISTENPORT)+" Protocol: "+str(self.PROTOCOL)+" Max Peers: "+str(self.PEERS), self.INFO)


	    if (self.PROTOCOL == "tcp"):
	        # try to initialize socket
	        try:
	            # if the host (no initial connection attempt to remote peer),
	            if (self.REMOTEHOST == ""):
	                # socket initialization for local host
	                self.print_disp(disp_win,"\nCreating local host socket...",self.INFO)
	                hostsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object
	                self.print_disp(disp_win,"Getting local hostname...",self.INFO)
	                self.print_disp(disp_win,"Local hostname"+str(self.LOCALHOST),self.INFO)
	                self.print_disp(disp_win,"Binding to port "+str(self.LISTENPORT)+"...",self.INFO)
	                hostsocket.bind( (self.LOCALHOST,self.LISTENPORT) )                             # bind to the port
	                self.print_disp(disp_win,"Local host:\t"+str(self.LOCALHOST)+"\nPort:\t"+str(self.LISTENPORT),self.INFO)
	                # listen for client connection (up to 5 requests)
	                self.print_disp(disp_win,"Listening for peer (max "+str(self.PEERS)+")...",self.INFO)
	                hostsocket.listen(self.PEERS)
	            # if the peer (initial connection attempt to remote peer),
	            else:
	                # socket initialization for peer(s) if HOST specified
	                self.print_disp(disp_win,"\nCreating peer(s) socket...",self.INFO)
	                peersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # create a socket object
	                self.print_disp(disp_win,"Connecting to peer "+str(self.REMOTEHOST)+" with port "+str(self.SENDPORT)+"...",self.INFO)
	                peersocket.connect( (self.REMOTEHOST,self.SENDPORT) )                                 # actively initiate TCP connection with host and port
	        except (OSError, socket_error, ConnectionRefusedError) as err:
	            self.print_disp(disp_win,"Error in connecting:"+str(err),self.ERR)
	            self.cleanup([hostsocket,peersocket])
	            sys.exit(self.CONNECTION_ERROR)

	        


	        while True:
	            # if the host (no initial connection was attempted to remote peer),
	            if (self.REMOTEHOST == ""):
	                # establish connection to client
	                peersocket, addr = hostsocket.accept()
	                self.print_disp(disp_win, "Connection established to "+str(addr),self.INFO)
	                # send message to client
	                msg = "Connection to server established."
	                peersocket.send(msg.encode('ascii'))
	                # receive name from client
	                new_name = peersocket.recv(1024).decode('ascii')
	                self.print_disp(disp_win,"New peer connected:"+str(new_name),self.INFO)
	                peer_names.append(new_name)
	            #if the peer,
	            # else:
	            #     # establish connection to host
	            #     hostsocket, addr = peersocket.accept()
	            #     print("Connection established to", addr)
	            #     # send message to client
	            #     msg = "Connection to server established."
	            #     peersocket.send(msg.encode('ascii'))
	            #     # receive name from client
	            #     new_name = peersocket.recv(1024).decode('ascii')
	            #     print_disp(disp_win,"New client connected: "+str(new_name))
	            #     peer_names.append(new_name)
	            
	            break



	        # create send and receive threads
	        send_thread = self.SendThread(1, "Send-Thread", peersocket,input_win, disp_win, self.NAME)
	        listen_thread = self.ListenThread(2, "Listen-Thread", peersocket,input_win, disp_win)
	        # start threads
	        send_thread.start()
	        listen_thread.start()

	    elif (PROTOCOL == "udp"):
	        print("udp")
	    else:
	        print("unrecognized protocol")





###################################################################################
############### RUN EVERYTHING ####################################################
###################################################################################

if __name__ == "__main__":
	print(sys.argv[1:])
	runner = Chat(sys.argv[1:])

