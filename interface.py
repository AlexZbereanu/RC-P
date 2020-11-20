from tkinter import *
import psutil


class Interface:
    def __init__(self, master):
        self.temp_label = None
        self.ram_label = None
        self.cpu_label = None
        self.master = master
        self.initWindows()

    def initWindows(self):
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
        self.ram_met()
        self.others()

    def cpu_met(self):
        cpu_use = psutil.cpu_percent(interval=1)
        self.cpu_label.config(text=' {}%'.format(cpu_use))
        self.cpu_label.after(200, self.cpu_met)

    def ram_met(self):
        ram_use = psutil.sensors_battery()
        self.ram_label.config(text=' {}%'.format(ram_use.percent))
        self.ram_label.after(200, self.ram_met)

    def others(self):
        temp = psutil.disk_usage('C:')
        self.temp_label.config(text=' {}%'.format(temp.percent))


