import psutil
from tkinter import *

discret_input_offset = 10000
input_reg_offset = 30000
holding_register_offset = 40000


class Interface:
    def __init__(self, master, c):
        self.disk_d_mem = None
        self.disk_c_mem = None
        self.disk_e_mem = None
        self.c = c
        self.disk_c_label = None
        self.disk_e_label = None
        self.disk_d_label = None
        self.plug_label = None
        self.bat_label = None
        self.cpu_label = None
        self.master = master

    def init_windows(self):
        self.master.title("Monitorizare resurse SO")
        self.master.configure(bg='midnight blue')

        self.cpu_label = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.cpu_label.place(x=330, y=20)
        self.bat_label = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.bat_label.place(x=330, y=100)
        self.plug_label = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.plug_label.place(x=830, y=100)
        self.disk_c_label = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.disk_c_label.place(x=330, y=180)
        self.disk_d_label = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.disk_d_label.place(x=330, y=260)
        self.disk_e_label = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.disk_e_label.place(x=330, y=340)
        self.disk_c_mem = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.disk_c_mem.place(x=830, y=180)
        self.disk_d_mem = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.disk_d_mem.place(x=830, y=260)
        self.disk_e_mem = Label(self.master, bg="black", fg="green", anchor=NE, font="Arial 30 bold", width=6)
        self.disk_e_mem.place(x=830, y=340)

        digi = Label(self.master, text="CPU Usage:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi.place(x=20, y=25)
        digi2 = Label(self.master, text="Battery percent:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi2.place(x=20, y=105)
        digi22 = Label(self.master, text="Is plugged:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi22.place(x=590, y=105)
        digi3 = Label(self.master, text="Disk C:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi3.place(x=20, y=185)
        digi4 = Label(self.master, text="Disk D:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi4.place(x=20, y=265)
        digi5 = Label(self.master, text="Disk E:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi5.place(x=20, y=345)
        digi6 = Label(self.master, text="Capacity C:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi6.place(x=590, y=185)
        digi7 = Label(self.master, text="Capacity D:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi7.place(x=590, y=265)
        digi8 = Label(self.master, text="Capacity E:", font="arial 24 bold", bg='midnight blue', fg="white")
        digi8.place(x=590, y=345)
        self.cpu_met()
        self.battery_met()
        self.disk_met()
        self.master.mainloop()

    def cpu_met(self):
        self.c.write_single_register(100 + input_reg_offset, int(psutil.cpu_percent(interval=1)))
        self.cpu_label.config(text=' {}%'.format(int(self.c.read_input_registers(100 + input_reg_offset, 1)[0])))
        self.cpu_label.after(200, self.cpu_met)

    def battery_met(self):
        battery = psutil.sensors_battery().power_plugged
        self.c.write_single_coil(1, battery)
        self.c.write_single_register(1 + holding_register_offset, int(psutil.sensors_battery().percent))
        self.bat_label.config(text=' {}%'.format(int(self.c.read_holding_registers(1 + holding_register_offset, 1)[0])))
        self.bat_label.after(200, self.battery_met)
        self.plug_label.config(text=' {}'.format(self.c.read_coils(1, 1)[0]))
        self.plug_label.after(200, self.battery_met)

    def disk_met(self):
        mem_e = 0
        mem_d = 0
        mem_c = 0
        self.c.write_multiple_registers(10 + holding_register_offset,
                                        [int(psutil.disk_usage('C:').percent), int(psutil.disk_usage('D:').percent)])
        self.c.write_single_register(12 + holding_register_offset, int(psutil.disk_usage('E:').percent))
        aux_e = int(psutil.disk_usage('E:').total)
        aux_c = int(psutil.disk_usage('C:').total)
        aux_d = int(psutil.disk_usage('D:').total)
        for i in range(0, 9):
            mem_e = aux_e // 10
            aux_e = mem_e
            mem_d = aux_d // 10
            aux_d = mem_d
            mem_c = aux_c // 10
            aux_c = mem_c
        self.c.write_single_register(13 + holding_register_offset, mem_c)
        self.c.write_single_register(14 + holding_register_offset, mem_d)
        self.c.write_single_register(15 + holding_register_offset, mem_e)

        self.disk_c_label.config(
            text=' {}%'.format(int(self.c.read_holding_registers(10 + holding_register_offset, 1)[0])))
        self.disk_d_label.config(
            text=' {}%'.format(int(self.c.read_holding_registers(11 + holding_register_offset, 1)[0])))
        self.disk_e_label.config(
            text=' {}%'.format(int(self.c.read_holding_registers(12 + holding_register_offset, 1)[0])))
        self.disk_e_mem.config(
            text=' {} GB'.format(int(self.c.read_holding_registers(15 + holding_register_offset, 1)[0])))
        self.disk_c_mem.config(
            text=' {} GB'.format(int(self.c.read_holding_registers(13 + holding_register_offset, 1)[0])))
        self.disk_d_mem.config(
            text=' {} GB'.format(int(self.c.read_holding_registers(14 + holding_register_offset, 1)[0])))
