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

## Squares under the big "5" (INTELLECT label) — hypothesis + prepared patch (2026-10-15)
- Fonts are chosen via `FontsLockit<Lang>` (term type 9: font term -> font asset name per language). Mod's `FontsLockitGerman` maps Dobra-Book SDF etc. to the Cyrillic-extended fonts in `fonts/english`. All those have full Ukrainian coverage, EXCEPT `CoreSansES Light SDF` (mapped from "GulimChe SDF"): it lacks Є І Ї є і ї Ґ ґ (still TODO to fix). `OpenDyslexic3-*` have no Cyrillic at all (only matters in dyslexic mode).
- Labels PSY/MOT/INT in `level2` use TMP base font LiberationSans + I2 Localize secondary term "Dobra-Book SDF". Only the INT Localize component (MonoBehaviour 25140) additionally holds a direct PPtr (fileID 2, pathID 9785 = base `Dobra-Book SDF` in sharedassets1, no Cyrillic) at offset 0x8C; PSY (26594) has it null → renders fine.
- Prepared: `tools/patch_int_label.py` → `work/patched/level2` (same size, only that PPtr zeroed). NOT yet tested in game; backup of level2 still to be made before install.
- Other possibly similar cases (empty term, secondary SinaNova-*, PPtr to #399/#400): level2 25266, 27202; sharedassets2 3272, 3310, 3326, 3350. Not investigated.
- I2 images lockit maps `LOAD_SCREEN_PANEL_IMG` -> sprite `loading-panel-<lang>`.

## Collage lockit translated (2026-10-15) — NOT installed in game
- Translations: `tools/collage_translations.py` (data + generator) → `work/collage_ua.json` (231 terms; only terms with a non-empty German value; headers untouched). Glossary used: Ревашоль, Мартінез, Еврарт, Куно, Головомір, «Танці в лахмітті», Фріссель, Сюзеренітет, комунари; formal "ви".
- Patch: `tools/patch_collage_lockit.py work/original/AssetBundles/collage/shared work/collage_ua.json work/patched/collage/shared` (UnityPy typetree edit, LZ4 repack, 68 KB → 99 KB). Verify: `tools/verify_collage_patch.py <orig> <patched>` — other objects byte-identical, other language columns unchanged, 0 placeholder/tag problems.
- game's `collage/shared` == `work/original/AssetBundles/collage/shared` (sha256 equal) → it is the untouched original; restore = just re-copy it.
- Not yet checked in game: (1) whether Collage UI fonts have Cyrillic glyphs (risk: squares!), (2) text fit in tabs/tooltips (abbreviated "Вел./Жирн./Серед./Мал./Тонк.", "Віз. аналіз № {0}"), (3) `<i>` tags in HIDDEN texts render.
- Review points in the translation: "Fuck the World" → "На хер цей світ" (kept vulgar like the source), "Lily Livered"/"Pale-Aged"/"Off Breeze"/"Ace's High" are guesses (names of photo filters/fragments).

- 2026-10-15: patched level2 (INT label PPtr zeroed) CONFIRMED in game: 'ІНТЕЛЕКТ' renders. Mod must ship patched level2 + resources.assets (game files, not bundles). Backups in work/backup.

## CoreSansES Light SDF usage (2026-10-15)
- Font term "GulimChe SDF" -> CoreSansES Light SDF. Used ONLY by HUD labels in level2/sharedassets1: HUD_DAY, HUD_JOURNAL/CHARSHEET/INVENTORY/CABINET_ABBREVIATION, Buttons/PAWNSHOP_BUTTON_CLOSE_TEXT.
- Only missing glyph needed by current text: І (in "ІНВ", HUD_INVENTORY_ABBREVIATION). Є/Ґ are not used by any of these terms, so not added.
- Fix: alias U+0406/0456/0407/0457 to Latin I/i/Ï/ï glyphs in the character table (visually identical; no atlas change). `tools/patch_coresans.py` -> `work/patched/fonts/english` (+64 bytes). NOT yet tested in game.
- Pawnshop close text 'ЗАКРИТИ ▼?' (Russian original also has '▼?') — ▼ not in this font; check in game how it renders.
- HUD_CHARSHEET_ABBREVIATION "ПЕРСОНАЖ" wraps ("ПЕРСО/НАЖ") in the bottom bar (overflow, Bug 3).

## SECOND CORRECTION: "WIRD GELADEN" is a texture after all (2026-10-15)
- Installing the patched `collage/shared` (Collage/BUTTON/LOADING = "Завантаження") did NOT change the splash. Player.log: game starts clean, StartupLanguage = German; no errors.
- Whole-tree search (data files, Managed, exe, StreamingAssets/aa, all bundles via UnityPy) finds "geladen" ONLY in collage/shared. But `images_dyslexic/german` has Texture2D `loading-panel-de` (268x39, path_id 5781628726658703548) and Sprite 3036182261067988640 with the baked white text "WIRD GELADEN" (+ fade block on the right where the spinner sits) — it matches the screenshot. Likewise `saving-panel-de` (262x39, Texture 136298903547947466 negated sign: -136298903547947466) there.
- Settings.json has dyslexicFont=false, yet the startup splash evidently uses the dyslexic image set (or settings not read yet at that point). The mod never touched `images_dyslexic/` — all ~55 textures there are still German originals (buttons, labels...) and show if the dyslexic option is on.
- `images/german` (mod): both loading-panel-de and saving-panel-de read "ЗБЕРЕЖЕННЯ" (loading one should be "ЗАВАНТАЖЕННЯ").
- Collage lockit translation is still valid/needed for Collage mode, independent of this.
- Player.log lives in `%USERPROFILE%\AppData\LocalLow\ZAUM Studio\Disco Elysium\Player.log` (+ Player-prev.log). Do not Read whole file (huge output) — grep it.

## Short technical labels (2026-10-15)
- `tools/patch_short_labels.py` -> `work/patched/lockits/german` (copy; NOT in game, release folder untouched). GeneralLockit changes: ABILITY_SHORT_INT 'Введення'->'Інт' (mistranslation of "Input"), HUD_JOURNAL 'ЖУР', HUD_CHARSHEET 'ПЕР', HUD_CABINET 'ШМ'->'ДУМ', ABILITY_BUTTON_RANDOM 'ВИПАДКОВО'. HUD_INVENTORY stays 'ІНВ'.
- Also not yet shortened (candidates): ЗАВАНТАЖИТИ, НАЛАШТУВАННЯ, ПІДВИЩЕННЯ РІВНЯ, СКАСУВАТИ. The JSON dumps in "Disco Elysium ukr dumb" were not updated.

## Repainted loading/saving panels for images_dyslexic/german (2026-10-15) — NOT installed in game
- `tools/make_loading_panels.py <orig images_dyslexic/german> <out> [preview dir]` repaints Texture2D `loading-panel-de` (268x39) -> "ЗАВАНТАЖЕННЯ" and `saving-panel-de` (262x39) -> "ЗБЕРЕЖЕННЯ". Output: `work/patched/images_dyslexic/german` (LZ4). Previews: `work/export/loading/dys_*_{old,new}.png`.
- Texture format: white RGB, alpha carries the image (text alpha ~24-26, right-hand spinner block alpha ~68). Block left edge x=163 (saving) / 169 (loading), read from row y=8. Old text overlapped the block in saving panel; cleaned by copying clean row 30.
- Font = Segoe UI Regular (system) — test only; replace with an OFL font (e.g. Noto Sans) before release. Original look was a heavier sans; ours is lighter — judge in game.
- Only the 2 Texture2D changed; Sprites untouched (they only reference the texture rect).
- TODO: same text bug in mod's `images/german` (both panels say "ЗБЕРЕЖЕННЯ"), plus all other textures in `images_dyslexic/german` are German (only matter if dyslexic option on).

## FINAL ANSWER: where "WIRD GELADEN" lives (2026-10-15)
- It is a hard-coded C# string literal compiled into the IL2CPP metadata: `disco_Data/il2cpp_data/Metadata/global-metadata.dat` (version 27), literal-table entry #14127, bytes at file offset 630745. Next to it sit the other languages' constants ("CARGANDO", "CARREGANDO", "CHARGEMENT", ...). Level0 has a TMP text "LOADING" (GO "RotationLoading") that code swaps per language. That is why no asset/bundle/lockit search ever found it; the Splash texture (sharedassets0 `Splash`, 1920x1080) is only the painting.
- The images_dyslexic loading/saving panel I repainted is the small in-game autosave/load indicator, NOT the startup splash. The user disliked it -> images_dyslexic/german was RESTORED in the game from work/backup (hash == original). `work/patched/images_dyslexic/german` is obsolete (do not ship). Collage/shared patch (Collage/BUTTON/LOADING) is still installed in the game; unrelated to the splash.
- Patch tool: `tools/patch_metadata_literal.py <src> <out> "WIRD GELADEN" "ЗАВАНТАЖЕННЯ"` appends the new UTF-8 text (24 B > 12 B old) at end of file and repoints the table entry (len, dataIndex). Only 4 bytes inside the original file change. Output: `work/patched/global-metadata.dat` (not installed). Risk: this is a game file (12 MB), breaks on game updates; font of that TMP text may lack Cyrillic (squares) -> test.
- Other hard-coded German literals may exist in the same metadata (UI strings in code). TODO: scan literals near "WIRD GELADEN" / list all German-looking literals.
- Player.log: grep only, never Read (very long).

## Splash fix confirmed in game + font size (2026-10-15)
- Patched `global-metadata.dat` literal works: startup screen shows "ЗАВАНТАЖЕННЯ" (Cyrillic glyphs OK). Installed in game; backup `work/backup/metadata/global-metadata.dat`.
- User wants it smaller (text takes ~half the screen at size 110). TMP text "LOADING" is MonoBehaviour path_id 49 in `level0` (GameObject "Text" under the loading UI): fontSize @+0x124 and fontSizeBase @+0x128 (floats, 110.0). `tools/patch_splash_fontsize.py <level0> <out> <size>` -> `work/patched/level0` (size 80; only 2 bytes differ). Other scenes (level1/2/3/35, sharedassets*) also contain a "LOADING" string — in-game area loading screens may use their own texts/sizes; unchecked.
