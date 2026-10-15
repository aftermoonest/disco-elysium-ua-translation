"""Read-only: dump MonoBehaviours of a scene file that contain a needle, with parsed GameObject/components refs.
Usage: python -I tools/dump_level_mb.py <levelN> <needle>
"""
import sys
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
env = UnityPy.load(sys.argv[1])
needle = sys.argv[2].lower().encode()
for o in env.objects:
    if o.type.name == "MonoBehaviour":
        raw = o.get_raw_data()
        if needle in raw.lower():
            print("MB", o.path_id, len(raw))
            for i in range(0, len(raw), 32):
                print("  %04x" % i, raw[i:i + 32].hex(" "), "".join(chr(b) if 32 <= b < 127 else "." for b in raw[i:i + 32]))
            try:
                d = o.read()
                print("  script:", d.m_Script.read().m_ClassName if d.m_Script else None, "go:", d.m_GameObject.read().m_Name if d.m_GameObject else None)
            except Exception as e:
                print("  (read failed)", str(e)[:80])
