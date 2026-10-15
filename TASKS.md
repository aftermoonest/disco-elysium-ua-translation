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
- [ ] Translate German column of CollageModeLockit (248 terms: achievements, actors, buttons, loading...; dump: work/export/collage_lockit.tsv), write back into collage/shared, test
- [ ] Fix `loading-panel-de` texture: it says "ЗБЕРЕЖЕННЯ" (Saving) — should be "ЗАВАНТАЖЕННЯ"; same text as saving-panel-de

## Bug 2 — Squares (missing glyphs)
- [ ] List all font assets in `fonts/english` and which are used where
- [ ] Find the font of "Інтелект" label (and others) lacking Cyrillic
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
- [ ] Release build script + Nexus changelog

