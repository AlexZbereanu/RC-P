from tkinter import *
import constants as const
from interface import Interface
from utils import set_bit
import re
import socket
import select
import struct
import random


class ModbusClient:
    """Modbus TCP client"""

    def __init__(self, host=None, port=None, unit_id=None, timeout=None,
                 debug=None, auto_open=None, auto_close=None):

        self.__hostname = 'localhost'
        self.__port = const.MODBUS_PORT
        self.__unit_id = 1
        self.__timeout = 30.0  # socket timeout
        self.__debug = False  # debug trace on/off
        self.__auto_open = False  # auto TCP connect
        self.__auto_close = False  # auto TCP close
        self.__sock = None  # socket handle
        self.__hd_tr_id = 0  # store transaction ID
        self.__last_except = 0  # last expect code

    def host(self, hostname=None):
        """Get or set host (IPv4 or hostname like 'plc.domain.net')
        """
        if (hostname is None) or (hostname == self.__hostname):
            return self.__hostname
        # when hostname change ensure old socket is close
        self.close()
        # IPv4 ?
        try:
            socket.inet_pton(socket.AF_INET, hostname)
            self.__hostname = hostname
            return self.__hostname
        except socket.error:
            pass
        # DNS name ?
        if re.match('^[a-z][a-z0-9\.\-]+$', hostname):
            self.__hostname = hostname
            return self.__hostname
        else:
            return None

    def port(self, port=None):
        """Get or set TCP port
        """
        if (port is None) or (port == self.__port):
            return self.__port
        # when port change ensure old socket is close
        self.close()
        # valid port ?
        if 0 < int(port) < 65536:
            self.__port = int(port)
            return self.__port
        else:
            return None

    def auto_open(self, state=None):
        """Get or set automatic TCP connect mode"""
        if state is None:
            return self.__auto_open
        self.__auto_open = bool(state)
        return self.__auto_open

    def auto_close(self, state=None):
        """Get or set automatic TCP close mode (after each request)"""
        if state is None:
            return self.__auto_close
        self.__auto_close = bool(state)
        return self.__auto_close

    def open(self):
        """Connect to modbus server (open TCP connection)
        """
        # restart TCP if already open
        if self.is_open():
            self.close()
        # init socket and connect
        # list available sockets on the target host/port
        # AF_xxx : AF_INET -> IPv4, AF_INET6 -> IPv6,
        #          AF_UNSPEC -> IPv6 (priority on some system) or 4
        # list available socket on target host
        for res in socket.getaddrinfo(self.__hostname, self.__port,
                                      socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, sock_type, proto, canon_name, sa = res
            try:
                self.__sock = socket.socket(af, sock_type, proto)
            except socket.error:
                self.__sock = None
                continue
            try:
                self.__sock.settimeout(self.__timeout)
                self.__sock.connect(sa)
            except socket.error:
                self.__sock.close()
                self.__sock = None
                continue
            break
        # check connect status
        if self.__sock is not None:
            return True
        else:
            self.__debug_msg('connect error')
            return False

    def is_open(self):
        """Get status of TCP connection
        """
        return self.__sock is not None

    def close(self):
        """Close TCP connection
        """
        if self.__sock:
            self.__sock.close()
            self.__sock = None
            return True
        else:
            return None

    def read_coils(self, bit_addr, bit_nb=1):
        """Modbus function READ_COILS (0x01)
        """
        # check params
        if not (0 <= int(bit_addr) <= 65535):
            self.__debug_msg('read_coils(): bit_addr out of range')
            return None
        if not (1 <= int(bit_nb) <= 2000):
            self.__debug_msg('read_coils(): bit_nb out of range')
            return None
        if (int(bit_addr) + int(bit_nb)) > 65536:
            self.__debug_msg('read_coils(): read after ad 65535')
            return None
        # build frame
        tx_buffer = self._mbus_frame(const.READ_COILS, struct.pack('>HH', bit_addr, bit_nb))
        # send request
        s_send = self._send_mbus(tx_buffer)
        # check error
        if not s_send:
            return None
        # receive
        f_body = self._recv_mbus()
        # check error
        if not f_body:
            return None
        # check min frame body size
        if len(f_body) < 2:
            self.__debug_msg('read_coils(): rx frame under min size')
            self.close()
            return None
        # extract field "byte count"
        rx_byte_count = struct.unpack("B", f_body[0:1])[0]
        # frame with bits value -> bits[] list
        f_bits = bytearray(f_body[1:])
        # check rx_byte_count: match nb of bits request and check buffer size
        if not ((rx_byte_count >= int((bit_nb + 7) / 8)) and
                (rx_byte_count == len(f_bits))):
            self.__debug_msg('read_coils(): rx byte count mismatch')
            self.close()
            return None
        # allocate a bit_nb size list
        bits = [None] * bit_nb
        # fill bits list with bit items
        for i, item in enumerate(bits):
            bits[i] = bool(f_bits[int(i / 8)] >> (i % 8) & 0x01)
        # return bits list
        return bits

    def read_discrete_inputs(self, bit_addr, bit_nb=1):
        """Modbus function READ_DISCRETE_INPUTS (0x02)
        """
        # check params
        if not (0 <= int(bit_addr) <= 65535):
            self.__debug_msg('read_discrete_inputs(): bit_addr out of range')
            return None
        if not (1 <= int(bit_nb) <= 2000):
            self.__debug_msg('read_discrete_inputs(): bit_nb out of range')
            return None
        if (int(bit_addr) + int(bit_nb)) > 65536:
            self.__debug_msg('read_discrete_inputs(): read after ad 65535')
            return None
        # build frame
        tx_buffer = self._mbus_frame(const.READ_DISCRETE_INPUTS, struct.pack('>HH', bit_addr, bit_nb))
        # send request
        s_send = self._send_mbus(tx_buffer)
        # check error
        if not s_send:
            return None
        # receive
        f_body = self._recv_mbus()
        # check error
        if not f_body:
            return None
        # check min frame body size
        if len(f_body) < 2:
            self.__debug_msg('read_discrete_inputs(): rx frame under min size')
            self.close()
            return None
        # extract field "byte count"
        rx_byte_count = struct.unpack("B", f_body[0:1])[0]
        # frame with bits value -> bits[] list
        f_bits = bytearray(f_body[1:])
        # check rx_byte_count: match nb of bits request and check buffer size
        if not ((rx_byte_count >= int((bit_nb + 7) / 8)) and
                (rx_byte_count == len(f_bits))):
            self.__debug_msg('read_discrete_inputs(): rx byte count mismatch')
            self.close()
            return None
        # allocate a bit_nb size list
        bits = [None] * bit_nb
        # fill bits list with bit items
        for i, item in enumerate(bits):
            bits[i] = bool(f_bits[int(i / 8)] >> (i % 8) & 0x01)
        # return bits list
        return bits

    def read_holding_registers(self, reg_addr, reg_nb=1):
        """Modbus function READ_HOLDING_REGISTERS (0x03)
        """
        # check params
        if not (0 <= int(reg_addr) <= 65535):
            self.__debug_msg('read_holding_registers(): reg_addr out of range')
            return None
        if not (1 <= int(reg_nb) <= 125):
            self.__debug_msg('read_holding_registers(): reg_nb out of range')
            return None
        if (int(reg_addr) + int(reg_nb)) > 65536:
            self.__debug_msg('read_holding_registers(): read after ad 65535')
            return None
        # build frame
        tx_buffer = self._mbus_frame(const.READ_HOLDING_REGISTERS, struct.pack('>HH', reg_addr, reg_nb))
        # send request
        s_send = self._send_mbus(tx_buffer)
        # check error
        if not s_send:
            return None
        # receive
        f_body = self._recv_mbus()
        # check error
        if not f_body:
            return None
        # check min frame body size
        if len(f_body) < 2:
            self.__debug_msg('read_holding_registers(): rx frame under min size')
            self.close()
            return None
        # extract field "byte count"
        rx_byte_count = struct.unpack('B', f_body[0:1])[0]
        # frame with regs value
        f_regs = f_body[1:]
        # check rx_byte_count: buffer size must be consistent and have at least the requested number of registers
        if not ((rx_byte_count >= 2 * reg_nb) and
                (rx_byte_count == len(f_regs))):
            self.__debug_msg('read_holding_registers(): rx byte count mismatch')
            self.close()
            return None
        # allocate a reg_nb size list
        registers = [None] * reg_nb
        # fill registers list with register items
        for i, item in enumerate(registers):
            registers[i] = struct.unpack('>H', f_regs[i * 2:i * 2 + 2])[0]
        # return registers list
        return registers

    def read_input_registers(self, reg_addr, reg_nb=1):
        """Modbus function READ_INPUT_REGISTERS (0x04)
        """
        # check params
        if not (0x0000 <= int(reg_addr) <= 0xffff):
            self.__debug_msg('read_input_registers(): reg_addr out of range')
            return None
        if not (0x0001 <= int(reg_nb) <= 0x007d):
            self.__debug_msg('read_input_registers(): reg_nb out of range')
            return None
        if (int(reg_addr) + int(reg_nb)) > 0x10000:
            self.__debug_msg('read_input_registers(): read after ad 65535')
            return None
        # build frame
        tx_buffer = self._mbus_frame(const.READ_INPUT_REGISTERS, struct.pack('>HH', reg_addr, reg_nb))
        # send request
        s_send = self._send_mbus(tx_buffer)
        # check error
        if not s_send:
            return None
        # receive
        f_body = self._recv_mbus()
        # check error
        if not f_body:
            return None
        # check min frame body size
        if len(f_body) < 2:
            self.__debug_msg('read_input_registers(): rx frame under min size')
            self.close()
            return None
        # extract field "byte count"
        rx_byte_count = struct.unpack('B', f_body[0:1])[0]
        # frame with regs value
        f_regs = f_body[1:]
        # check rx_byte_count: buffer size must be consistent and have at least the requested number of registers
        if not ((rx_byte_count >= 2 * reg_nb) and
                (rx_byte_count == len(f_regs))):
            self.__debug_msg('read_input_registers(): rx byte count mismatch')
            self.close()
            return None
        # allocate a reg_nb size list
        registers = [None] * reg_nb
        # fill registers list with register items
        for i, item in enumerate(registers):
            registers[i] = struct.unpack('>H', f_regs[i * 2:i * 2 + 2])[0]
        # return registers list
        return registers

    def write_single_coil(self, bit_addr, bit_value):
        """Modbus function WRITE_SINGLE_COIL (0x05)
        """
        # check params
        if not (0 <= int(bit_addr) <= 65535):
            self.__debug_msg('write_single_coil(): bit_addr out of range')
            return None
        # build frame
        bit_value = 0xFF if bit_value else 0x00
        tx_buffer = self._mbus_frame(const.WRITE_SINGLE_COIL, struct.pack('>HBB', bit_addr, bit_value, 0))
        # send request
        s_send = self._send_mbus(tx_buffer)
        # check error
        if not s_send:
            return None
        # receive
        f_body = self._recv_mbus()
        # check error
        if not f_body:
            return None
        # check fix frame size
        if len(f_body) != 4:
            self.__debug_msg('write_single_coil(): rx frame size error')
            self.close()
            return None
        # register extract
        (rx_bit_addr, rx_bit_value, rx_padding) = struct.unpack('>HBB', f_body[:4])
        # check bit write
        is_ok = (rx_bit_addr == bit_addr) and (rx_bit_value == bit_value)
        return True if is_ok else None

    def write_single_register(self, reg_addr, reg_value):
        """Modbus function WRITE_SINGLE_REGISTER (0x06)
        """
        # check params
        if not (0 <= int(reg_addr) <= 65535):
            self.__debug_msg('write_single_register(): reg_addr out of range')
            return None
        if not (0 <= int(reg_value) <= 65535):
            self.__debug_msg('write_single_register(): reg_value out of range')
            return None
        # build frame
        tx_buffer = self._mbus_frame(const.WRITE_SINGLE_REGISTER,
                                     struct.pack('>HH', reg_addr, reg_value))
        # send request
        s_send = self._send_mbus(tx_buffer)
        # check error
        if not s_send:
            return None
        # receive
        f_body = self._recv_mbus()
        # check error
        if not f_body:
            return None
        # check fix frame size
        if len(f_body) != 4:
            self.__debug_msg('write_single_register(): rx frame size error')
            self.close()
            return None
        # register extract
        rx_reg_addr, rx_reg_value = struct.unpack('>HH', f_body)
        # check register write
        is_ok = (rx_reg_addr == reg_addr) and (rx_reg_value == reg_value)
        return True if is_ok else None

    def write_multiple_coils(self, bits_addr, bits_value):
        """Modbus function WRITE_MULTIPLE_COILS (0x0F)
        """
        # number of bits to write
        bits_nb = len(bits_value)
        # check params
        if not (0x0000 <= int(bits_addr) <= 0xffff):
            self.__debug_msg('write_multiple_coils(): bits_addr out of range')
            return None
        if not (0x0001 <= int(bits_nb) <= 0x07b0):
            self.__debug_msg('write_multiple_coils(): number of bits out of range')
            return None
        if (int(bits_addr) + int(bits_nb)) > 0x10000:
            self.__debug_msg('write_multiple_coils(): write after ad 65535')
            return None
        # build frame
        # format bits value string
        bits_val_str = b''
        # allocate bytes list
        b_size = int(bits_nb / 8)
        b_size += 1 if (bits_nb % 8) else 0
        bytes_l = [0] * b_size
        # populate bytes list with bits_value
        for i, item in enumerate(bits_value):
            if item:
                byte_i = int(i / 8)
                bytes_l[byte_i] = set_bit(bytes_l[byte_i], i % 8)
        # format bits_val_str
        for byte in bytes_l:
            bits_val_str += struct.pack('B', byte)
        bytes_nb = len(bits_val_str)
        # format modbus frame body
        body = struct.pack('>HHB', bits_addr, bits_nb, bytes_nb) + bits_val_str
        tx_buffer = self._mbus_frame(const.WRITE_MULTIPLE_COILS, body)
        # send request
        s_send = self._send_mbus(tx_buffer)
        # check error
        if not s_send:
            return None
        # receive
        f_body = self._recv_mbus()
        # check error
        if not f_body:
            return None
        # check fix frame size
        if len(f_body) != 4:
            self.__debug_msg('write_multiple_coils(): rx frame size error')
            self.close()
            return None
        # register extract
        (rx_bit_addr, rx_bit_nb) = struct.unpack('>HH', f_body[:4])
        # check regs write
        is_ok = (rx_bit_addr == bits_addr)
        return True if is_ok else None

    def write_multiple_registers(self, regs_addr, regs_value):
        """Modbus function WRITE_MULTIPLE_REGISTERS (0x10)
        """
        # number of registers to write
        regs_nb = len(regs_value)
        # check params
        if not (0x0000 <= int(regs_addr) <= 0xffff):
            self.__debug_msg('write_multiple_registers(): regs_addr out of range')
            return None
        if not (0x0001 <= int(regs_nb) <= 0x007b):
            self.__debug_msg('write_multiple_registers(): number of registers out of range')
            return None
        if (int(regs_addr) + int(regs_nb)) > 0x10000:
            self.__debug_msg('write_multiple_registers(): write after ad 65535')
            return None
        # build frame
        # format reg value string
        regs_val_str = b""
        for reg in regs_value:
            # check current register value
            if not (0 <= int(reg) <= 0xffff):
                self.__debug_msg('write_multiple_registers(): regs_value out of range')
                return None
            # pack register for build frame
            regs_val_str += struct.pack('>H', reg)
        bytes_nb = len(regs_val_str)
        # format modbus frame body
        body = struct.pack('>HHB', regs_addr, regs_nb, bytes_nb) + regs_val_str
        tx_buffer = self._mbus_frame(const.WRITE_MULTIPLE_REGISTERS, body)
        # send request
        s_send = self._send_mbus(tx_buffer)
        # check error
        if not s_send:
            return None
        # receive
        f_body = self._recv_mbus()
        # check error
        if not f_body:
            return None
        # check fix frame size
        if len(f_body) != 4:
            self.__debug_msg('write_multiple_registers(): rx frame size error')
            self.close()
            return None
        # register extract
        (rx_reg_addr, rx_reg_nb) = struct.unpack('>HH', f_body[:4])
        # check regs write
        is_ok = (rx_reg_addr == regs_addr)
        return True if is_ok else None

    def _can_read(self):
        """Wait data available for socket read
        """
        if self.__sock is None:
            return None
        if select.select([self.__sock], [], [], self.__timeout)[0]:
            return True
        else:
            self.__debug_msg('timeout error')
            self.close()
            return None

    def _send(self, data):
        """Send data over current socket

        :param data: registers value to write
        :type data: str (Python2) or class bytes (Python3)
        :returns: True if send ok or None if error
        :rtype: bool or None
        """
        # check link
        if self.__sock is None:
            self.__debug_msg('call _send on close socket')
            return None
        # send
        data_l = len(data)
        try:
            send_l = self.__sock.send(data)
        except socket.error:
            send_l = None
        # handle send error
        if (send_l is None) or (send_l != data_l):
            self.__debug_msg('_send error')
            self.close()
            return None
        else:
            return send_l

    def _recv(self, max_size):
        """Receive data over current socket

        :param max_size: number of bytes to receive
        :type max_size: int
        :returns: receive data or None if error
        :rtype: str (Python2) or class bytes (Python3) or None
        """
        # wait for read
        if not self._can_read():
            self.close()
            return None
        # recv
        try:
            r_buffer = self.__sock.recv(max_size)
        except socket.error:
            r_buffer = None
        # handle recv error
        if not r_buffer:
            self.__debug_msg('_recv error')
            self.close()
            return None
        return r_buffer

    def _recv_all(self, size):
        """Receive data over current socket, loop until all bytes is receive (avoid TCP frag)

        :param size: number of bytes to receive
        :type size: int
        :returns: receive data or None if error
        :rtype: str (Python2) or class bytes (Python3) or None
        """
        r_buffer = bytes()
        while len(r_buffer) < size:
            r_packet = self._recv(size - len(r_buffer))
            if not r_packet:
                return None
            r_buffer += r_packet
        return r_buffer

    def _send_mbus(self, frame):
        """Send modbus frame

        :param frame: modbus frame to send (with MBAP for TCP/CRC for RTU)
        :type frame: str (Python2) or class bytes (Python3)
        :returns: number of bytes send or None if error
        :rtype: int or None
        """
        # for auto_open mode, check TCP and open if need
        if self.__auto_open and not self.is_open():
            self.open()
        # send request
        bytes_send = self._send(frame)
        if bytes_send:
            if self.__debug:
                self._pretty_dump('Tx', frame)
            return bytes_send
        else:
            return None

    def _recv_mbus(self):
        """Receive a modbus frame

        :returns: modbus frame body or None if error
        :rtype: str (Python2) or class bytes (Python3) or None
        """
        # receive
        # modbus TCP receive
        # 7 bytes header (mbap)
        rx_buffer = self._recv_all(7)
        # check recv
        if not (rx_buffer and len(rx_buffer) == 7):
            self.__debug_msg('_recv MBAP error')
            self.close()
            return None
        rx_frame = rx_buffer
        # decode header
        (rx_hd_tr_id, rx_hd_pr_id,
         rx_hd_length, rx_hd_unit_id) = struct.unpack('>HHHB', rx_frame)
        # check header
        if not ((rx_hd_tr_id == self.__hd_tr_id) and
                (rx_hd_pr_id == 0) and
                (rx_hd_length < 256) and
                (rx_hd_unit_id == self.__unit_id)):
            self.__debug_msg('MBAP format error')
            if self.__debug:
                rx_frame += self._recv_all(rx_hd_length - 1)
                self._pretty_dump('Rx', rx_frame)
            self.close()
            return None
        # end of frame
        rx_buffer = self._recv_all(rx_hd_length - 1)
        if not (rx_buffer and
                (len(rx_buffer) == rx_hd_length - 1) and
                (len(rx_buffer) >= 2)):
            self.__debug_msg('_recv frame body error')
            self.close()
            return None
        rx_frame += rx_buffer
        # dump frame
        if self.__debug:
            self._pretty_dump('Rx', rx_frame)
        # body decode
        rx_bd_fc = struct.unpack('B', rx_buffer[0:1])[0]
        f_body = rx_buffer[1:]
        if self.__auto_close:
            self.close()
        # check except
        if rx_bd_fc > 0x80:
            # except code
            exp_code = struct.unpack('B', f_body[0:1])[0]
            self.__last_except = exp_code
            self.__debug_msg('except (code ' + str(exp_code) + ')')
            return None
        else:
            # return
            return f_body

    def _mbus_frame(self, fc, body):
        """Build modbus frame (add MBAP for Modbus/TCP, slave AD + CRC for RTU)
        """
        # build frame body
        f_body = struct.pack('B', fc) + body
        # modbus/TCP
        # build frame ModBus Application Protocol header (mbap)
        self.__hd_tr_id = random.randint(0, 65535)
        tx_hd_pr_id = 0
        tx_hd_length = len(f_body) + 1
        f_mbap = struct.pack('>HHHB', self.__hd_tr_id, tx_hd_pr_id,
                             tx_hd_length, self.__unit_id)
        return f_mbap + f_body

    def _pretty_dump(self, label, data):
        """Print modbus/TCP frame ('[header]body') on stdout
        """
        # split data string items to a list of hex value
        dump = ['%02X' % c for c in bytearray(data)]
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

    def __debug_msg(self, msg):
        """Print debug message if debug mode is on
        """
        if self.__debug:
            print(msg)


if __name__ == "__main__":
    SERVER_HOST = "localhost"
    SERVER_PORT = 502

    c = ModbusClient()

    # uncomment this line to see debug message
    # c.debug(True)
    # define modbus server host, port
    c.host(SERVER_HOST)
    c.port(SERVER_PORT)
    root = Tk()
    root.geometry("1080x650")
    root.resizable(0, 0)
    while True:
        # open or reconnect TCP to server
        if not c.is_open():
            if not c.open():
                print("unable to connect to " + SERVER_HOST + ":" + str(SERVER_PORT))

        s = Interface(root, c)
        # root.mainloop()
        root.destroy()

        # sleep 7s before next polling
        # time.sleep(7)
