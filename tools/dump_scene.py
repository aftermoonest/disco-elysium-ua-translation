"""Read-only: list GameObjects and printable strings of MonoBehaviours in a scene file (level0, level1, ...).
Usage: python -I tools/dump_scene.py <levelN file>
"""
import re
import sys
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
env = UnityPy.load(sys.argv[1])
for o in env.objects:
    t = o.type.name
    if t == "GameObject":
        d = o.read()
        print("GO", o.path_id, d.m_Name)
    elif t == "MonoBehaviour":
        raw = o.get_raw_data()
        strs = [s.decode("utf-8", "replace") for s in re.findall(rb"[\x20-\x7e\xc2-\xf4\x80-\xbf]{4,}", raw)]
        print("MB", o.path_id, o.byte_size, strs[:8])
