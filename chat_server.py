from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore
PORT = 5005
NAME = "LNMChat"

class EndSession(Exception): pass

class CommandHandler:
    """class to handle commands, apart from just message text"""

    def unknown(self, session, cmd):
        """Handles unknown commands

        Args:
            session (ChatSession): The user who used the command.
            cmd (string): The command that was used.
        """
        session.push('Unknown command: %s\r\n' % cmd)
        
    ''' handle is defined here'''

    def handle(self, session, line):
        """Method to handle commands.
        Checks if user did input anything and parses the command from the input.

        Args:
            session (ChatSession): The user that used the command.
            line (string): The message that was sent, command will be parsed from this.

        Raises:
            IndexError: If user's input was only one word. Sets line to empty string.
            TypeError: If command was not found.
        """
        if not line.strip():
            return
        parts = line.split(' ', 1)
        cmd = parts[0]
        try:
            line = parts[1].strip() + "\n"
        except IndexError: line=''
        meth = getattr(self, 'do_'+cmd, None)
        try:
            meth(session, line)
        except TypeError:
            self.unknown(session, cmd)

class Room(CommandHandler):
    """An environment which may contain multiple users (sessions). Takes care of basic command handling and broadcasting."""
    def __init__(self, server):
        """Init method
        Sets connected sessions to empty array.

        Args:
            server (ChatServer): The server whose users we want to handle.
        """
        self.server = server
        self.sessions = []

    def add(self, session):
        """Method to add a new session to the room sessions.
        Args:
            session (ChatSession): The user we want to add to the server.
        """
        self.sessions.append(session)
    def remove(self, session):
        """Method to remove user session from the room sessions.
        Args:
            session (ChatSession): The user we want to remove from the server.
        """
        self.sessions.remove(session)
    def broadcast(self, line):
        """Broadcasts specified line to all sessions in the room.
        Args:
            line (string): The line to broadcast to all sessions.
        """
        for session in self.sessions:
            session.push(line)
    def do_logout(self, session, line):
        """Method to logout from the room and end the session.
        Args:
            session (ChatSession): The session to end.
            line (string): ?
        """
        raise EndSession

class LoginRoom(Room):
    """Meant for a single user who has just connected. Takes a room the user connects to as argument."""
    def add(self, session):
        """Adds the user session to room and prints a welcome message and instructions to the connected user.
        Args:
            session (ChatSession): The user to add to the room.
        """
        Room.add(self, session)
        self.broadcast('Welcome to %s!\r\n' % self.server.name)
        self.broadcast('Type login <name> to enter the chat room.\r\n')
        self.broadcast('Type say <message> to send your message.\r\n')
        self.broadcast('Type "who" to see the users in your chat room.\r\n')
        self.broadcast('Type "look" to see the users logged into the entire chat server.\r\n')
        self.broadcast('Finally, use "logout" to exit from the server.\n\r\n')

    def unknown(self, session, cmd):
        """Handles unknown commands aka everything else except login/logout.

        Args:
            session (ChatSession): The user who used the command.
            cmd (string): The command that was used.
        """

        #All unknown commands except login/logout. Prompts:
        session.push('Please login\nUse login <nick>\r\n')
    def do_login(self, session, line):
        """Method to login.
        Checks if user has given a name and if it already exists in the selected server.
        Enters the user into the main room if name doesn't exist.

        Args:
            session (ChatSession): The session which is joining.
            line (string): The name the user wants to be seen as.
        """
        name = line.strip()
        if not name:
            session.push('Please enter a name\r\n')
        elif name in self.server.users:
            session.push("The name %s is already taken.\r\n" % name)
            session.push("Please try again.\r\n")
        else:
            session.name = name
            session.enter(self.server.main_room)

class ChatRoom(Room):
    """This is meant for multiple users who can chat with others in the room."""
    def add(self, session):
        """Method to add a new user to the room.
        Broadcasts a notice message to others and adds the user to the server's users.

        Args:
            session (ChatSession): The user that joins the room.
        """
        #notify others about the new users
        self.broadcast(session.name + ' has entered the room.\r\n')
        self.server.users[session.name] = session
        Room.add(self, session)
    def remove(self, session):
        """Method to remove a user from the room.
        Removes the user from the room and broadcasts a notice to others in the room.

        Args:
            session (ChatSession): The user to remove from the room.
        """
        Room.remove(self, session)
        #notify everyone that the user has left the room.
        self.broadcast(session.name+" has left the room.\r\n")
    def do_say(self, session, line):
        """Method to send user's message to others in the room.
        Args:
            session (ChatSession): The user that sends the message.
            line (string): The message user wants to send.
        """
        self.broadcast(session.name+": "+line+"\r\n")
    def do_look(self, session, line):
        """Method to get a list of users in the room.
        Args:
            session (ChatSession): The user that used the command.
            line (string): ?
        """
        session.push("Following users are in the room:\r\n")
        for other in self.sessions:
            session.push(other.name+"\r\n")
        session.push("\r\n")
    def do_who(self, session, line):
        """Method to get a list of all users who are logged in.

        Args:
            session (ChatSession): The user that used the command.
            line (string): ?
        """
        #to see who are logged in
        session.push("\nFollowing users are logged in:\r\n")
        for name in self.server.users:
            session.push(name+"\r\n")
        session.push("\r\n")

class LogoutRoom(Room):
    """Room for a single user. Just removes the user's name from the server."""
    def add(self, session):
        """Method to remove user's name from the server.

        Args:
            session (ChatSession): The user whose name will be removed from the server.

        Raises:
            KeyError: If user's name doesn't exist in the server.
        """
        #adding the user here just deletes the user's name from the server
        try:
            del self.server.users[session.name]
        except KeyError:
            pass

class ChatSession(async_chat):
    """Takes care of a connection between the server and a client"""

    def __init__(self, server, sock):
        """Init method.

        Args:
            server (ChatServer): The server to connect to.
            sock (): The socket given to the user.
        """
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator("\r\n")
        self.data = []
        self.name = None
        #all sessions begin in a separate login room.
        self.enter(LoginRoom(server))

        #following greets the user
        #self.push("Welcome to %s!\r\n" % self.server.name)

    def enter(self, room):
        """Method to enter to the room.

        Args:
            room (ChatRoom): The room to enter to.

        Raises:
            AttributeError: If room doesn't exist.
        """
        try:
            cur = self.room
        except AttributeError:
            pass
        else: cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):
        """Method to store connection data.

        Args:
            data (): Data to append to server data.
        """
        self.data.append(data)
    def found_terminator(self):
        """terminator is found when a full line is read. Then the message is broadcast to everyone

        Raises:
            EndSession: Ends the session if there is no rooms.
        """

        line = ''.join(self.data)
        self.data = []
        try:
            self.room.handle(self, line)
        except EndSession:
            self.handle_close()
        #self.server.broadcast(line)
    def handle_close(self):
        """Method to handle session closing."""
        async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server))


class ChatServer(dispatcher):
    """this class handles individual sessions and creates them. Also, it handles broadcast."""

    def __init__(self, port, name):
        """Init method.
        Starts the server in port and with name given.

        Args:
            port (int): The port to run the server in.
            name (string): The name for the server.
        """
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(5)
        self.name = name
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self):
        """Method to handle new session connection."""
        conn, addr = self.accept()
        #print "Connection attempt from: ", addr[0]
        #self.sessions.append(ChatSession(self, conn))
        ChatSession(self, conn)

if __name__ == "__main__":
    s = ChatServer(PORT, NAME)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print
