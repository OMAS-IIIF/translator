import tkinter as tk
from tkinter import ttk, messagebox

from paraglidetranslator.components.deeplconnection import DeepLConnection


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
        self.key = key
        self.data = data
        self.langs = langs
        self.langvar = tk.StringVar(self, lang)
        self.langselector = ttk.Combobox(self, textvariable=self.langvar, width=3)
        self.langselector["values"] = langs
        self.langselector.pack(side="left")

        self.doit = ttk.Button(self, text="T", command=self.doit)
        self.doit.pack(side="left")

    def doit(self):
        deepl = DeepLConnection()
        for ll in self.langs:
            if ll == self.langvar.get():
                continue
            if self.data[self.key][ll].get() == self.key or self.data[self.key][ll].get() == "":
                deepl_lang = ll.upper()
                if deepl_lang == "EN":
                    deepl_lang = "EN-US"
                try:
                    result = deepl.client.translate_text(self.data[self.key][self.langvar.get()].get(),
                                                         target_lang=deepl_lang)
                except Exception as e:
                    messagebox.showerror("Error", e)
                    return
                self.data[self.key][ll].set(result)
