# Plan

## Phase 0 — Project setup
- Get game install path, UABEA, Unity version used by the game (needed for fonts), Python.
- `git init` + `.gitignore` (or at least a `backups/` folder) so edits are reversible.
- Create `work/` (copies), `tools/` (scripts), `docs/findings.md`.
- Make a reproducible test loop: copy bundles into game → launch → screenshot.

## Phase 1 — Fix known bugs (investigation first)
1. **German in skills + loading screen.** Search all bundles and `resources.assets`/`sharedassets*` for strings "WIRD GELADEN", "ENZYKLOPÄDIE", "LOGIK" (UABE search / python UnityPy). Determine whether they're TextMeshPro text in scenes/prefabs, a separate localization asset, or baked into textures (loading screen likely image/Text in scene).
2. **Missing-glyph squares.** List every font asset (TMP SDF) in `fonts/` and the fonts referenced by the character sheet; find the ones lacking Cyrillic (the "Інтелект" label uses a different font); patch like the others (or add fallback font in TMP).
3. **Text overflow.** Find long strings in `GeneralLockit` (compare length UA vs original EN/DE), shorten them, or adjust autosize in affected elements.
4. **Image crash.** Bisect: replace images in batches, find the asset(s) that crash (size/format/mipmaps mismatch vs original).

## Phase 2 — Quality
- Review/improve machine translation (terminology glossary: skills, thoughts, names). Glossary in `docs/glossary.md`.
- Consider re-translating weak parts (DeepL / Claude) with glossary consistency.

## Phase 3 — Release
- Build script that produces the release folder, version/changelog, Nexus description.
