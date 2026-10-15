"""Read-only: find which Unity object in resources.assets holds a given text.

Usage: python -I tools/inspect_resources.py <resources.assets> <needle>
"""
import sys
import UnityPy

path, needle = sys.argv[1], sys.argv[2].encode()
env = UnityPy.load(path)
for obj in env.objects:
    if obj.byte_size > 5_000_000:
        continue
    raw = obj.get_raw_data()
    if needle.lower() in raw.lower():
        name = None
        try:
            name = obj.read().name if hasattr(obj.read(), "name") else None
        except Exception:
            pass
        print(obj.type.name, "path_id", obj.path_id, "size", obj.byte_size, "name", name)
        if obj.type.name == "TextAsset":
            t = obj.read()
            print(t.text[:1500] if hasattr(t, "text") else "")
