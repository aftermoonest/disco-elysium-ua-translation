"""Read-only: recursive byte search (UTF-8 + UTF-16LE, case-insensitive) over a directory tree,
and, for files that UnityPy can open as bundles, inside their decompressed objects.

Usage: python -I tools/grep_tree.py <dir> <needle> [--bundles]
"""
import mmap
import re
import sys
from pathlib import Path

root, needle = Path(sys.argv[1]), sys.argv[2]
do_bundles = "--bundles" in sys.argv
pats = [re.compile(re.escape(needle.encode(e)), re.I) for e in ("utf-8", "utf-16-le")]
if do_bundles:
    import UnityPy
for f in sorted(root.rglob("*")):
    if not f.is_file() or f.stat().st_size == 0:
        continue
    rel = f.relative_to(root)
    try:
        with open(f, "rb") as fh, mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as m:
            for p in pats:
                s = p.search(m)
                if s:
                    print("RAW", rel, "@", s.start())
                    break
    except Exception as e:
        print("skip", rel, e)
    if do_bundles and f.stat().st_size < 1_500_000_000:
        try:
            with open(f, "rb") as fh:
                head = fh.read(8)
            if not head.startswith(b"UnityFS"):
                continue
            env = UnityPy.load(str(f))
            for o in env.objects:
                if o.byte_size > 60_000_000:
                    continue
                raw = o.get_raw_data()
                if any(p.search(raw) for p in pats):
                    d = o.read()
                    print("BUNDLE", rel, o.type.name, o.path_id, getattr(d, "m_Name", None))
        except Exception as e:
            print("bundle-skip", rel, str(e)[:80])
