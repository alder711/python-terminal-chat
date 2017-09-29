import socket
import threading

class ListenThread(threading.Thread):
    def __init__(self, threadID, name, socket):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket


    def run(self):
        while True:
            # get new message from socket
            new_data = self.socket.recv(1024).decode('ascii')
            # place new message here
            print(new_message)

# class for a thread to send messages
class SendThread(threading.Thread):
    def __init__(self, threadID, name, socket):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket = socket

    def run(self):
        while True:
            # store message
            message = input()
            self.socket.send(data.encode('ascii'))



 # socket initialization for local host
print_disp(disp_win,"\nCreating local host socket...",INFO)
hostsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object
print_disp(disp_win,"Getting local hostname...",INFO)
print_disp(disp_win,"Local hostname"+str(LOCALHOST),INFO)
print_disp(disp_win,"Binding to port "+str(PORT)+"...",INFO)
hostsocket.bind( (LOCALHOST,PORT) )                             # bind to the port
print_disp(disp_win,"Local host:\t"+str(LOCALHOST)+"\nPort:\t"+str(PORT),INFO)
# listen for client connection (up to 5 requests)
print_disp(disp_win,"Listening for peer (max "+str(PEERS)+")...",INFO)
hostsocket.listen(PEERS)