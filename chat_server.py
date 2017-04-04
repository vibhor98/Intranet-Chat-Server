from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore

PORT = 5005
NAME = "LNMChat"

class EndSession(Exception): pass

class CommandHandler:
    '''class to handle commands, apart from just message text'''

    def unknown(self, session, cmd):
        session.push('Unknown command: %s\r\n' % cmd)

    def handle(self, session, line):
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
    '''An environment which may contain multiple users (sessions). Takes care of basic command handling and broadcasting.'''
    def __init__(self, server):
        self.server = server
        self.sessions = []

    def add(self, session):
        self.sessions.append(session)
    def remove(self, session):
        self.sessions.remove(session)
    def broadcast(self, line):
        for session in self.sessions:
            session.push(line)
    def do_logout(self, session, line):
        raise EndSession

class LoginRoom(Room):
    '''Meant for a single user who has just connected.'''
    def add(self, session):
        Room.add(self, session)
        self.broadcast('Welcome to %s!\r\n' % self.server.name)
        self.broadcast('Type login <name> to enter the chat room.\r\n')
        self.broadcast('Type say <message> to send your message.\r\n')
        self.broadcast('Type "who" to see the users in your chat room.\r\n')
        self.broadcast('Type "look" to see the users logged into the entire chat server.\r\n')
        self.broadcast('Finally, use "logout" to exit from the server.\n\r\n')

    def unknown(self, session, cmd):
        #All unknown commands except login/logout. Prompts:
        session.push('Please login\nUse login <nick>\r\n')
    def do_login(self, session, line):
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
    '''This is meant for multiple users who can chat with others in the room.'''
    def add(self, session):
        #notify others about the new users
        self.broadcast(session.name + ' has entered the room.\r\n')
        self.server.users[session.name] = session
        Room.add(self, session)
    def remove(self, session):
        Room.remove(self, session)
        #notify everyone that the user has left the room.
        self.broadcast(session.name+" has left the room.\r\n")
    def do_say(self, session, line):
        self.broadcast(session.name+": "+line+"\r\n")
    def do_look(self, session, line):
        session.push("Following users are in the room:\r\n")
        for other in self.sessions:
            session.push(other.name+"\r\n")
        session.push("\r\n")
    def do_who(self, session, line):
        #to see who are logged in
        session.push("\nFollowing users are logged in:\r\n")
        for name in self.server.users:
            session.push(name+"\r\n")
        session.push("\r\n")

class LogoutRoom(Room):
    '''Room for a single user. Just removes the user's name from the server.'''
    def add(self, session):
        #adding the user here just deletes the user's name from the server
        try:
            del self.server.users[session.name]
        except KeyError:
            pass

class ChatSession(async_chat):
    '''Takes care of a connection between the server and a client'''

    def __init__(self, server, sock):
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

        try:
            cur = self.room
        except AttributeError:
            pass
        else: cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):
        self.data.append(data)
    def found_terminator(self):
        '''terminator is found when a full line is read. Then the message is broadcast to everyone'''

        line = ''.join(self.data)
        self.data = []
        try:
            self.room.handle(self, line)
        except EndSession:
            self.handle_close()
        #self.server.broadcast(line)
    def handle_close(self):
        async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server))


class ChatServer(dispatcher):
    '''this class handles individual sessions and creates them. Also, it handles broadcast.'''

    def __init__(self, port, name):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(5)
        self.name = name
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self):
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
