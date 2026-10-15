# Tasks

## Setup
- [x] Game install path, Unity version (2020.3.12f1), Python 3.12
- [ ] UABEA path (user installed it; path not yet recorded)
- [x] `git init`, `.gitignore` (git tracks docs/tools only)
- [ ] Backup of release folder + dumps outside the repo
- [x] Create `work/`, `tools/`, `docs/findings.md`, `docs/glossary.md`
- [x] Python + UnityPy for scripted bundle inspection

## Bug 1 — German skill names + loading screen
- [x] "WIRD GELADEN" is TEXT (not a texture): term `Collage/BUTTON/LOADING`, German column of `CollageModeLockit` in `collage/shared` bundle (68 KB). The mod never touched this bundle.
- [x] Skill names found: resources.assets CharsheetSkillLabelsGerman (id 3005)
- [x] Patched via tools/patch_skill_labels.py, verified in game 2026-10-15 (backup in work/backup)
- [ ] Tune small font sizes (Тремтіння, Навіювання, Самовладання, Електрохімія, Координація)
- [ ] Decide how to ship resources.assets with the mod (Nexus instructions)
- [x] Translate German column of CollageModeLockit (231 terms) -> work/collage_ua.json; patched copy work/patched/collage/shared (NOT in game yet)
- [ ] Test collage/shared in game (installed 2026-10-15; it did NOT fix the splash text; Collage UI itself still untested)
- [ ] REAL source of "WIRD GELADEN": Texture2D `loading-panel-de` (268x39, path_id 5781628726658703548) in `images_dyslexic/german` (original German, mod never touched images_dyslexic). Repaint to "ЗАВАНТАЖЕННЯ"; also saving-panel-de there
- [x] (obsolete) repainted dyslexic panels - wrong target, restored in game
- [x] DONE 2026-10-15: splash "ЗАВАНТАЖЕННЯ" via global-metadata.dat literal (installed, verified) + font size 80 via level0 (installed; backups work/backup/metadata, work/backup/level)
- [ ] Fix `loading-panel-de` texture: it says "ЗБЕРЕЖЕННЯ" (Saving) — should be "ЗАВАНТАЖЕННЯ"; same text as saving-panel-de

## Bug 2 — Squares (missing glyphs)
- [ ] List all font assets in `fonts/english` and which are used where
- [x] INTELLECT label squares fixed: level2 Localize PPtr override zeroed (tools/patch_int_label.py), verified in game
- [ ] CoreSansES Light SDF lacks Є І Ї Ґ (mapped from 'GulimChe SDF') — find where it's used
- [ ] Check similar PPtr overrides: level2 25266/27202, sharedassets2 3272/3310/3326/3350
- [ ] Rebuild SDF atlas with Cyrillic; replace; verify

## Bug 3 — Text overflow
- [ ] Script: compare length of UA vs source strings, list worst offenders
- [ ] Collect in-game screenshots of overflowing places
- [ ] Shorten strings / tweak layout

## Bug 4 — Images
- [ ] Compare replaced images vs originals (size, format, mips)
- [ ] Bisect crash cause; document in findings.md
- [ ] Re-add remaining image translations

## Later
- [ ] Translation quality pass + glossary
- [ ] Collage mode labels (`collage/` bundle) check
- [x] Installer prototype (installer/installer.py + tools/build_package.py + tools/test_installer.py), 22 tests pass on a test copy
- [x] Installer: GUI checked by user on Windows+Steam (works); README UK/EN; PyInstaller exe (tested via 22 checks); GitHub Actions workflow written (not run)
- [ ] Installer: Mac test (user has a Mac), Mac patch set, GOG/Xbox hashes, signing/SmartScreen note, publish repo + Releases
- [ ] Release build script + Nexus changelog


