# Tasks

## Setup
- [ ] Tell Claude: game install path, UABEA path, Unity version, whether Python is installed
- [ ] `git init`, `.gitignore`, backup of current release folder + dumps
- [ ] Create `work/`, `tools/`, `docs/findings.md`, `docs/glossary.md`
- [ ] Set up Python + UnityPy for scripted bundle inspection (read-only first)

## Bug 1 — German skill names + loading screen
- [ ] Search bundles/resources.assets for "WIRD GELADEN", "LOGIK", "ENZYKLOPÄDIE"
- [ ] Identify where the skill names/descriptions on the character sheet come from
- [ ] Translate and re-import; verify in game

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
