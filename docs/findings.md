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

## English source texts + glossary pipeline (2026-10-15)
- English GeneralLockit: `resources.assets` MonoBehaviour path_id 2996 (5476 terms, no typetree in file -> parsed with node layout borrowed from the Russian lockit bundle). `tools/dump_english_lockits.py` -> `work/glossary/en_GeneralLockit.json`.
- English dialogues: Pixel Crushers DialogueDatabase in `StreamingAssets/aa/StandaloneWindows64/dialoguebundle_assets_all_*.bundle` (MonoBehaviour 'Disco Elysium', 65 MB). Entry fields by `Articy Id` -> lockit term `<field>/<ArticyId>` (Dialogue Text, Alternate1-4, tooltip1-10). `tools/dump_english_dialogues.py` -> `work/glossary/en_DialoguesLockit.json` (72 893 strings; 72 771 of the 73 948 UA dialogue terms match).
- `tools/build_term_table.py` -> `work/glossary/terms.tsv` (791 canonical entities: actors, items, thoughts, area names, skills...) and `conflicts.json` (243 candidates where EN name occurs but UA canonical stem is missing in the UA line). Batches in `work/glossary/batches/b01-b12.json`; Haiku results go to `work/glossary/out/`.

## Glossary applied on copy (2026-10-15)
- Haiku verdicts merged: `docs/glossary.md`; detailed before/after: `docs/glossary_report.md`. Patched copy `work/patched/lockits/german_glossary` (176 terms changed, verified, NOT installed in game). Skill names/Eugene/Glen/Evrart/Scab etc. deliberately left for user decision.

## Distribution inventory (2026-10-15)
Game files changed by the mod (old = work/backup original, new = current game), bsdiff patch sizes:
| file (under disco_Data) | old -> new | diff |
|---|---|---|
| resources.assets | 3,444,764 -> 3,445,016 | bsdiff 660 B (skill labels) |
| level0 | 10,940 -> 10,940 | 2 bytes, bsdiff 154 B (splash font size) |
| level2 | 5,134,712 -> 5,134,712 | 3 bytes, bsdiff 168 B (INTELLECT label fix, other session) |
| il2cpp_data/Metadata/global-metadata.dat | 12,380,944 -> 12,380,968 | bsdiff 213 B (WIRD GELADEN literal) |
| StreamingAssets/AssetBundles/Windows/collage/shared | 68,180 -> 99,129 | bsdiff 88,740 B (translation + LZ4 repack) |
Plus drop-in bundles (own content, shipped as files): lockits/german, images/german, fonts/english.
=> An installer can ship tiny binary patches keyed by the SHA-256 of the original file; no game file is redistributed. bsdiff patches need `bz2` + ~40 lines pure-Python bspatch at install time (no UnityPy needed).
Platform plan: Windows Steam (tested here), Steam Deck/Linux = Proton uses the same Windows files, Mac native (user has a Mac to test; its files/bundles differ -> separate patch set from its originals), GOG / Xbox-app-on-Windows (Game Pass; install dir selectable, not necessarily WindowsApps) = verify hashes, add patch sets per version. Consoles impossible.

## macOS build (2026-10-15) — in progress
- User's Mac install (Steam): `~/Library/Application Support/Steam/steamapps/common/Disco Elysium/disco.app/Contents/Resources/Data/StreamingAssets/AssetBundles` (confirmed). Game dir has no `disco_Data`, so the installer's `data_dirs: ["disco_Data"]` never matches -> "Game not found". Tk (tkinter) aborts on macOS 26 with system/old Python ("macOS 26 (2603) or later required, have instead 16 (1603)"); `--cli` works.
- The Windows package cannot be reused as is: it bsdiff-patches `resources.assets`, `level0`, `level2`, `il2cpp_data/Metadata/global-metadata.dat`, `collage/shared` (platform-specific bytes, SHA-256 verified) and ships bundles under `AssetBundles/Windows/`.
- Next: user runs `python3 -I tools/mac_probe.py > mac_report.txt` on the Mac (read-only) to get the layout, scripting backend (IL2CPP vs Mono), hashes and Unity target platform of every file we touch. Then build a `macos-steam-final-cut` variant from Mac originals.
- 2026-10-15 RESULT: macOS build CONFIRMED WORKING in game by the user (Apple Silicon Mac, macOS 26, Steam). Method: `tools/build_mac_files.py --install` (re-patches Mac originals with the existing tools, takes the three bundles from the Windows package unchanged).
  - Windows-built bundles load fine from `AssetBundles/OSX/` -> no retargeting needed.
  - Mac object ids differ from Windows, so patches find objects by content: level0 splash text path_id 50 (Windows 49); level2 INT Localize path_id 25133 (Windows 25140, same PPtr (2, 9785)); metadata literal "WIRD GELADEN" is entry #13270 (Windows #14127). resources.assets skill labels: same path_ids 3005/3010.
  - Mac original SHA-256 (Steam, Unity 2020.3.12f1, IL2CPP, metadata v27): resources.assets e331daf5…a4f1 (3,468,436 B); level0 78cca762…7774 (11,188); level2 97818 6d0…41fc (5,132,160); global-metadata.dat 182882d0…43f5c (11,155,924); OSX/collage/shared 66b2cc08…5484 (68,176). Full report: user's mac_report.txt (from `tools/mac_probe.py`).
  - Not done yet: a `macos-steam-final-cut` variant in the installer (needs bsdiff patches from the Mac originals + `data_dirs` `disco.app/Contents/Resources/Data` + bundle folder `OSX`), tkinter fallback to `--cli` on macOS 26, README note. Intel Macs / older macOS untested.
- 2026-10-15 macOS installer CONFIRMED by the user on the Apple Silicon Mac (macOS 26.3, Steam): package built on Windows with the `macos-steam-final-cut` variant (`build_package.py` + `work/mac_build`), installed from the python zip with the system Python. Tk guard: `platform.mac_ver()` reports 26.3 (NOT 16), so the guard keys on Apple's Python (path contains /Xcode.app/ or /CommandLineTools/) + macOS >= 26. Mac patch sizes: resources.assets 663 B, level0 154, level2 166, metadata 215, collage/shared 88,738.
- Release flow for Mac: on the Mac `build_mac_files.py --install` (once, to get originals + files) -> zip work/mac_build -> unpack into work/mac_build on Windows -> `build_package.py`. Redo when the game updates (hashes change).
