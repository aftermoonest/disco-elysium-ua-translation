# Disco Elysium — Ukrainian translation (Nexus Mods mod)

Ukrainian localization of Disco Elysium: The Final Cut. The mod **replaces the German language** (so Russian isn't needed in Steam). Everything the player sees as "German" is really Ukrainian text/fonts/images.

User communicates in Ukrainian; reply in Ukrainian unless asked otherwise. Code, file names and comments in English.

## Layout
- `Disco Elysium  Ukrainian translation/` (note the DOUBLE space) — the release build, as published on Nexus. Mirrors the game's `disco_Data\StreamingAssets\AssetBundles\Windows\`:
  - `fonts/english` — Unity asset bundle with patched fonts (Noto Sans + Minion Pro, as in the Russian localization)
  - `images/german` — bundle with replaced UI images (buttons, labels)
  - `lockits/german` — bundle with `DialoguesLockit` + `GeneralLockit` (all text)
- `Disco Elysium ukr dumb/` — UABE JSON dumps of the lockits (50 MB+ each; never read whole, use grep/streaming):
  - `ua-dialogies-de.json` (dialogues), `ua-general-de*.json` (technical/UI text), `output ... бекап.json` (backups)
- `Знімок екрана ...png` — screenshots of known bugs.
- Game install: `D:\Games\SteamLibrary\steamapps\common\Disco Elysium` (Steam). Its `lockits/german` (2.7 MB, compressed) and `images/german` are the MOD itself, installed in compressed form (verified: its GeneralLockit contains Ukrainian). So NO original German exists in the game; use other languages (e.g. lockits/russian, images/russian) as originals/layout references. The release-folder bundles are the uncompressed (16 MB / 28 MB) variants. No `lockits/english` exists (English is built into resources). Extra folders: `images_dyslexic/`, `shared/content.bundle`, `collage/`.
- Tooling installed 2026-10-15: Git 2.55, Python 3.12, UnityPy 1.25.4 (open a new terminal or refresh PATH if `git`/`python` are not found).

## Workflow (from the user's guide, Notion "Disco Elysium tips")
1. Bundles live in `<game>\disco_Data\StreamingAssets\AssetBundles\Windows\{lockits,fonts,images,collage}`. Use bundle files, not `.manifest`.
2. Open/extract/import with **UABEA** (github.com/nesrak1/UABEA). Dump `DialoguesLockit` and `GeneralLockit` as JSON, edit, import back.
3. Fonts: replacing needs Unity (TextMeshPro SDF font assets). Guide: steamcommunity.com/sharedfiles/filedetails/?id=3023518241
4. Images: recreated as components in Figma ("Disco Elysium Images"); `collage/` bundle holds Collage mode labels.
5. Text was machine translated (GPT-4o via API, RU→UK, line by line with a Python script) then hand-fixed. DeepL may be better.
6. Reference: ukrainizer.netlify.app

## Known bugs (see TASKS.md)
1. Some fonts lack Cyrillic → squares (e.g. "Інтелект" label on the character sheet).
2. Skill names on character sheet (LOGIK, ENZYKLOPÄDIE…) and the loading screen ("WIRD GELADEN") still show German. Location unknown; suspected `resources.assets` / other bundles / scenes, not the lockits.
3. Some text overflows its box.
4. Replacing ALL image assets once crashed the game — suspect wrong asset mapping/IDs.

## Rules for Claude
- NEVER modify files in the release folder or dumps in place; work on copies in `work/` and keep backups. These are binary bundles and huge JSONs; git tracks only the docs/tools (not the big binaries).
- Never load a whole dump into context; use grep with `head_limit`, or Python scripts that stream/parse.
- Put scratch scripts in `tools/`, not in the release folder.
- Don't touch the user's game install without explicit confirmation; prefer testing against a copy.
- Record every finding (asset names, path IDs, keys) in `docs/findings.md` so it survives between sessions.
- Plan: `PLAN.md`. Tasks: `TASKS.md`.



