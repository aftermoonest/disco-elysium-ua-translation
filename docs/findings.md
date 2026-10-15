# Findings


# Findings

## Environment
- Game Unity version: 2020.3.12f1. Game: `D:\Games\SteamLibrary\steamapps\common\Disco Elysium\disco_Data`
- Originals of AssetBundles copied (no manifests) to `work/original/AssetBundles` (gitignored).
- Tools in `tools/` (all read-only): grep_game.py, grep_bundles.py, inspect_resources.py, dump_obj.py, list_tex.py, list_charsheet.py. Run with `python -I`.

## Bug: skill names on character sheet in German (2026-10-15)
- Grid tile labels are NOT in the lockits. They live in `resources.assets` as MonoBehaviour `CharsheetSkillLabelsGerman` (path_id 3005, 1436 bytes): 24 strings (LOGIK, ENZYKLOPÄDIE, ...) + per-label float layout data. Sibling objects exist for every language (English 2997/3003, Russian 3010, Spanish 3011, ...).
- Right-hand panel title ("ЕНЦИКЛОПЕДІЯ") comes from the lockit and is already translated.
- Fix options: (a) patch resources.assets (ships a modified 3.4 MB game file; strings must fit the serialized layout, UnityPy typetree read failed → edit raw bytes/ rebuild with care); (b) check whether the game can load these labels some other way. TODO: decide.
- Note: Russian label object (3010) is 1672 bytes — longer strings; compare its layout for Cyrillic sizing.

## Bug: loading screen "WIRD GELADEN"
- Not text in any game file/bundle (raw UTF-8/UTF-16 search negative). It's baked into texture `loading-panel-de` in `images/german` (also `button-load-de`). Needs repainting in the mod's images bundle. TODO: check whether the mod's bundle still has the original texture.

## Bug: squares under the big "5" on the character sheet
- 8 squares = 8 letters = "ІНТЕЛЕКТ" (hypothesis): that text uses a font lacking Cyrillic. TODO: find the TMP object/font used.
