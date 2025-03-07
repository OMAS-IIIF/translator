import os
import tkinter as tk
from tkinter import ttk

class OpenDialog:

    def __init__(self, parent, title):
        super().__init__(parent, title)
        d = tk.filedialog.askdirectory(parent=parent, initialdir=os.getcwd())
