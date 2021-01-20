import psutil
from tkinter import *


class Interface:
    def __init__(self, master, c):
        self.c = c
        self.temp_label = None
        self.ram_label = None
        self.cpu_label = None
        self.master = master

    def init_windows(self):
        self.master.title("Monitorizare resurse SO")
        self.master.configure(bg='midnight blue')

        self.cpu_label = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.cpu_label.place(x=330, y=20)
        self.ram_label = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.ram_label.place(x=330, y=100)
        self.temp_label = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.temp_label.place(x=330, y=180)

        digi = Label(self.master, text="CPU Usage:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi.place(x=20, y=25)
        digi2 = Label(self.master, text="Battery percent:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi2.place(x=20, y=100)
        digi3 = Label(self.master, text="Temperature:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi3.place(x=20, y=175)
        self.cpu_met()
        self.battery_met()
        self.temperature_met()
        self.master.mainloop()

    def cpu_met(self):
        self.c.write_single_register(5, int(psutil.cpu_percent(interval=1)))
        self.cpu_label.config(text=' {}%'.format(int(self.c.read_holding_registers(5, 1)[0])))
        self.cpu_label.after(200, self.cpu_met)

    def battery_met(self):
        self.c.write_single_register(1, int(psutil.sensors_battery().percent))
        self.ram_label.config(text=' {}%'.format(int(self.c.read_holding_registers(1, 1)[0])))
        self.ram_label.after(200, self.battery_met)

    def temperature_met(self):
        temp = psutil.disk_usage('C:')
        self.temp_label.config(text=' {}%'.format(temp.percent))
