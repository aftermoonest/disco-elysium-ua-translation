"""Shorten technical/HUD labels in GeneralLockit of a COPY of lockits/german.

Usage: python -I tools/patch_short_labels.py <source lockits/german> <out lockits/german>
"""
import sys
from pathlib import Path
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")

CHANGES = {
    "Abilities/ABILITY_SHORT_INT": "Інт",      # was 'Введення' (mistranslation of "Input")
    "HUD_JOURNAL_ABBREVIATION": "ЖУР",         # was ЖУРНАЛ (wrapped)
    "HUD_CHARSHEET_ABBREVIATION": "ПЕР",       # was ПЕРСОНАЖ (wrapped)
    "HUD_CABINET_ABBREVIATION": "ДУМ",         # was ШМ (unclear, Russian 'шкаф мыслей')
    "Buttons/ABILITY_BUTTON_RANDOM_TEXT": "ВИПАДКОВО",  # was ВИПАДКОВИЙ ВИБІР
}

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
env = UnityPy.load(str(src))
for o in env.objects:
    if o.type.name == "MonoBehaviour" and o.read().m_Name.startswith("GeneralLockit"):
        tt = o.read_typetree()
        n = 0
        for t in tt["mSource"]["mTerms"]:
            if t["Term"] in CHANGES:
                print(t["Term"], repr(t["Languages"][0]), "->", CHANGES[t["Term"]])
                t["Languages"][0] = CHANGES[t["Term"]]
                n += 1
        assert n == len(CHANGES), n
        o.save_typetree(tt)
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_bytes(env.file.save(packer="lz4"))
print("written", dst, dst.stat().st_size)
