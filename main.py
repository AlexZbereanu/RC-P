from tkinter import Tk

import const
from interface import Interface
import client
import server

if __name__ == '__main__':
    server = server.ModbusServer()
    server.start()
    server.stop()
    '''root = Tk()
    root.geometry("1080x650")
    root.resizable(0, 0)
    server = Interface(root)
    root.mainloop()'''
