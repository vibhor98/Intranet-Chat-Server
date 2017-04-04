# Intranet-Chat-Box
This is a server-side script to handle intranet chatting. We've used `asyncore` and `asynchat` modules from Python's standard library to handle recieving and broadcasting text in the backend. Simply execute the script to start the server; the port has been set to 5005. You can set it to anything, but setting the number above 1023 is preferred. Once the server starts running, clients can connect to it by using the ip address of the machine running it.

We use `telnet` as a client interface to connect to the server. `telnet` comes installed in Unix-based systems. Windows users may require to install it before connecting to the server.

To connect to the chat server, type `telnet <server-ip> <port num>` on the client. As mentioned before, the port number is set by default to 5005. A suucessful connection would yield something like the following on the client:

`MacBookPro:~ binaryBoy$ telnet 172.22.24.23 5005
Trying 172.22.24.23...
Connected to 172.22.24.23.
Escape character is '^]'.
Welcome to LNMChat!
Type login <name> to enter the chat room.
Type say <message> to send your message.
Type "who" to see the users in your chat room.
Type "look" to see the users logged into the entire chat server.
Finally, use "logout" to exit from the server.`

