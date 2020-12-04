import socket
import threading

import const
import client

if __name__ == '__main__':
    client = client.ModbusClient("127.0.0.1", const.PORT, 1, 10, 1)
    client.open()
    client.send(b'alex')
    while True:
        ok = 'bye'
        message = client.recv(1024)
        print('From server:' + str(message))
        #out_data = input()
        #client.send(bytes(out_data, 'UTF-8'))

        bits = client.read_coils(0, 10)
        # if success display registers
        if bits:
            print("bit ad #0 to 9: "+str(bits))
        #if ok == out_data:
    client.close()
