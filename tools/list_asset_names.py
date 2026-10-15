"""Read-only: list Texture2D/Sprite/Font/TMP names in the game's serialized files matching a regex.

Usage: python -I tools/list_asset_names.py <disco_Data dir> <regex> [<types comma list>]
"""
import re
import sys
from pathlib import Path
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
root, rx = Path(sys.argv[1]), re.compile(sys.argv[2], re.I)
types = set((sys.argv[3] if len(sys.argv) > 3 else "Texture2D,Sprite,Font").split(","))
for f in sorted(root.iterdir()):
    if not f.is_file() or f.suffix in (".resS", ".resource", ".json", ".config", ".dll") or f.name.endswith((".resS", ".resource")):
        continue
    try:
        env = UnityPy.load(str(f))
    except Exception:
        continue
    for o in env.objects:
        if o.type.name in types:
            try:
                n = o.read().m_Name
            except Exception:
                continue
            if rx.search(n):
                print(f.name, o.type.name, o.path_id, n)
