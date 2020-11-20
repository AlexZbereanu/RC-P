import struct
import random
import socket
import select

import const


class ModbusClient:

    def __init__(self, hostname=None, port=None, unit_id=None, timeout=None,
                 debug=False):
        self.timeout = timeout
        self.hostname = hostname
        self.port = port
        self.debug = debug
        self.sock = None
        self.tr_id = 0
        self.unit_id = 1
        self.last_error = None

    def close(self):
        """inchide  conexiunea TCP
        """
        if self.sock:
            self.sock.close()
            self.sock = None
            return True
        else:
            return None

    def open(self):
        """open TCP connection
        """
        # restart daca este deschisa deja conexiunea
        if self.sock is not None:
            self.close()
        # initializare
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.debug_msg("Socket has been created!")
        except socket.error:
            self.sock = None
            self.debug_msg("Socket was not created!")

        SERVER = socket.gethostbyname('www.google.com')

        try:
            self.sock.settimeout(self.timeout)
            self.sock.connect((SERVER, const.PORT))
            self.debug_msg("Socket has been connected on port " + SERVER)
        except socket.error:
            self.sock.close()
            self.sock = None
        # check connect status
        if self.sock is not None:
            return True
        else:
            self.last_error = const.MB_CONNECT_ERR
            self.debug_msg('connect error')
            return False

    def can_read(self):
        if self.sock is None:
            return None
        if select.select([self.sock], [], [], self.timeout)[0]:
            return True
        else:
            self.last_error = const.MB_TIMEOUT_ERR
            self.debug_msg('timeout error')
            self.close()
            return None

    def send(self, data):
        """trimitere date catre socket
        """
        # check link
        if self.sock is None:
            self.debug_msg('apel trimitere pe socket inchis')
            return None
        # send
        data_l = len(data)
        try:
            send_l = self.sock.send(data)
        except socket.error:
            send_l = None
        # handle send error
        if (send_l is None) or (send_l != data_l):
            self.last_error = const.MB_SEND_ERR
            self.debug_msg('eroare de trimitere pachet catre socket')
            self.close()
            return None
        else:
            return send_l

    def recv(self, max_size):
        # wait for read
        if not self.can_read():
            self.close()
            return None
        # recv
        try:
            r_buffer = self.sock.recv(max_size)
        except socket.error:
            r_buffer = None
        # handle recv error
        if not r_buffer:
            self.last_error = const.MB_RECV_ERR
            self.debug_msg('_recv error')
            self.close()
            return None
        return r_buffer

    def recv_all(self, size):
        r_buffer = bytes()
        while len(r_buffer) < size:
            r_packet = self.recv(size - len(r_buffer))
            if not r_packet:
                return None
            r_buffer += r_packet
        return r_buffer

    def mbus_adu(self, fc, body):
        # build frame body
        f_body = struct.pack('B', fc) + body
        # build frame ModBus Application Protocol header (mbap)
        self.tr_id = random.randint(0, 65535)
        tx_pr_id = 0
        tx_hd_length = len(f_body) + 1
        f_mbap = struct.pack('>HHHB', self.tr_id, tx_pr_id,
                             tx_hd_length, self.unit_id)
        return f_mbap + f_body

    def send_mbus(self, frame):
        """trimitere  frame
        """
        # send request
        bytes_send = self.send(frame)
        if bytes_send:
            if self.debug:
                self.print_frame('Tx', frame)
            return bytes_send
        else:
            return None

    def recv_mbus(self):
        # receive
        # 7 bytes header (mbap)
        rx_buffer = self.recv_all(7)
        # check recv
        if not (rx_buffer and len(rx_buffer) == 7):
            self.last_error = const.MB_RECV_ERR
            self.debug_msg('_recv MBAP error')
            self.close()
            return None
        rx_frame = rx_buffer
        # decode header
        (rx_hd_tr_id, rx_hd_pr_id,
         rx_hd_length, rx_hd_unit_id) = struct.unpack('>HHHB', rx_frame)
        # check header
        if not ((rx_hd_tr_id == self.tr_id) and
                (rx_hd_pr_id == 0) and
                (rx_hd_length < 256) and
                (rx_hd_unit_id == self.unit_id)):
            self.last_error = const.MB_RECV_ERR
            self.debug_msg('MBAP format error')
            if self.debug:
                rx_frame += self.recv_all(rx_hd_length - 1)
                self.print_frame('Rx', rx_frame)
            self.close()
            return None
        # end of frame
        rx_buffer = self.recv_all(rx_hd_length - 1)
        if not (rx_buffer and
                (len(rx_buffer) == rx_hd_length - 1) and
                (len(rx_buffer) >= 2)):
            self.last_error = const.MB_RECV_ERR
            self.debug_msg('_recv frame body error')
            self.close()
            return None
        rx_frame += rx_buffer
        # dump frame
        if self.debug:
            self.print_frame('Rx', rx_frame)
        # body decode
        rx_bd_fc = struct.unpack('B', rx_buffer[0:1])[0]
        f_body = rx_buffer[1:]

        # check except
        if rx_bd_fc > 0x80:
            # except code
            exp_code = struct.unpack('B', f_body[0:1])[0]
            self.last_error = const.MB_EXCEPT_ERR
            self.debug_msg('except (code ' + str(exp_code) + ')')
            return None
        else:
            # return
            return f_body

    def debug_msg(self, msg):
        if self.debug:
            print(msg)

    def print_frame(self, label, data):
        """Print adu on stdout
        """
        # split data string items to a list of hex value
        dump = ['%02X' % c for c in bytearray(data)]
        # format for TCP
        if len(dump) > 6:
            # [MBAP] ...
            dump[0] = '[' + dump[0]
            dump[6] += ']'
        # print result
        print(label)
        s = ''
        for i in dump:
            s += i + ' '
        print(s)
