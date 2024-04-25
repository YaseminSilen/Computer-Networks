import sys
import socket
import threading
import time


class Main:
    def __init__(self):
        self.PORT = int(sys.argv[2])
        self.SERVER = sys.argv[1]
        self.FORMAT = 'utf-8'
        self.ADDR = (self.SERVER, self.PORT)

        self.username = ''

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        self.file_receiving = False

    def auth(self):
        response = self.client.recv(128).decode(self.FORMAT)

        while True:
            if response == 'LOGIN_USERNAME':
                msg = input('Username: ')
                self.username = msg
                self.send(msg)
            elif response == 'LOGIN_PASSWORD':
                msg = input('Password: ')
                self.send(msg)
            elif response == 'INVALID_PASS':
                print('Invalid Password. Please try again')
                msg = input('Password: ')
                self.send(msg)
            elif response == 'LOGIN_BANNED':
                print('Invalid Password. Your account has been blocked. Please try again later')
                break
            elif response == 'STILL_BANNED':
                print('Your account is blocked due to multiple login failures. Please try again later')
                break
            elif response == 'WRONG_USERNAME':
                print(response)
                break
            elif response == 'ALREADY_CONNECTED':
                print('This user is already connected in another session.')
                break
            elif response == 'LOGIN_SUCCESS':
                print(response)
                self.loop()
                break

            response = self.client.recv(128).decode(self.FORMAT)
        self.client.close()

    def loop(self):
        thread = threading.Thread(target=self.file_check)
        thread.start()

        while True:
            cmd = input("Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, UPD, OUT): ")
            token = cmd.split()

            if len(token) == 0:
                continue

            if token[0] == 'UPD':
                if len(token) < 3:
                    print('Wrong UPD output')
                else:
                    self.send_file(token[1], token[2])
                continue

            self.send(cmd)
            response = self.client.recv(1024).decode()
            if response == 'DISCONNECTED':
                print(f'Bye, {self.username.capitalize()}!')
                break
            print(response)

    def send_file(self, destination, filename):
        try:
            file = open(filename, 'rb')
            self.send(f'UPD {destination} {filename}')

            response = self.client.recv(128).decode()

            if response == 'USER_NOT_ACTIVE':
                print(f'{destination} is not active')
            elif response == 'SEND_FILE':
                data = file.read(1024)
                while data:
                    self.send('FILE_PART')
                    self.client.recv(128)

                    self.client.send(data)
                    data = file.read(1024)
                self.send('DONE')
                print(f'{filename} has been uploaded')
        except FileNotFoundError:
            print('File not found')

    def file_check(self):
        while True:
            time.sleep(1)
            if self.client.fileno() == -1:
                break

            self.send('CHECK_FILE')
            response = self.client.recv(128).decode()

            if response == 'FILE':
                self.file_receiving = True
                self.send('SEND_SENDER')
                sender = self.client.recv(128).decode()
                self.send('SEND_FILENAME')
                filename = self.client.recv(128).decode()

                file = open(sender+'_'+filename, 'wb')
                # UPD hans ../Archive/example1.mp4
                buffer = self.client.recv(1024)
                while buffer:
                    file.write(buffer)
                    if len(buffer) != 1024:
                        break
                    buffer = self.client.recv(1024)

                print(sender, 'sends', filename)
                file.close()
                self.file_receiving = False

    def send(self, msg):
        self.client.send(msg.encode(self.FORMAT))


if __name__ == '__main__':
    Main().auth()

