"""Read-only: export Texture2D/Sprite assets whose name contains a substring to PNG.

Usage: python -I tools/export_texture.py <bundle> <name_substring> <out_dir> [tag]
Prints bundle, object type, path_id, name, size, format for every match.
"""
import sys
from pathlib import Path
import UnityPy

bundle, needle, out = sys.argv[1], sys.argv[2].lower(), Path(sys.argv[3])
tag = sys.argv[4] if len(sys.argv) > 4 else Path(bundle).name
out.mkdir(parents=True, exist_ok=True)
env = UnityPy.load(bundle)
for o in env.objects:
    if o.type.name not in ("Texture2D", "Sprite"):
        continue
    d = o.read()
    if needle in d.m_Name.lower():
        img = d.image
        fn = out / f"{tag}__{o.type.name}_{o.path_id}_{d.m_Name}.png"
        img.save(fn)
        print(tag, o.type.name, o.path_id, d.m_Name, img.size, getattr(d, "m_TextureFormat", None), "->", fn.name)
