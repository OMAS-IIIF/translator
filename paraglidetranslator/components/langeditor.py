import platform
import tkinter as tk
from pprint import pprint
from tkinter import ttk, simpledialog, messagebox

from deepl import TextResult
from tksheet import Sheet

from paraglidetranslator.components.deeplconnection import DeepLConnection


class LangEditor(ttk.Frame):
    keys: dict[str, tk.StringVar]
    langs: list[str]
    scrollable_frame: ttk.Frame

    def __init__(self,
                 parent: tk.Widget,
                 langs: list[str],
                 data: list[list[str]],
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(padding=5, borderwidth=3, relief=tk.RIDGE)

        self.keys = {}
        self.langs = langs
        self.data = data  # dict[key: dict[lang, value]]
        self.parent = parent

        self.row = -1
        self.col = -1

        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)
        self.sheet = Sheet(self,
                           data=data,
                           theme="light blue")
        try:
            self.sheet.set_options(stretch_columns="all", stretch_headers="all")
        except Exception:
            # Fallback für ältere Versionen
            self.sheet.set_options(stretch_columns=True)

        self.sheet.set_header_data(['key', *self.langs])
        self.sheet.enable_bindings()
        self.sheet.grid(row=0, column=0, sticky="nswe")
        self.sheet.set_options(auto_resize_columns=150)
        self.sheet.readonly_columns(0, readonly=True)
        self.sheet.highlight_columns(columns=[0],
                                     bg="lightgray",
                                     fg="gray",
                                     redraw=True)
        self.sheet.bind("<<SheetSelect>>", self.on_row_selected)

    def on_row_selected(self, event=None):
        try:
            sel = self.sheet.get_currently_selected()
            # sel besitzt in tksheet üblicherweise .row und .column
            if sel and getattr(sel, "row", None) is not None and getattr(sel, "column", None) is not None:
                self.row = sel.row
                self.col = sel.column
            else:
                # Fallback: irgendeine ausgewählte Zeile aus dem Set
                rows = self.sheet.get_selected_rows()  # set
                if not rows:
                    return
                self.row = sorted(rows)[-1]  # z.B. höchste Zeilennummer
            values = self.sheet.get_row_data(self.row)
        except Exception as e:
            tk.messagebox.showerror("Error", str(e))

    def get_data(self):
        return self.sheet.get_sheet_data()

    def add_line(self):
        data: list[str] = []
        key = simpledialog.askstring("Paraglide key", "Enter the new paraglide key:")
        data.append(key)
        for lang in self.langs:
            data.append(key)

        self.sheet.insert_row(row=data, idx=None)
        self.sheet.see(row=self.sheet.get_total_rows() - 1)

    def translate(self):
        deepl = DeepLConnection()
        fromlang = self.langs[self.col - 1]
        for index, ll in enumerate(self.langs):
            if ll == fromlang:
                continue
            if self.data[self.row][index + 1] == self.data[self.row][0] or self.data[self.row][index + 1] == "":
                deepl_lang = ll.upper()
                if deepl_lang == "EN":
                    deepl_lang = "EN-US"
                try:
                    result = str(deepl.client.translate_text(self.data[self.row][self.col], target_lang=deepl_lang))
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    return
                self.sheet.set_cell_data(self.row, index + 1, result)

    def sort_data_by_key(self):
        self.sheet.sort_rows_by_column(column=0, reverse=False)



