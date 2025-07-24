import json
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
import sys
import platform

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
    data: dict[str, dict[str, tk.StringVar]]  # dict[key: dict[lang, value]]
    json_files: dict[str, Path]
    lang_editor_w: LangEditor
    deepl_key: str
    directory: Path

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
        self.save_w = ttk.Button(taskbar, text="Save", command=self.save)
        self.save_w.pack(side=tk.LEFT)
        self.add_w = ttk.Button(taskbar, text="Add key...", state="disabled", command=self.add_empty_line)
        self.add_w.pack(side=tk.LEFT)
        self.sort_w = ttk.Button(taskbar, text="Sort", state="disabled", command=self.sort_data)
        self.sort_w.pack(side=tk.LEFT)
        self.purge_w = ttk.Button(taskbar, text="Purge", state="disabled", command=self.purge)
        self.purge_w.pack(side=tk.LEFT)

        self.all_w = ttk.Button(taskbar, state="disabled", text="Translate all", command=self.translate_all)
        self.all_w.pack(side=tk.LEFT)

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

        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label="Open...", command=self.opendir)
        menu_file.add_command(label="Save", command=self.save)
        menu_file.add_command(label="Purge", command=self.purge)

        menubar.add_cascade(menu=menu_action, label='Action')
        menu_action.add_command(label="Add line", command=self.add_empty_line)
        menu_action.add_command(label="Translate all", command=self.add_empty_line)

        return menubar

    def quit(self):
        self._parent.destroy()

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
        for lang, tmp in tmpdata.items():
            for key, value in tmp.items():
                if self.data.get(key, None) is None:
                    self.data[key] = {}
                self.data[key][lang] = tk.StringVar(self, value)
        self.lang_editor_w = LangEditor(self, data=self.data)
        self.lang_editor_w.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.add_w.configure(state=tk.ACTIVE)
        self.all_w.configure(state=tk.ACTIVE)
        self.sort_w.configure(state=tk.ACTIVE)
        self.purge_w.configure(state=tk.ACTIVE)

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
        #   dict[key: dict[lang, value]] ==> dict[lang: dict[key, value]]
        #
        res: dict[str,dict[str, str]] = {}
        for key, tmpdata in self.data.items():
            for lang, value in tmpdata.items():
                if res.get(lang) is None:
                    res[lang] = {}
                res[lang][key] = value.get()
        for ll in res.keys():
            with open(self.json_files[ll], "w", encoding="utf-8") as fhandle:
                json.dump(res[ll], fhandle, indent=4, ensure_ascii=False)

    def purge(self):
        backups = list(self.directory.glob(f"??.???.json"))
        for backup in backups:
            delpath = Path(backup)
            delpath.unlink()

    def sort_data(self):
        self.lang_editor_w.destroy()
        self.data = dict(sorted(self.data.items()))
        self.lang_editor_w = LangEditor(self, data=self.data)
        self.lang_editor_w.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.add_w.configure(state=tk.ACTIVE)
        self.all_w.configure(state=tk.ACTIVE)
        self.sort_w.configure(state=tk.ACTIVE)
        self.purge_w.configure(state=tk.ACTIVE)

    def add_empty_line(self):
        if self.lang_editor_w:
            self.lang_editor_w.add_line()

    def translate_all(self):
        deepl = DeepLConnection()
        for key, tmpdata in self.data.items():
            for lang, value in tmpdata.items():
                if value.get() == key or value.get() == "":
                    deepl_lang = lang.upper()
                    if deepl_lang == "EN":
                        deepl_lang = "EN-US"
                    try:
                        result = deepl.client.translate_text(self.data[key][lang].get(), target_lang=deepl_lang)
                    except Exception as e:
                        print(e)
                        result = key
                    self.data[key][lang].set(result)


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
