import json
import os
from tkinter import messagebox, simpledialog


class DeepLKey:
    __deepl_key: str

    def __init__(self, deepl_key: str | None = None):
        key_file_path = os.path.expanduser('~/.deepl_key.json')
        try:
            with open(key_file_path) as f:
                jsonkey = json.load(f)
                self.__deepl_key = jsonkey['key']
        except FileNotFoundError:
            # If the file doesn't exist, prompt the user for the key
            # parent.withdraw()  # Hide the root window
            messagebox.showinfo("Key Required", "The DeepL API key file was not found. Please enter your key.")
            key = simpledialog.askstring("DeepL API Key", "Enter your DeepL API key:")
            if key:
                # Save the key to the file for future use
                self.save_key_to_file(key)
                self.__deepl_key = key
                return
            else:
                messagebox.showerror("Error", "No key provided. Exiting.")
                raise SystemExit("No DeepL API key provided.")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "The key file is corrupted. Please check the file or provide a new key.")
            raise SystemExit("Invalid key file.")

    def save_key_to_file(self, key):
        # Save the key to the file in JSON format
        key_file_path = os.path.expanduser('~/.deepl_key.json')
        key_data = {'key': key}
        with open(key_file_path, 'w') as f:
            json.dump(key_data, f)

    @property
    def deepl_key(self):
        return self.__deepl_key

