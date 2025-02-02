import tkinter as tk
from tkinter import ttk

from components.connection import Connection


class Translate(ttk.Frame):
    langselector: tk.Widget
    doit: tk.Widget
    langvar: tk.StringVar

    def __init__(self,
                 parent: tk.Widget,
                 key: str,
                 data: dict[str, dict[str, tk.StringVar]],
                 langs: list[str],
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        lang = langs[0]
        for ll in langs:
            if data[key][ll].get() != key:
                lang = ll
                break
        self.langvar = tk.StringVar(self, lang)
        self.langselector = ttk.Combobox(self, textvariable=self.langvar, width=3)
        self.langselector["values"] = langs
        self.langselector.pack(side="left")

        self.doit = ttk.Button(self, text="T", command=self.doit)
        self.doit.pack(side="left")

    def doit(self):
        deepl = Connection()
