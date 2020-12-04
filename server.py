import socket

import const


class ModbusServer(object):

    def __init__(self, host='', port=const.PORT):
        self.host = host
        self.port = port
        self.running = False
        self.service = None

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket has been successfuly created")
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((socket.gethostbyname(socket.gethostname()), const.PORT))
        print("Socket has been binded to " + str(const.PORT))

        s.listen(1)

        while True:
            sock, client_addres = s.accept()
            print('Connected to ' + str(client_addres))
            mes = sock.recv(1024)
            print(mes)
            sock.send(mes + b' what?')
            if mes == b'bye':
                print('lala')
                sock.close()

    def stop(self):
        if self.is_run:
            self.service.shutdown()
            self.service.server_close()

    def is_run(self):
        return self.running
