"""Read-only: export Texture2D objects from a serialized file by name list to PNG (downscaled preview).
Usage: python -I tools/export_by_id.py <serialized file> <out dir> <name> [<name> ...]
"""
import sys
from pathlib import Path
import UnityPy

f, out = sys.argv[1], Path(sys.argv[2])
names = set(sys.argv[3:])
out.mkdir(parents=True, exist_ok=True)
env = UnityPy.load(f)
for o in env.objects:
    if o.type.name == "Texture2D":
        d = o.read()
        if d.m_Name in names:
            im = d.image
            print(d.m_Name, o.path_id, im.size)
            im.thumbnail((1600, 1000))
            im.convert("RGB").save(out / f"{Path(f).name}_{d.m_Name}.png")
