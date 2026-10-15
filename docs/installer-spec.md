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
