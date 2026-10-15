"""Build a patched COPY of collage/shared with the German column of CollageModeLockit in Ukrainian.

Usage: python -I tools/patch_collage_lockit.py <source collage/shared> <translations.json> <out collage/shared>
Never writes to the game folder. Only terms with a non-empty German value are touched; all of them must be
covered by the translations file (asserted).
"""
import json
import sys
from pathlib import Path

import UnityPy

sys.stdout.reconfigure(encoding="utf-8")


def main():
    src, tr_path, dst = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    tr = json.loads(tr_path.read_text(encoding="utf-8"))
    env = UnityPy.load(str(src))
    for o in env.objects:
        if o.type.name == "MonoBehaviour" and o.read().m_Name == "CollageModeLockit":
            tt = o.read_typetree()
            break
    else:
        raise SystemExit("CollageModeLockit not found")
    codes = [l["Code"] for l in tt["mSource"]["mLanguages"]]
    de = codes.index("de")
    todo = [t for t in tt["mSource"]["mTerms"] if t["Languages"][de]]
    missing = [t["Term"] for t in todo if t["Term"] not in tr]
    extra = [k for k in tr if k not in {t["Term"] for t in todo}]
    assert not missing, f"untranslated terms: {missing}"
    assert not extra, f"translations for terms without German value: {extra}"
    for t in todo:
        t["Languages"][de] = tr[t["Term"]]
    o.save_typetree(tt)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(env.file.save(packer="lz4"))
    print(f"patched {len(todo)} terms -> {dst} ({dst.stat().st_size} bytes, source {src.stat().st_size})")


if __name__ == "__main__":
    main()
