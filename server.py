import sys
import socket
import threading
from datetime import datetime


class Message:
    ID = 0

    def __init__(self, owner, msg):
        self.id = Message.ID
        Message.ID += 1

        self.owner = owner
        self.msg = msg
        self.date = datetime.now()

    def serverToString(self):
        return f'#{self.id}; {self.date}; {self.owner}; {self.msg}'

    def clientToString(self):
        return f'#{self.id}; {self.owner}: {self.msg}; {self.date}'

    def recent(self, date):
        return date > self.date


class Room:
    ID = 0

    def __init__(self, owner, participants):
        self.owner = owner
        self.participants = [owner]
        self.participants.extend(participants)
        self.media = []
        self.id = Room.ID + 1
        self.logfile = open(str(self.id)+'_messageLog.txt', 'w')
        Room.ID += 1


class Server:
    def __init__(self):
        # Load user information
        self.usercounter = 1
        users_file = open('credentials.txt')
        self.logfile = open('userlog.txt', 'w')
        self.users = {}

        for line in users_file:
            line = line.split()

            #                      password, wrong_pass_c, ban_date, file_size,
            self.users[line[0]] = [line[1], 0, datetime.now().second, ['sender', 'filename', None]]
        # -------------------------------------

        self.active_users = {}
        self.public_messages = []
        self.rooms = {}

        self.PORT = int(sys.argv[1])
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)

    def start(self):
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER}")
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.auth, args=(conn, addr))
            thread.start()
            print("[ACTIVE CONNECTIONS] {}".format(threading.active_count() - 1))

    def preprocess(self, conn: socket.socket, addr, username, cmd):
        """
        Broadcast message:      BCM message
        Download Active Users:  ATU
        Separate Room Service:  SRB username1 username2
        Separate Room Service:  SRM roomID message
        Read Messages:          RDM
        Log out:                OUT

        PtP Communication
        Upload file:            UPD username filename
        """
        token = cmd.split()
        if token[0] == 'BCM' and len(token) > 1:
            self.BCM(conn, addr, username, cmd[4:])
        elif token[0] == 'ATU':
            self.ATU(conn, addr, username)
        elif token[0] == 'SRB' and len(token) > 1:
            self.SRB(conn, addr, username, token[1:])
        elif token[0] == 'SRM' and len(token) > 2:
            try:
                self.SRM(conn, addr, username, int(token[1]), ' '.join(token[2:]))
            except ValueError:
                conn.send(b"[ERR] wrong input")
        elif token[0] == 'RDM' and len(token) > 1:
            self.RDM(conn, addr, username, token[1], token[1:])
        elif token[0] == 'UPD' and len(token) > 2:
            self.UPD(conn, addr, username, token[1], token[2])
        else:
            conn.send(b"[ERR] wrong input")

    def BCM(self, conn, addr, username, msg):
        print(username.capitalize(), 'broadcasted BCM')
        self.public_messages.append(f'#{len(self.public_messages)+1} \"{msg}\" at {datetime.now()}.')
        conn.send('Broadcast message, #{} broadcast at {}.'.format(len(self.public_messages), datetime.now()).encode(self.FORMAT))

    def ATU(self, conn, addr, username):
        print(f'{username.capitalize()} issued ATU command')
        res = ''
        for user in self.active_users:
            res += f'{str(user).capitalize()}, {conn.getsockname()[0]}, {conn.getsockname()[1]}, active since {self.active_users[user][2]}.\n'

        print('Return active user list: ')
        print(res)

        conn.send(res.encode(self.FORMAT))

    def SRB(self, conn, addr, username, participants):
        for participant in participants:
            if participant not in self.active_users.keys():
                conn.send(f'There is no active user: {participant}'.encode(self.FORMAT))
                return
        new_room = Room(username, participants)
        self.rooms[new_room.id] = new_room
        conn.send(b'DONE')

    def SRM(self, conn, addr, username, roomID, msg):
        if roomID not in self.rooms:
            conn.send(b'Room is not found')
        elif username not in self.rooms[roomID].participants:
            conn.send(b'You are not in this seperate room chat')
        else:
            m = Message(username, msg)
            self.rooms[roomID].media.append(m)
            self.rooms[roomID].logfile.write(m.serverToString()+'\n')
            self.rooms[roomID].logfile.flush()
            conn.send(b'Message shared')

    def RDM(self, conn, addr, username, msgType, timestamp):
        if msgType == 'b':
            conn.send(str(self.public_messages).encode(self.FORMAT))
        elif msgType == 's':
            res = ''
            for room in self.rooms:
                if username in self.rooms[room].participants:
                    res += f'Room id: {room}\n'
                    for message in self.rooms[room].media:
                        res += message.clientToString() + '\n'
                    res += '\n'
            if res == '':
                res = 'NO MESSAGE'
            conn.send(res.encode(self.FORMAT))
        else:
            conn.send(b'WRONG RDM COMMAND')

    def UPD(self, conn, addr, username, destination_user, filename):
        if destination_user not in self.active_users:
            print('USER NOT ACTIVE')
            conn.send(b'USER_NOT_ACTIVE')
            return

        if '/' in filename:
            filename = filename[filename.rfind('/')+1:]

        conn.send(b'SEND_FILE')
        file = open(filename, 'wb')

        buffer = conn.recv(128).decode()
        while True:
            if buffer == 'DONE':
                break
            if buffer == 'FILE_CHECK':
                buffer = conn.recv(128).decode()
                continue
            if buffer == 'FILE_PART':
                conn.send(b'SEND')
                buffer = conn.recv(1024)

            file.write(buffer)
            buffer = conn.recv(128).decode()

        file.close()

        file = open(filename, 'rb')

        self.users[destination_user][3][0] = username
        self.users[destination_user][3][1] = filename
        self.users[destination_user][3][2] = file
        file.close()

    def auth(self, conn: socket.socket, addr):
        print("[NEW CONNECTION] {} connected".format(addr))

        conn.send(b'LOGIN_USERNAME')
        username = conn.recv(128).decode()
        if username in self.users:
            conn.send(b'LOGIN_PASSWORD')
            password = conn.recv(128).decode()

            print(f'[LOGIN ATTEMPT] username: {username}, pass: {password}')
            if username in self.active_users:
                conn.send(b'ALREADY_CONNECTED')
            elif self.users[username][1] >= int(sys.argv[2]) and (datetime.now().second - self.users[username][2]) < 10:
                conn.send(b'STILL_BANNED')
                conn.close()
            elif password == self.users[username][0]:
                self.users[username][1] = 0
                conn.send(b'LOGIN_SUCCESS')
                self.active_users[username] = [conn, addr, datetime.now()]
                self.handle_client(username, conn, addr)
            else:
                self.users[username][1] += 1
                while self.users[username][1] < int(sys.argv[2]) and password != self.users[username][0]:
                    conn.send(b'INVALID_PASS')
                    password = conn.recv(128).decode()
                    print(f'[LOGIN ATTEMPT] username: {username}, pass: {password}')
                    self.users[username][1] += 1

                if password == self.users[username][0]:
                    conn.send(b'LOGIN_SUCCESS')
                    self.users[username][1] = 0
                    self.active_users[username] = [conn, addr, datetime.now().second]
                    self.handle_client(username, conn, addr)
                else:
                    self.users[username][2] = datetime.now().second
                    conn.send(b'LOGIN_BANNED')
                    conn.close()
        else:
            conn.send(b'WRONG_USERNAME')
        conn.close()

    def handle_client(self, username, conn: socket.socket, addr: str):
        self.logfile.write(f'{self.usercounter}; {datetime.now().strftime("%c")}; {username}\n')
        self.logfile.flush()
        self.usercounter += 1

        while True:
            msg = conn.recv(128).decode()

            if msg == 'OUT':
                print(username.capitalize(), 'logout')
                conn.send(b'DISCONNECTED')
                break
            elif msg == 'CHECK_FILE':
                if self.users[username][3][2] is None:
                    conn.send(b'NO_FILE')
                else:
                    conn.send(b'FILE')
                    conn.recv(128)
                    conn.send(self.users[username][3][0].encode(self.FORMAT))
                    conn.recv(128)
                    conn.send(self.users[username][3][1].encode(self.FORMAT))

                    file = self.users[username][3][2]
                    file = open(file.name, 'rb')

                    conn.sendall(file.read())

                    file.close()

                    self.users[username][3][2] = None
            else:
                self.preprocess(conn, addr, username, msg)

        del(self.active_users[username])


if __name__ == '__main__':
    Server().start()
