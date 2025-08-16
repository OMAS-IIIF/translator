import json
import os
import shutil
import tkinter as tk
from pprint import pprint
from tkinter import ttk, filedialog
from pathlib import Path
import sys
import platform
from typing import Dict, List, Optional

from paraglidetranslator.components.deeplconnection import DeepLConnection
from paraglidetranslator.components.deepl_key import DeepLKey
from paraglidetranslator.components.langeditor import LangEditor

current_os = platform.system()  # "Windows", "Darwin" (macOS), "Linux"

#
# <a href="https://www.freepik.com/icons/translation/8#uuid=462e7e58-4e23-49be-a37a-d7fb64545b36">Icon by rizky maulidhani</a>
#

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
    data: list[list[str]]
    json_files: dict[str, Path]
    lang_editor_w: LangEditor
    deepl_key: str
    directory: Path

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data = {}
        self.langs = []
        self.lang_editor_w = None
        self.json_files = {}

        self._parent = parent
        ttk.Frame.__init__(self, *args, **kwargs)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        menubar = self.create_menubar()

        taskbar = TaskBar(self, padding=10)
        self.open_w = ttk.Button(taskbar, text="Open...", command=self.opendir)
        self.open_w.pack(side=tk.LEFT)
        self.save_w = ttk.Button(taskbar, text="Save", command=self.save)
        self.save_w.pack(side=tk.LEFT)
        self.add_w = ttk.Button(taskbar, text="Add key...", state="disabled", command=self.add_empty_line)
        self.add_w.pack(side=tk.LEFT)
        self.sort_w = ttk.Button(taskbar, text="Sort", state="disabled", command=self.sort_data)
        self.sort_w.pack(side=tk.LEFT)
        self.purge_w = ttk.Button(taskbar, text="Purge", state="disabled", command=self.purge)
        self.purge_w.pack(side=tk.LEFT)

        self.translate_w = ttk.Button(taskbar, state="disabled", text="Translate", command=self.translate)
        self.translate_w.pack(side=tk.LEFT)

        #self.all_w = ttk.Button(taskbar, state="disabled", text="Translate all", command=self.translate_all)
        #self.all_w.pack(side=tk.LEFT)

        self.quit_w = ttk.Button(taskbar, text="QUIT", command=self.quit)
        self.quit_w.pack(side=tk.RIGHT)

        taskbar.pack(side=tk.TOP, fill=tk.X)

        access = DeepLKey()
        DeepLConnection(access.deepl_key)

    def create_menubar(self):
        menubar = tk.Menu(self._parent)
        self._parent.configure(menu=menubar)
        menu_file = tk.Menu(menubar, tearoff=0)
        menu_action = tk.Menu(menubar, tearoff=0)
        #menu_language = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label="Open...", command=self.opendir)
        menu_file.add_command(label="Save", command=self.save)
        menu_file.add_command(label="Purge", command=self.purge)

        menubar.add_cascade(menu=menu_action, label='Action')
        menu_action.add_command(label="Add line", command=self.add_empty_line)
        # menu_action.add_command(label="Translate", command=self.add_empty_line)
        #
        return menubar

    def quit(self):
        self._parent.destroy()

    def dict_by_lang_to_rows_with_key(
            self,
            data: dict[str, dict[str, str]],  # {lang: {key: value}}
            languages: Optional[List[str]] = None,  # gewünschte Spaltenreihenfolge der Sprachen
            keys: Optional[List[str]] = None,  # gewünschte Zeilenreihenfolge der Keys
            fill: str = ""  # Fallback für fehlende Werte
    ) -> list[list[str]]:
        if not data:
            return [], []

        # Sprachenreihenfolge
        langs = languages or sorted(data.keys())

        # Schlüsselreihenfolge (stabile Reihenfolge nach erstem Auftauchen pro langs)
        if keys is None:
            seen = set()
            ordered_keys: list[str] = []
            for lang in langs:
                for k in data.get(lang, {}).keys():
                    if k not in seen:
                        seen.add(k)
                        ordered_keys.append(k)
            keys = ordered_keys

        # Zeilen aufbauen: [key, val(lang1), val(lang2), ...]
        rows: List[List[str]] = [
            [k] + [data.get(lang, {}).get(k, fill) for lang in langs]
            for k in keys
        ]
        return langs, rows

    def opendir(self):
        dir = tk.filedialog.askdirectory(initialdir=os.getcwd())
        self.directory = Path(dir)
        files = list(self.directory.glob("??.json"))
        tmpdata: dict[str,dict[str, str]] = {}  # dict[lang: dict[key, value]]
        for file in files:
            filepath = Path(file)
            with open(filepath, "r", encoding="utf-8") as fhandle:
                lang = filepath.stem
                tmpdata[lang] = json.load(fhandle)
                self.json_files[lang] = filepath
        # dict[lang: dict[key, value]]  ==> dict[key: dict[lang, value]]
        self.langs, data = self.dict_by_lang_to_rows_with_key(tmpdata)
        del data[0]

        self.lang_editor_w = LangEditor(self, langs=self.langs, data=data)
        self.lang_editor_w.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.add_w.configure(state=tk.ACTIVE)
        self.add_w.configure(state=tk.ACTIVE)
        self.sort_w.configure(state=tk.ACTIVE)
        self.purge_w.configure(state=tk.ACTIVE)
        self.translate_w.configure(state=tk.ACTIVE)

    def save(self):
        #
        # first let's make backup copies
        #
        if not self.json_files:
            return
        for ll, p in self.json_files.items():
            backups = list(self.directory.glob(f"{ll}.???.json"))
            version = 0
            for backup in backups:
                parts = backup.stem.split(".")
                tmp = int(parts[-1])
                if tmp > version:
                    version = tmp
            version += 1
            target = p.with_stem(f"{p.stem}.{version:03}")
            shutil.copy2(p, target)
        #
        # reshuffle for writing files
        #   list[list[key|value]] ==> dict[lang: dict[key, value]]
        #
        res: dict[str,dict[str, str]] = {}
        for ll in self.langs:
            res[ll] = {'$schema': 'https://inlang.com/schema/inlang-message-format'}
        key: str = ""
        data = self.lang_editor_w.get_data()
        for row in data:
            for index, cell in enumerate(row):
                if index == 0:
                    key = cell
                    continue
                res[self.langs[index - 1]][key] = cell
        for ll in res.keys():
            #print("Writing... ", self.json_files[ll])
            #print(json.dumps(res[ll], indent=4, ensure_ascii=False))
            with open(self.json_files[ll], "w", encoding="utf-8") as fhandle:
                json.dump(res[ll], fhandle, indent=4, ensure_ascii=False)

    def purge(self):
        backups = list(self.directory.glob(f"??.???.json"))
        for backup in backups:
            delpath = Path(backup)
            delpath.unlink()

    def sort_data(self):
        self.lang_editor_w.sort_data_by_key()

    def add_empty_line(self):
        if self.lang_editor_w:
            self.lang_editor_w.add_line()

    def translate(self):
        self.lang_editor_w.translate()


class App(tk.Tk):

    def __init__(self, title, *args, **kwargs):
        super().__init__(title, *args, **kwargs)
        #self.title = 'LocoPy V01'
        self.wm_title('Translator V0.1.1')
        self.geometry('1200x700+100+100')


def main():
    root = App('Translator V0.1.1')
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

if __name__ == '__main__':
    main()
