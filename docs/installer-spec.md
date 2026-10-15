# Installer spec (decisions 2026-10-15)

- Goal: one installer for all PC versions: Windows (Steam, GOG, Xbox app/Game Pass with selectable install dir), Steam Deck / Linux (Proton = same Windows files), Mac native (user will test on their Mac; Mac needs its own patch set built from Mac originals). Consoles: impossible.
- UI: small tkinter window (detected path, Install / Remove buttons, log) + text mode (`--cli`, automatic fallback when no display). Pure Python, no UnityPy at install time.
- UI languages: Ukrainian (default) + English, by system locale with a switch.
- Game detection: Steam libraries (Win/Mac/Linux/Deck SD card), GOG default dirs, `XboxGames\Disco Elysium\Content`, manual "Browse".
- Install = restore originals from `_ua_backup/` first, then apply -> running a newer installer on top of an older install just works (update = run the new version). No auto-update. Optional button only opens the Nexus page.
- Safety: SHA-256 check of every file to patch against a table of known original versions; unknown version -> stop and show hashes (+ "collect info" mode so users can report them); refuse while the game runs; atomic writes (temp + rename); `--dry-run`; manifest with mod version in `_ua_backup/`; Remove restores originals.
- Patches: bsdiff (bz2) deltas per file per platform/version, applied by a ~40-line pure-Python bspatch. Our own bundles (lockits/german, images/german, fonts/english, collage/shared) ship as data files (recompressed LZ4/LZMA to ~10-15 MB total), not as deltas where they are our content.
- Setting the game language to German: NOT automated (user decision). README tells players to choose Deutsch in the game settings.
- Distribution: GitHub repo = installer code + patch definitions + translation source (translation/*.tsv); builds (.exe / macOS / Linux, zip with data pack) as GitHub Release assets; Nexus mirrors the zip. Known caveats: unsigned exe -> SmartScreen; macOS Gatekeeper -> document `python3 installer.py` or `xattr -d com.apple.quarantine`.

## Source of truth (as of 2026-10-15)
- `translation/general.tsv` (8,585 terms) and `translation/dialogues.tsv` (74,029 terms): exported from the game's current `lockits/german` (user's latest edits live ONLY there; they changed 250+703 terms and added 322+81 vs the old dumps).
- Full binary snapshot of the modded game files: `work/snapshot/2026-10-15/` (+ manifest.json with SHA-256), not in git.
- Old dumps `Disco Elysium ukr dumb/*.json` and release folder bundles are OUTDATED (14:05-14:07) — do not build from them.

## Prototype status (2026-10-15)
- `installer/installer.py` — single-file installer (stdlib only): GUI (tkinter, UA/EN) + `--cli install|remove|info|collect-info`, `--dry-run`, `--yes`, `--game`, `--lang`. Pure-Python bspatch. Steam/GOG/Xbox/Epic/Deck/Mac path detection written, only Windows+Steam exercised.
- `tools/build_package.py` — builds `dist/DiscoElysium_UA_installer/` + `dist/..._v<ver>.zip` from `work/snapshot/<date>` (originals from `work/backup`), re-verifies every patch with the installer's own bspatch. Package 39 MB, zip (LZMA) 11 MB. `dist/` is git-ignored.
- `tools/test_installer.py` — 22 end-to-end checks on a throw-away copy (`work/testgame/`): dry-run, install, byte-exact backups, re-install/update, remove restores byte-for-byte, unknown version refused (nothing changed), hand-installed/no-backup case explained, wrong folder, collect-info, no *.ua_tmp left, GUI smoke test. ALL PASSED. The real game folder was never written.
- Known gaps: only the Windows/Steam variant exists (Mac/GOG/Xbox variants need their originals); GUI not yet looked at by a human; PyInstaller exe + GitHub Actions + README not done; process check for macOS not implemented; installer refuses on a game already hand-modded without backup (user must "Verify files" in Steam first).

## Packaging status (2026-10-15, later)
- `installer/README.uk.md` + `README.en.md` written (included in packages).
- `tools/build_package.py [--dist DIR] [--exe path]` now makes two archives: `..._python.zip` (installer.py + READMEs + package; Mac / Linux / Steam Deck / any Python 3) 11 MB, and `..._windows.zip` (PyInstaller .exe 10.6 MB + READMEs + package) 21.4 MB. In a frozen exe the `package/` folder is looked up NEXT to the exe.
- Windowed exe: stdout is None -> `_attach_console()` reuses redirected handles (pipes) or attaches to the parent console, so `--cli` works from cmd/PowerShell and from scripts.
- All 22 e2e checks pass for installer.py (dist/) AND for the unzipped windows.zip exe (`UA_DIST=dist_next UA_EXE=... UA_TESTGAME=testgame_exe python tools/test_installer.py`).
- GitHub Actions workflow (CI binaries for macOS/Linux) was written and then REMOVED on 2026-10-15 (not needed for now; it is in git history, commit b75b6b3). Mac / Linux / Deck use the `python` zip (`python3 installer.py`). Revisit only if testers find the script inconvenient.
- Not verified anywhere but Windows+Steam: Mac, Linux/Deck, GOG, Xbox app. Hashes/patch sets for them are still missing.
- Version naming: current release is **1.0** (manifest mod_version "1.0", archives ..._v1.0_*.zip). Tests: installer.py and the unzipped .exe both ALL PASSED.
- Archives use plain Deflate (NOT LZMA): Windows Explorer cannot extract LZMA zips (error 0x80004005). Sizes now: python zip 14.2 MB, windows zip 24.5 MB. Verified with .NET ZipFile/Expand-Archive.
- GitHub repo published 2026-10-15: https://github.com/aftermoonest/disco-elysium-ua-translation (public, branch master). Code/docs only; translation/*.tsv, game files and zips are NOT in it. No Release created yet.
