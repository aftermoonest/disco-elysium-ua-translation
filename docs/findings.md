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

## Correction: game folder already contains the mod
- `lockits/german` in the game dir has Ukrainian text (verified via UnityPy). `work/original/AssetBundles/*/german` are therefore the installed MOD, not originals. Real originals = other languages (russian/english...).
- Lockit terms are a list `mSource.mTerms[]` with `Term` and `Languages[0]`; skill names are `Actors/<id>/Name`. Bundles also contain `ImagesLockit<Lang>`.

## CharsheetSkillLabels* binary format (resources.assets, MonoBehaviour w/o typetree)
header 28 bytes (GameObject PPtr, enabled, Script PPtr), name string (len + 4-aligned), int count, then per entry:
int id, int len, UTF-8 text (4-aligned), 9 floats: [fontSize, 0, -31.7, 0, 0, xOffset, yOffset, width, height]. ids 1..29 = skills.
Parser/builder: `tools/patch_skill_labels.py`. Patched COPY: `work/patched/resources.assets` (+252 bytes, re-parses OK, not yet tested in game).
Font sizes are a crude heuristic (Russian layout, shrunk by length ratio, min 12) — tune after in-game test (e.g. "Тремтіння" got 12).
Deployment note: mod would have to ship a modified `resources.assets` (3.4 MB game file) — breaks on game updates; Nexus install instructions need updating.

- 2026-10-15: patched resources.assets confirmed working in game (all 24 names Ukrainian). Small sizes remain on a few labels; user says it works.

## CORRECTION: "WIRD GELADEN" (2026-10-15)
- Earlier claim "it is a texture" was WRONG. It is the German column of `Collage/BUTTON/LOADING` ("Wird geladen") in MonoBehaviour `CollageModeLockit` inside `collage/shared` (game's AssetBundles/Windows/collage/shared). Languages list order: en, zh-CN, zh-TW, es, pt-BR, fr, de(idx 6), ko, ru, pl, ja, tr, ar. 248 terms, all other German values are still German too (whole Collage mode untranslated).
- My first lockit grep missed it because `lockits/german` is already the Ukrainian mod, and the term lives in a different bundle.
- Separate bug: textures `loading-panel-de` and `saving-panel-de` (346x39, images/german) BOTH read "ЗБЕРЕЖЕННЯ"; loading one should be "ЗАВАНТАЖЕННЯ". Russian/English counterparts are white-on-transparent.
- `resources.assets` MonoBehaviours 2996 (term Buttons/LOAD_SCREEN_PANEL_SAVING_TEXT) and 2998 (LOAD_SCREEN_PANEL_IMG -> sprite "loading-panel") are the built-in default lockit/images source.
- Exports: `work/export/loading/*.png` (+ `_preview.png` on dark bg), `work/export/collage_lockit.tsv`. Tools: export_texture.py, find_terms.py, probe_loading.py, dump_collage_lockit.py.
