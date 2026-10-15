# Disco Elysium — Ukrainian translation: installer

This installer adds the Ukrainian translation to Disco Elysium — The Final Cut. The translation **replaces the German
language slot** of the game, so after installing you must choose **Deutsch** in the game's language settings.

The installer:
- checks that your game version is supported (by file checksums);
- saves the original files to a `_ua_backup` folder inside the game folder;
- changes only the files it needs (small patches + translation bundles);
- can completely **remove** the translation and restore the game;
- updates by simply running a newer installer.

## Supported platforms

| Platform | Status |
|---|---|
| Windows, Steam | tested |
| Steam Deck / Linux (Steam, Proton) | expected to work (same files as Windows), feedback welcome |
| Windows, GOG / Xbox app (Game Pass) / Epic | the installer checks the version and tells you; see "Another game version" |
| macOS, Steam (Apple Silicon, macOS 26) | files verified in the game; the Mac installer itself is still being tested. Intel Macs and older macOS were not tested |
| Consoles (Xbox, PlayStation, Switch) | not possible |

## Installing

### Windows
1. Unzip the archive somewhere (do **not** run it from inside the zip). The `package` folder must stay next to the `.exe`.
2. Close the game. Run `DiscoElysium_UA_installer.exe`.
3. If Windows shows "Windows protected your PC" (SmartScreen): click "More info" → "Run anyway".
   The program is not code-signed. Its code is a plain Python script (`installer.py`) that you can read.
4. Click **Find game** (or **Browse…** if it is not found), then **Install / update**.

### Steam Deck
1. Switch to Desktop Mode (Steam → Power → Switch to Desktop).
2. Download and unzip the "python" archive, open the folder in Dolphin, then "Open Terminal Here".
3. Run `python3 installer.py` (a window opens) or `python3 installer.py --cli install`.
   On Deck the game runs through Proton, so the files are the same as on Windows.

### Linux
Same as Steam Deck: run `python3 installer.py` in the unzipped folder.
If the window does not open (no `python3-tk`), use text mode: `python3 installer.py --cli install`.

### macOS
1. Open Terminal in the unzipped folder and run `python3 installer.py`
   On macOS 26 the Tk window of the system Python aborts ("macOS 26 (2603) or later required"). The installer detects this
   and switches to text mode by itself: just confirm the installation with `y`.
   To remove the translation: `python3 installer.py --cli remove`.
2. If macOS blocks the file: `xattr -d com.apple.quarantine installer.py`.
3. The Steam version is supported (`~/Library/Application Support/Steam/steamapps/common/Disco Elysium`). The game must not be running.
   If the installer says "Unknown game version", see below.

## After installing
Start the game and choose **Deutsch** in the language settings. All text will be in Ukrainian.

## Removing
Run the installer and click **Remove (restore original)**. The backups are put back and the `_ua_backup` folder disappears.

## Updating
Run the new installer and click **Install / update**. The backups of the originals stay the same.

## Text mode
```
python3 installer.py --cli info            show what was found
python3 installer.py --cli install         install (asks first; --yes skips the question)
python3 installer.py --cli remove          remove
python3 installer.py --cli install --dry-run   change nothing, only show the steps
python3 installer.py --cli collect-info    checksums of the game files (for a report)
python3 installer.py --game "PATH" ...     point to the game folder manually
python3 installer.py --lang uk             Ukrainian interface
```
On Windows use `DiscoElysium_UA_installer.exe` instead of `python3 installer.py`.

## Troubleshooting

**"Unknown game version"**: the game files do not match any known version. Nothing was changed. What to do:
1. In Steam: Disco Elysium → Properties → Installed files → **Verify integrity of game files**, then run the installer again.
2. If the game is from another store (GOG, Xbox, Epic) or macOS: run `--cli collect-info` and send the output to the author
   so your version can be added.

**"The game files already contain the translation, but there is no installer backup"**: the translation was installed by hand.
Verify the game files in Steam (see above), then install through the installer.

**"The game is running"**: close Disco Elysium.

**Steam updated the game or "verified files"**: the translation may be gone. Install it again.

**Squares or German text**: make sure Deutsch is chosen in the game settings, and report where exactly you see it (a screenshot helps).

## For developers
The package is the `installer.py` script plus a `package/` folder (`manifest.json`, `patches/*.bsdiff`, `data/`). The installer
needs no third-party libraries (Python 3.8+ only). Modified game files are not redistributed: the package holds only
binary diffs (bsdiff) against the originals, verified by SHA-256.
