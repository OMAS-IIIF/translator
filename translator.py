import io
import json
import os
import tkinter as tk
from pprint import pprint
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import sys
import platform

import deepl
from deepl import DeepLClient

from components.connection import Connection
from components.deepl_key import DeepLKey
from components.langeditor import LangEditor

current_os = platform.system()  # "Windows", "Darwin" (macOS), "Linux"


# Get absolute path for resources
def resource_path(relative_path):
    """Get absolute path for bundled resources (useful for PyInstaller)."""
    if getattr(sys, 'frozen', False):  # Running in a PyInstaller bundle
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path


class TaskBar(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(relief=tk.GROOVE, borderwidth=2)


class MainWindow(ttk.Frame):
    data: dict[str, dict[str, tk.StringVar]]  # dict[key: dict[lang, value]]
    json_files: dict[str,Path]
    lang_editor_w: LangEditor
    deepl_key: str

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data = {}
        self.lang_editor_w = None
        self.json_files = {}

        self._parent = parent
        ttk.Frame.__init__(self, *args, **kwargs)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        menubar = self.create_menubar()

        taskbar = TaskBar(self, padding=10)
        self.open_w = ttk.Button(taskbar, text="Open...", command=self.opendir)
        self.open_w.pack(side=tk.LEFT)
        self.save_w = ttk.Button(taskbar, text="Save...")
        self.save_w.pack(side=tk.LEFT)
        self.add_w = ttk.Button(taskbar, text="Add key...", state="disabled", command=self.add_empty_line)
        self.add_w.pack(side=tk.LEFT)

        self.all_w = ttk.Button(taskbar, state="disabled", text="Translate all")
        self.all_w.pack(side=tk.LEFT)

        self.quit_w = ttk.Button(taskbar, text="QUIT", command=self.quit)
        self.quit_w.pack(side=tk.RIGHT)

        taskbar.pack(side=tk.TOP, fill=tk.X)

        # key_file_path = os.path.expanduser('~/.deepl_key.json')
        # try:
        #     with open(key_file_path) as f:
        #         jsonkey = json.load(f)
        #         self.deepl_key = jsonkey['key']
        # except FileNotFoundError:
        #     # If the file doesn't exist, prompt the user for the key
        #     #parent.withdraw()  # Hide the root window
        #     messagebox.showinfo("Key Required", "The DeepL API key file was not found. Please enter your key.")
        #     key = simpledialog.askstring("DeepL API Key", "Enter your DeepL API key:")
        #     if key:
        #         # Save the key to the file for future use
        #         self.save_key_to_file(key)
        #         return
        #     else:
        #         messagebox.showerror("Error", "No key provided. Exiting.")
        #         raise SystemExit("No DeepL API key provided.")
        # except json.JSONDecodeError:
        #     messagebox.showerror("Error", "The key file is corrupted. Please check the file or provide a new key.")
        #     raise SystemExit("Invalid key file.")
        access = DeepLKey()
        Connection(access.deepl_key)

    # def save_key_to_file(self, key):
    #     # Save the key to the file in JSON format
    #     key_file_path = os.path.expanduser('~/.deepl_key.json')
    #     key_data = {'key': key}
    #     with open(key_file_path, 'w') as f:
    #         json.dump(key_data, f)

    def create_menubar(self):
        menubar = tk.Menu(self._parent)
        self._parent.configure(menu=menubar)
        menu_connect = tk.Menu(menubar)
        menu_edit = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_connect, label='Connect')
        menubar.add_cascade(menu=menu_edit, label='Edit')

        return menubar

    def quit(self):
        self._parent.destroy()

    def opendir(self):
        dir = tk.filedialog.askdirectory(initialdir=os.getcwd())
        directory = Path(dir)
        files = list(directory.glob("*.json"))
        tmpdata: dict[str,dict[str, str]] = {}  # dict[lang: dict[key, value]]
        for file in files:
            filepath = Path(file)
            with open(filepath, "r", encoding="utf-8") as fhandle:
                lang = filepath.stem
                tmpdata[lang] = json.load(fhandle)
                self.json_files[lang] = filepath
        # dict[lang: dict[key, value]]  ==> dict[key: dict[lang, value]]
        for lang, tmp in tmpdata.items():
            for key, value in tmp.items():
                if self.data.get(key, None) is None:
                    self.data[key] = {}
                self.data[key][lang] = tk.StringVar(self, value)
        self.lang_editor_w = LangEditor(self, self.data)
        self.lang_editor_w.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.add_w.configure(state="enabled")
        self.all_w.configure(state="enabled")

    def add_empty_line(self):
        if self.lang_editor_w:
            self.lang_editor_w.add_line()


class App(tk.Tk):

    def __init__(self, title, *args, **kwargs):
        super().__init__(title, *args, **kwargs)
        #self.title = 'LocoPy V01'
        self.wm_title('Translator V0.1')
        self.geometry('1200x700+100+100')


if __name__ == '__main__':
    root = App('LocoPy V0.1')
    main = MainWindow(root)

    #
    # Create the application icon
    #
    if current_os == "Windows":
        icon_path = resource_path("images/translator.ico")  # Windows uses .ico
        root.iconbitmap(icon_path)

    elif current_os == "Darwin":  # macOS
        icon_path = resource_path("images/translator.icns")  # macOS prefers .icns in app bundles
        try:
            from AppKit import NSApplication, NSImage  # macOS-specific

            app = NSApplication.sharedApplication()
            img = NSImage.alloc().initByReferencingFile_(str(icon_path))
            app.setApplicationIconImage_(img)
        except ImportError:
            print("AppKit not available; ensure it's installed via 'pip install pyobjc'.")

    elif current_os == "Linux":
        icon_path = resource_path("images/translator.png")  # Linux uses .png
        icon_img = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon_img)

    else:
        print(f"Warning: Unsupported OS ({current_os}). No icon applied.")

    root.mainloop()
