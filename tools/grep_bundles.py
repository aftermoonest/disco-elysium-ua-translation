"""Read-only: search text inside AssetBundles (decompressed by UnityPy).

Usage: python -I tools/grep_bundles.py <bundle_or_dir> <needle> [<needle> ...]
Searches raw object bytes (UTF-8 and UTF-16LE), prints bundle, object type, path_id, name.
"""
import sys
from pathlib import Path
import UnityPy

target = Path(sys.argv[1])
needles = [n for n in sys.argv[2:]]
pats = []
for n in needles:
    pats += [(n, n.lower().encode("utf-8")), (n, n.lower().encode("utf-16-le"))]

files = [target] if target.is_file() else [
    f for f in target.rglob("*") if f.is_file() and f.suffix != ".manifest"]
for f in files:
    try:
        env = UnityPy.load(str(f))
    except Exception:
        continue
    for obj in env.objects:
        if obj.byte_size > 30_000_000:
            continue
        raw = obj.get_raw_data().lower()
        for n, p in pats:
            if p in raw:
                name = None
                try:
                    name = getattr(obj.read(), "name", None) or getattr(obj.read(), "m_Name", None)
                except Exception:
                    pass
                print(f"{f.parent.name}/{f.name}\t{obj.type.name}\tpath_id={obj.path_id}\t{name}\t{n!r}")
                break
