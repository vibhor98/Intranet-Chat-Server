# Intranet-Chat-Server
This is a server-side script to handle intranet chatting. This can be handy when your Internet connection goes down / or is slow, and you need to communicate to someone in your network. 

[Demonstration video for the script.](https://www.dropbox.com/s/qc16p5bleyewq3h/Demo.mp4?dl=0)

We've used `asyncore` and `asynchat` modules from Python's standard library to handle receiving and broadcasting text in the backend. 

## How it works
#### 1. Start the server:
```
python chat_server.py
```
The server works on the port **5005**. You can set it to anything, but setting the number above 1023 is preferred. 

Once the server starts running, clients can connect to it by using the ip address of the machine running it.

We use `telnet` as a client interface to connect to the server. `telnet` comes installed in Unix-based systems. Windows users may require to install it before connecting to the server.

DISCLOSURE: Telnet is not encrypted by default and this should not be used as a way to send secure and important messages. If you are using this on a public or private network your data can be visible to those with rights to collect and inspect your data. Please use caution.

#### 2. Connect to the chat server on the client's terminal or command prompt.
```
telnet <server-ip> <port num>
```

As mentioned before, the port number is set by default to 5005. The client can be any machine on the same network as that of the server. A successful connection would yield something like the following on the client:

#### 3. Successful connection
```
*MacBookPro:~ binaryBoy$ telnet 172.22.24.23 5005
Trying 172.22.24.23...
Connected to 172.22.24.23.
Escape character is '^]'.
Welcome to LNMChat!
Type login <name> to enter the chat room.
Type say <message> to send your message.
Type "who" to see the users in your chat room.
Type "look" to see the users logged into the entire chat server.
Finally, use "logout" to exit from the server.
```
Just like this client, other clients can also connect in the same way. Once multiple clients are connected, they can start chatting. 

The default **maximum number of clients**  - 5.
You can set it to any number of your preference, by changing [line 155](https://github.com/Pin4in/Intranet-Chat-Server/blob/master/chat_server.py#L155)


Currently, the code doesn't notify the users whether some user is already typing a message. So,  bit of patience and discipline is required from each user, to maintain the output clean.

To add such a functionality, a function like `found_terminator()` of `ChatSession` class can be used to detect keystrokes from a session(i.e, a user). We shall soon add this functionality.
