# Translator

Translator is a little, handy tool to manage the language files of a web application
using based on [paraglide](https://inlang.com/m/gerre34r/library-inlang-paraglideJs).
It uses a connection to [DeepL API](https://www.deepl.com/de/products/api). In order to use the
translator, You need at least a (free) account for the DeepL API. When You start up the translator
for the first time, it will ask for the DeepL API access key (See DeepL documentation how to get it)

## Usage of translator

After starting the translator app, You choose "OPEN" and select the directory where the
language specific JSON files are located (.../messages/en.json, .../messages/de.json etc.).
All the files will be read and displayed in a spreadsheet like manner.

### JSON input
For preparing the JSON file (which consists of a "key" for the text and the translation), e.g.
for german:
```json
{
  "$schema": "https://inlang.com/schema/inlang-message-format",
  "hello_world": "Hello, {name} from de-ch!",
  "unkown_api_error": "Unbekannter API-Fehler ({num})!"
}
```
If a key is not existing in a file, the corresponding field will be filled with
the key as "translated" value. The translation may be entered by hand, or
You can choose the base language and perform an automatic translation based
ön DeepL.

### Saving
Before saving, the "old" files are backuped with a name <lang>.XXX.json, where
XXX is a number 001, 002, 003, ...

The purge button removes *all* the backup files (for cleaning up).
