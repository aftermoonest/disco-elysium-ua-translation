"""Read-only raw byte search for text in Unity game data files (UTF-8 and UTF-16LE).

Usage: python -I tools/grep_game.py <data_dir> <needle> [<needle> ...]
Skips .resS/.resource streams. Case-insensitive for ASCII needles.
Note: compressed AssetBundles will not match; use grep_bundles.py for those.
"""
import re
import sys
from pathlib import Path

SKIP_SUFFIX = {".ress", ".resource", ".manifest"}


def main():
    root = Path(sys.argv[1])
    needles = sys.argv[2:]
    pats = []
    for n in needles:
        for enc in ("utf-8", "utf-16-le"):
            pats.append((n, enc, re.compile(re.escape(n.encode(enc)), re.I)))
    for f in sorted(root.iterdir()):
        if not f.is_file() or f.suffix.lower() in SKIP_SUFFIX:
            continue
        data = f.read_bytes()
        for n, enc, p in pats:
            hits = [m.start() for m in p.finditer(data)]
            if hits:
                print(f"{f.name}\t{n!r}\t{enc}\t{len(hits)} hits\tfirst@{hits[0]}")


if __name__ == "__main__":
    main()
