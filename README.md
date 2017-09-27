Python Terminal Chat
====================

Simple Python/ncurses-powered server-client(s) chat for the terminal.




Server Usage
------------

./chat_server.py [-h][-p PORT]

    -c, --clients=  maximum number of clients to allow connection (default 5)
    -h              display this help
    -p, --port=     specify port to use (default is 12345)
    -t, --type=     specify a protocol to use (default tcp)
    

Client Usage
------------

./chat_client.py [-h][HOST PORT [-nt]]

    -h          display this help
    HOST        hostname to connect to
    PORT        port to connect with
    -n, --name= set name of client (defalt is Anonymous)
    -t, --type= set connection type (default is tcp)