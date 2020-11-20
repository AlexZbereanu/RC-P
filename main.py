from tkinter import Tk

import const
from interface import Interface
import client

if __name__ == '__main__':
    client = client.ModbusClient("www.google.com", const.PORT, 1, 30, 1)
    client.open()
    client.close()
    '''root = Tk()
    root.geometry("1080x650")
    root.resizable(0, 0)
    server = Interface(root)
    root.mainloop()'''
