import io
import os
import tkinter as tk
from tkinter import ttk, simpledialog

class TaskBar(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(relief=tk.GROOVE, borderwidth=2)

class MainWindow(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._parent = parent
        ttk.Frame.__init__(self, *args, **kwargs)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        menubar = self.create_menubar()

        taskbar = TaskBar(self, padding=10)
        #self.connect_w = ttk.Button(taskbar, text="Connect...", command=self.connect)
        self.connect_w = ttk.Button(taskbar, text="Connect...")
        self.connect_w.pack(side=tk.LEFT)

    def create_menubar(self):
        menubar = tk.Menu(self._parent)
        self._parent.configure(menu=menubar)
        menu_connect = tk.Menu(menubar)
        menu_edit = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_connect, label='Connect')
        menubar.add_cascade(menu=menu_edit, label='Edit')

        #menu_connect.add_command(label='Connect...', command=self.connect)
        #menu_connect.add_command(label='Disconnect', command=self.disconnect)
        return menubar


class App(tk.Tk):

    def __init__(self, title, *args, **kwargs):
        super().__init__(title, *args, **kwargs)
        #self.title = 'LocoPy V01'
        self.wm_title('Translator V0.1')
        self.geometry('800x500+100+100')


if __name__ == '__main__':
    root = App('LocoPy V0.1')
    main = MainWindow(root)
    root.mainloop()
