import os
import platform
import tkinter as tk
from tkinter import ttk

from components.Translate import Translate


class LangEditor(ttk.Frame):
    keys: dict[str, tk.StringVar]
    langs: [str]
    fromlang: dict[str, tk.StringVar]

    def __init__(self,
                 parent: tk.Widget,
                 data: dict[str, dict[str, tk.StringVar]],
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(padding=5, borderwidth=3, relief=tk.RIDGE)
        self.keys = {}
        self.langs = []
        self.fromlang = {}

        # Create a canvas and a scrollbar
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure the scrollable frame
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        # Create a window inside the canvas
        window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Make the frame expand when resized
        def _on_frame_resize(event):
            canvas.itemconfig(window, width=event.width)

        self.bind("<Configure>", _on_frame_resize)

        # Scroll event handling (macOS trackpad fix included)
        def _on_mousewheel(event):
            if platform.system() == "Darwin":  # macOS trackpad support
                canvas.yview_scroll(-1 * int(event.delta // 3), "units")  # Smoother scrolling
            else:
                canvas.yview_scroll(-1 * (event.delta // 120), "units")  # Windows/Linux

        def _on_scroll_linux(event):
            canvas.yview_scroll(-1 * (event.num - 4), "units")

        # Bind scrolling events
        if platform.system() == "Darwin":
            canvas.bind_all("<MouseWheel>", _on_mousewheel)  # macOS trackpad
        else:
            canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
            canvas.bind_all("<Button-4>", _on_scroll_linux)  # Linux (scroll up)
            canvas.bind_all("<Button-5>", _on_scroll_linux)  # Linux (scroll down)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Layout for scrollbar and canvas
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Build the form inside `scrollable_frame`
        label = ttk.Label(scrollable_frame, text="Key")
        label.grid(row=0, column=0, sticky="nsew")
        scrollable_frame.columnconfigure(0, weight=1)

        row = 0
        col = 1
        for key, tmp in data.items():
            if row == 0:
                for lang in tmp.keys():
                    self.langs.append(lang)
                    ttk.Label(scrollable_frame, text=lang.upper()).grid(row=0, column=col, sticky="nsew")
                    scrollable_frame.columnconfigure(col, weight=1)
                    col += 1
                gaga = ttk.Label(scrollable_frame, text="Action", width=3)
                gaga.grid(row=0, column=col, sticky="nsew")
                gaga.grid_propagate(False)
                scrollable_frame.columnconfigure(col, weight=0)
                row += 1
                continue
            self.keys[key] = tk.StringVar(scrollable_frame, key)
            keyentry = ttk.Entry(scrollable_frame, textvariable=self.keys[key])
            keyentry.grid(row=row, column=0, sticky="nsew")
            col = 1
            for lang in self.langs:
                if tmp.get(lang, None) is None:
                    tmp[lang] = tk.StringVar(scrollable_frame, key)
                entry = ttk.Entry(scrollable_frame, textvariable=tmp[lang])
                entry.grid(row=row, column=col, sticky="nsew")
                col += 1
            self.fromlang[key] = tk.StringVar(scrollable_frame, self.langs[0])
            translate = Translate(scrollable_frame, data=data, key=key, langs=self.langs)
            translate.grid(row=row, column=col, sticky="nsew")
            translate.grid_propagate(False)
            row += 1

        # Ensure frame resizes dynamically
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Ensure resizing keeps the width of the frame
        def _update_width(event):
            canvas.itemconfig(window, width=canvas.winfo_width())

        canvas.bind("<Configure>", _update_width)

        # Make sure the canvas scrolls with the mouse wheel inside the widget
        scrollable_frame.bind("<Enter>", lambda _: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        scrollable_frame.bind("<Leave>", lambda _: canvas.unbind_all("<MouseWheel>"))

# class LangEditor(ttk.Frame):
#     keys: dict[str, tk.StringVar]
#
#     def __init__(self,
#                  parent: tk.Widget,
#                  data: dict[str, dict[str, tk.StringVar]],
#                  *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#         self.keys = {}
#
#
#         label = ttk.Label(self, text="Key")
#         label.grid(row=0, column=0, sticky="nsew")
#         self.columnconfigure(0, weight=1)
#         row = 0
#         col = 1
#         for key, tmp in data.items():
#             if (row == 0):
#                 for lang in tmp.keys():
#                     ttk.Label(self, text=lang.upper()).grid(row=0, column=col, sticky="nsew")
#                     col += 1
#                     self.columnconfigure(col, weight=1)
#                 row += 1
#                 continue
#             self.keys[key] = tk.StringVar(self, key)
#             keyentry = ttk.Entry(self, textvariable=self.keys[key])
#             keyentry.grid(row=row, column=0, sticky="nsew")
#             col = 1
#             for lang, value in tmp.items():
#                 entry = ttk.Entry(self, textvariable=value)
#                 entry.grid(row=row, column=col, sticky="nsew")
#                 col += 1
#             row += 1

