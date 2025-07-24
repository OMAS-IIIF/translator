import platform
import tkinter as tk
from pprint import pprint
from tkinter import ttk, simpledialog

from paraglidetranslator.components.Translate import Translate


class LangEditor(ttk.Frame):
    keys: dict[str, tk.StringVar]
    langs: [str]
    fromlang: dict[str, tk.StringVar]
    scrollable_frame: ttk.Frame

    def __init__(self,
                 parent: tk.Widget,
                 data: dict[str, dict[str, tk.StringVar]],  # dict[key: dict[lang, value]]
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(padding=5, borderwidth=3, relief=tk.RIDGE)
        self.keys = {}
        self.langs = []
        self.fromlang = {}
        self.data = data  # dict[key: dict[lang, value]]
        self.parent = parent

        # Create a canvas and a scrollbar
        self.canvas_w = tk.Canvas(self)
        scrollbar_w = ttk.Scrollbar(self, orient="vertical", command=self.canvas_w.yview)
        self.scrollable_frame = ttk.Frame(self.canvas_w)

        # Configure the scrollable frame
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas_w.configure(
                scrollregion=self.canvas_w.bbox("all")
            )
        )

        # Create a window inside the canvas
        window = self.canvas_w.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Make the frame expand when resized
        def _on_frame_resize(event):
            self.canvas_w.itemconfig(window, width=event.width)

        self.bind("<Configure>", _on_frame_resize)

        # Scroll event handling (macOS trackpad fix included)
        def _on_mousewheel(event):
            if platform.system() == "Darwin":  # macOS trackpad support
                self.canvas_w.yview_scroll(-1 * int(event.delta // 3), "units")  # Smoother scrolling
            else:
                self.canvas_w.yview_scroll(-1 * (event.delta // 120), "units")  # Windows/Linux

        def _on_scroll_linux(event):
            self.canvas_w.yview_scroll(-1 * (event.num - 4), "units")

        # Bind scrolling events
        if platform.system() == "Darwin":
            self.canvas_w.bind_all("<MouseWheel>", _on_mousewheel)  # macOS trackpad
        else:
            self.canvas_w.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
            self.canvas_w.bind_all("<Button-4>", _on_scroll_linux)  # Linux (scroll up)
            self.canvas_w.bind_all("<Button-5>", _on_scroll_linux)  # Linux (scroll down)

        self.canvas_w.configure(yscrollcommand=scrollbar_w.set)

        # Layout for scrollbar and canvas
        self.canvas_w.grid(row=0, column=0, sticky="nsew")
        scrollbar_w.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Build the form inside `scrollable_frame`
        label = ttk.Label(self.scrollable_frame, text="Key")
        label.grid(row=0, column=0, sticky="nsew")
        self.scrollable_frame.columnconfigure(0, weight=1)

        row = 0
        col = 1
        for key, tmp in self.data.items():
            if row == 0:
                for lang in tmp.keys():
                    self.langs.append(lang)
                    ttk.Label(self.scrollable_frame, text=lang.upper()).grid(row=0, column=col, sticky="nsew")
                    self.scrollable_frame.columnconfigure(col, weight=1)
                    col += 1
                gaga = ttk.Label(self.scrollable_frame, text="Action", width=3)
                gaga.grid(row=0, column=col, sticky="nsew")
                gaga.grid_propagate(False)
                self.scrollable_frame.columnconfigure(col, weight=0)
                row += 1
                continue
            self.keys[key] = tk.StringVar(self.scrollable_frame, key)
            keyentry = ttk.Entry(self.scrollable_frame, textvariable=self.keys[key])
            keyentry.grid(row=row, column=0, sticky="nsew")
            col = 1
            for lang in self.langs:
                if tmp.get(lang, None) is None:
                    tmp[lang] = tk.StringVar(self.scrollable_frame, key)
                    entry = ttk.Entry(self.scrollable_frame, textvariable=tmp[lang], foreground="red")
                else:
                    if tmp[lang] == key:
                        entry = ttk.Entry(self.scrollable_frame, textvariable=tmp[lang], foreground="red")
                    else:
                        entry = ttk.Entry(self.scrollable_frame, textvariable=tmp[lang])
                entry.grid(row=row, column=col, sticky="nsew")
                col += 1
            self.fromlang[key] = tk.StringVar(self.scrollable_frame, self.langs[0])
            translate = Translate(self.scrollable_frame, data=data, key=key, langs=self.langs)
            translate.grid(row=row, column=col, sticky="nsew")
            translate.grid_propagate(False)
            row += 1

        # Ensure frame resizes dynamically
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas_w.configure(scrollregion=self.canvas_w.bbox("all")))

        # Ensure resizing keeps the width of the frame
        def _update_width(event):
            self.canvas_w.itemconfig(window, width=self.canvas_w.winfo_width())

        self.canvas_w.bind("<Configure>", _update_width)

        # Make sure the canvas scrolls with the mouse wheel inside the widget
        self.scrollable_frame.bind("<Enter>", lambda _: self.canvas_w.bind_all("<MouseWheel>", _on_mousewheel))
        self.scrollable_frame.bind("<Leave>", lambda _: self.canvas_w.unbind_all("<MouseWheel>"))

    def add_line(self):
        key = simpledialog.askstring("Paraglide key", "Enter the new paraglide key:")
        self.keys[key] = tk.StringVar(self.scrollable_frame, key)
        self.data[key] = {}

        row = len(self.data) + 1
        keyentry = ttk.Entry(self.scrollable_frame, textvariable=self.keys[key])
        keyentry.grid(row=row, column=0, sticky="nsew")
        col = 1
        for lang in self.langs:
            self.data[key][lang] = tk.StringVar(self.scrollable_frame, key)
            entry = ttk.Entry(self.scrollable_frame, textvariable=self.data[key][lang], foreground="red")
            entry.grid(row=row, column=col, sticky="nsew")
            col += 1
        self.fromlang[key] = tk.StringVar(self.scrollable_frame, self.langs[0])
        translate = Translate(self.scrollable_frame, data=self.data, key=key, langs=self.langs)
        translate.grid(row=row, column=col, sticky="nsew")
        translate.grid_propagate(False)
        self.parent.update_idletasks()
        self.canvas_w.yview_moveto(1.0)


