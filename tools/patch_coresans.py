"""Patched COPY of fonts/english where 'CoreSansES Light SDF' also maps Ukrainian І/і/Ї/ї to the
visually identical Latin I/i and Ï/ï glyphs (character-table aliases, same glyph index; no atlas change).
Used only for HUD abbreviations (e.g. "ІНВ"). Є/Ґ have no Latin look-alike and are not added.

Usage: python -I tools/patch_coresans.py <fonts/english in> <out>
"""
import sys
from pathlib import Path

import UnityPy

ALIASES = {0x0406: 0x49, 0x0456: 0x69, 0x0407: 0xCF, 0x0457: 0xEF}  # new unicode -> existing unicode

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
env = UnityPy.load(str(src))
for obj in env.objects:
    if obj.type.name != "MonoBehaviour":
        continue
    tt = obj.read_typetree()
    if tt.get("m_Name") != "CoreSansES Light SDF":
        continue
    table = tt["m_CharacterTable"]
    by_unicode = {c["m_Unicode"]: c for c in table}
    for new, old in ALIASES.items():
        if new in by_unicode:
            continue
        entry = dict(by_unicode[old])
        entry["m_Unicode"] = new
        table.append(entry)
        print(f"U+{new:04X} -> glyph {entry['m_GlyphIndex']} (as U+{old:04X})")
    obj.save_typetree(tt)
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_bytes(env.file.save())
print("written", dst, dst.stat().st_size, "(source", src.stat().st_size, ")")
