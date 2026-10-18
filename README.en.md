# PoP Save Tool — editor for Prince of Persia: The Lost Crown

*[Italiano](README.md) · English*

Reads, shows and **edits** the game saves (`PopSaveGame*.AlkSave`,
`Progression*.AlkContent`, `GameOptions*.AlkContent`, screenshots).
The files are not encrypted: they are gzip-compressed JSON (details in
[ANALISI_FORMATO.en.md](ANALISI_FORMATO.en.md); Italian version:
[ANALISI_FORMATO.md](ANALISI_FORMATO.md)).

Requirements: **Python 3.8+** (no external library). The web editor interface is
available in Italian, English, German, Spanish and French.

## Windows executable

`dist/PoPSaveEditor-win64.zip` contains the standalone exe (no Python needed)
together with the READMEs and the quick guides. Unzip it anywhere and double-click
`PoPSaveEditor.exe`: the web editor starts on `127.0.0.1:8765` (next free port if
busy). From the command line it behaves like the script, e.g.
`PoPSaveEditor.exe info`.

To rebuild it (Windows, tested with Python 3.14):

```bash
python -m pip install pyinstaller
python -m PyInstaller PoPSaveEditor.spec --noconfirm
powershell -Command "Compress-Archive -Path 'dist\PoPSaveEditor-win64\*' -DestinationPath 'dist\PoPSaveEditor-win64.zip' -Force"
```

## Windows installer

`dist/PoPSaveEditor-Setup.exe` installs the editor **for the current user**, with
no administrator rights:

- default folder `%LOCALAPPDATA%\Programs\PoPSaveEditor` (can be changed);
- Start menu shortcut, optional desktop shortcut;
- entry in Windows **Apps & features**, with uninstall;
- the uninstaller removes program, shortcuts and registry entry but **leaves**
  the game saves and the backups in `%LOCALAPPDATA%\PoPSaveTool` untouched.

Double-click for the guided installation. From the command line:

```bash
PoPSaveEditor-Setup.exe --silent                  # silent installation
PoPSaveEditor-Setup.exe --uninstall               # guided uninstall
PoPSaveEditor-Setup.exe --uninstall --silent      # silent uninstall
```

`/S` works like `--silent` from `cmd.exe` and PowerShell (in Git Bash use the long
form, which is not rewritten as a path). The exe is not digitally signed:
SmartScreen may ask for confirmation.

To rebuild the installer (after rebuilding `dist/PoPSaveEditor.exe` and the docs
inside `dist/PoPSaveEditor-win64`):

```bash
python -m PyInstaller PoPSaveEditor-Setup.spec --noconfirm
```

## Quick start (web interface)

```bash
python popedit.py web
```

It opens `http://127.0.0.1:8765` with:

- **Overview** – readable summary of the save and folder selection
- **Edit** – tables with readable names for fast travels and challenges, plus the
  editable values: crystals, health, upgrades, abilities, stones of knowledge,
  inventory, game options
- **Screenshots** – the 13 thumbnails saved by the game
- **JSON** – the raw content of every file, for free editing
- **Backups** – list of backups with one-click restore

The language of the interface can be switched from the selector in the top bar
(Italiano, English, Deutsch, Español, Français); the choice is remembered. Game
data (item names, level codes and region names) is not translated.

The server listens on `127.0.0.1` only, so it is not reachable from outside.
Close the game before applying changes.

## Where the saves are (and how to pick them)

The game saves in Documents, in a folder per profile:

```
Documents\My Games\Prince Of Persia The Lost Crown\<profile>\Saves\
    SaveSlot0\Save_<number>\PopSaveGameSlot0Index0.AlkSave
    SaveSlot1\Save_<number>\...
    SaveSlot2\Save_<number>\...
    SaveSlot3\Save_<number>\...
```

If OneDrive synchronises Documents, the path starts with `OneDrive\DOCUMENTS`.
The main file is `PopSaveGameSlot<N>Index0.AlkSave`; next to it you find
`Progression*.AlkContent`, `GameOptions*.AlkContent` and the screenshots.

In the **Overview** tab the **Save folder** box shows the active path, lists the
saves it found and lets you:

- open another save from the drop-down list;
- use **Browse...** to pick a folder with the Windows dialog (the `Save_...`
  folder, the `SaveSlotN` or the profile folder; with several saves the newest is
  used);
- read **Where are they?** with the full path and the OneDrive/cloud notes.

The choice is remembered in `%LOCALAPPDATA%\PoPSaveTool\last_save.txt` and
restored next time; if the folder disappears, the tool falls back to the one
indicated by the game in `lastSavedFolder.txt`.

From the command line, `python popedit.py saves` lists them; `--save "path"`
picks a specific folder for that command.

Careful: with Ubisoft/Steam cloud saves enabled, turn off syncing for this game
while editing, otherwise the cloud may overwrite your changes (or the other way
round).

## Command line

```bash
python popedit.py info                        # summary of the most recent save
python popedit.py info --save "path"          # on a specific save
python popedit.py saves                       # list saves and where they are

python popedit.py extract -o estratti         # readable JSON + .jpg screenshots
python popedit.py pack -i estratti            # repack the edited JSON

python popedit.py set crystals=99999 playtime=2:00:00 completion=75
python popedit.py set hp=500 sword=4 bow=4 quiver=4 stones=3

python popedit.py backups                     # list backups
python popedit.py restore                     # restore the latest backup
```

Keys accepted by `set`: `crystals` (currency), `playtime` (`HH:MM:SS` or seconds),
`completion` (percentage or 0–1), `hp`, `sword`, `bow`, `quiver`, `potion_count`,
`potion_effect`, `health_upgrades`, `stones` (level of every stone).

### Quick actions: removed

The three automatic actions (`reveal_map`, `unlock_fast_travel`,
`complete_challenges`) are **no longer part of the project**: in-game testing
showed that force-filling the map bitmaps left the map stuck and no longer
visible, and those bulk writes can also leave the save in a state the game does
not like.

The editor now only **reads** map, fast travels and challenges (tables in the Edit
tab) and writes only the values you choose, one at a time. The readable names
(region/level for fast travels, lesson name for challenges) come from
`popdata.py` (included in the sources), extracted from the game bundles.

If you used an older version and the map is gone, open the **Backups** tab and
restore the backup made before that action (or copy back the save folder you
kept by hand).

If `--save` is omitted, the tool uses the last folder written by the game in
`lastSavedFolder.txt` (for example `…\SaveSlot3\Save_134359460918773693`).

## Safety

- **Every write creates a full backup first** in
  `%LOCALAPPDATA%\PoPSaveTool\backups\<save_folder>__<date-time>`.
- Restoring saves the current state too, so you can always go back.
- Writing is atomic (temporary file + replace) and updates the sizes in the
  container header.
- An unmodified file is repacked **identical** to the original.

Advice: before trying, copy the save folder by hand and, if you use Ubisoft/Steam
cloud saves, disable syncing for that game.

## Layout

```
pop-save-tool/
├─ popsave.py            library: container read/write, backups, patches
├─ popdata.py            extracted game data (23 fast travels, 13 lessons)
├─ i18n.py               translations (IT, EN, DE, ES, FR)
├─ popedit.py            command line interface and web server
├─ installer.py          per-user Windows installer
├─ web/                  web interface (HTML/CSS/JS)
├─ tests/selfcheck.py    automatic check on a copy of the save
├─ estratti/             readable copy of the analysed save (JSON + JPG)
├─ README.md             Italian documentation
├─ dist/                 exe, zip, installer and quick guides (LEGGIMI.txt)
├─ ANALISI_FORMATO.en.md full format analysis (English)
└─ ANALISI_FORMATO.md    the same analysis in Italian
```

To re-run the checks: `python tests/selfcheck.py` (it works on a temporary copy
and never touches the original). The test also verifies that the quick actions no
longer exist, that the translations are complete and that reading map, fast
travels and challenges writes nothing to the save.

`popdata.py` is already included: the editor needs no extra library. Only to
regenerate it from the game bundles you need `pip install UnityPy` (see
`tmp/extract_gamedata.py`).

