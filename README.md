# Intranet-Chat-Server
This is a server-side script to handle intranet chatting. This can be handy when your Internet connection goes down / or is slow, and you need to communicate to someone in your network. We've used `asyncore` and `asynchat` modules from Python's standard library to handle recieving and broadcasting text in the backend. Simply execute the script by typing `python chat_server.py` to start the server. 

The port for server connection has been set to 5005. You can set it to anything, but setting the number above 1023 is preferred. Once the server starts running, clients can connect to it by using the ip address of the machine running it.

We use `telnet` as a client interface to connect to the server. `telnet` comes installed in Unix-based systems. Windows users may require to install it before connecting to the server.

To connect to the chat server, type `telnet <server-ip> <port num>` on the client's terminal or command prompt.  As mentioned before, the port number is set by default to 5005. The client can be any machine on the same network as that of the server. A suucessful connection would yield something like the following on the client:

*MacBookPro:~ binaryBoy$ telnet 172.22.24.23 5005<br />
Trying 172.22.24.23...<br />
Connected to 172.22.24.23.<br />
Escape character is '^]'.<br />
Welcome to LNMChat!<br />
Type login <name> to enter the chat room.<br />
Type say <message> to send your message.<br />
Type "who" to see the users in your chat room.<br />
Type "look" to see the users logged into the entire chat server.<br />
Finally, use "logout" to exit from the server.<br />*

Just like this client, other clients can also connect in the same way. Once multiple clients are connected, they can start chatting. 

Currently, the code doesn't notify the users whether some user is already typing a message. So,  bit of patience and discipline is required from each user, to maintain the output clean.

To add such a functionality, a function like `found_terminator()` of `ChatSession` class can be used to detect keystrokes from a session(i.e, a user). We shall soon add this functionality.

Here's a [demonstration video for the script.](https://www.dropbox.com/s/qc16p5bleyewq3h/Demo.mp4?dl=0)
