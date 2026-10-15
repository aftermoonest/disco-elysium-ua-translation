"""Build a patched COPY of resources.assets where CharsheetSkillLabelsGerman holds Ukrainian names.

Usage: python -I tools/patch_skill_labels.py <game resources.assets> <out resources.assets>

Source text: Ukrainian GeneralLockit (the mod's lockits/german) via Actor term ids, matched through the
Russian label object (CharsheetSkillLabelsRussian, 3010). Layout floats (font size, rect) are taken from the
Russian entry (designed for Cyrillic), font size is reduced if the Ukrainian line is longer.
Never writes to the game folder.
"""
import re
import struct
import sys
from pathlib import Path

import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
GERMAN_ID, RUSSIAN_ID = 3005, 3010

# Manual line breaks for single-word names that Russian splits over two lines.
BREAKS = {"Концептуалізація": "Концептуа-\nлізація", "Еквілібристика": "Еквілі-\nбристика"}


def parse(raw):
    p = 28
    n = struct.unpack_from("<i", raw, p)[0]
    p += 4
    head_end = p + (n + 3) // 4 * 4
    p = head_end
    count = struct.unpack_from("<i", raw, p)[0]
    p += 4
    entries = []
    for _ in range(count):
        eid, ln = struct.unpack_from("<ii", raw, p)
        p += 8
        text = raw[p:p + ln].decode("utf-8")
        p += (ln + 3) // 4 * 4
        floats = list(struct.unpack_from("<9f", raw, p))
        p += 36
        entries.append([eid, text, floats])
    assert p == len(raw), "unexpected trailing data"
    return raw[:head_end], entries


def build(head, entries):
    out = bytearray(head)
    out += struct.pack("<i", len(entries))
    for eid, text, fl in entries:
        b = text.encode("utf-8")
        out += struct.pack("<ii", eid, len(b)) + b + b"\x00" * (-len(b) % 4)
        out += struct.pack("<9f", *fl)
    return bytes(out)


def lockit_terms(bundle, name):
    env = UnityPy.load(str(bundle))
    for o in env.objects:
        if o.type.name == "MonoBehaviour" and o.read().m_Name == name:
            return {t["Term"]: (t["Languages"][0] if t["Languages"] else "")
                    for t in o.read_typetree()["mSource"]["mTerms"]}


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    ru_terms = lockit_terms(ROOT / "work/original/AssetBundles/lockits/russian", "GeneralLockitRussian")
    ua_terms = lockit_terms(ROOT / "Disco Elysium  Ukrainian translation/lockits/german", "GeneralLockitGerman")
    norm = lambda s: re.sub(r"[\s\-]", "", s).lower()

    env = UnityPy.load(str(src))
    objs = {o.path_id: o for o in env.objects if o.path_id in (GERMAN_ID, RUSSIAN_ID)}
    head_de, de = parse(objs[GERMAN_ID].get_raw_data())
    _, ru = parse(objs[RUSSIAN_ID].get_raw_data())
    ru_by_id = {e[0]: e for e in ru}

    for ent in de:
        eid = ent[0]
        _, ru_text, ru_fl = ru_by_id[eid]
        keys = [t for t, v in ru_terms.items()
                if t.startswith("Actors/") and t.endswith("/Name") and norm(v) == norm(ru_text)]
        assert len(keys) == 1, (eid, ru_text, keys)
        ua = ua_terms[keys[0]]
        text = BREAKS.get(ua)
        if text is None:
            text = ua.replace(" ", "\n", 1) if "\n" in ru_text else ua
        ru_max = max(len(s) for s in ru_text.split("\n"))
        ua_max = max(len(s) for s in text.split("\n"))
        fl = list(ru_fl)
        if ua_max > ru_max:
            fl[0] = max(12.0, round(fl[0] * ru_max / ua_max * 2) / 2)
        print(f"{eid:>3} {ent[1]!r:28} -> {text!r:24} size {ru_fl[0]} -> {fl[0]}")
        ent[1], ent[2] = text, fl

    objs[GERMAN_ID].set_raw_data(build(head_de, de))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(env.file.save())
    print("written", dst, dst.stat().st_size, "bytes (source", src.stat().st_size, ")")


if __name__ == "__main__":
    main()
