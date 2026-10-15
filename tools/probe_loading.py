"""Read-only: where does the loading-screen text come from? (collage lockit 'geladen', LOAD_SCREEN_PANEL users)"""
import sys
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
D = r"D:\Games\SteamLibrary\steamapps\common\Disco Elysium\disco_Data"
env = UnityPy.load(D + r"\StreamingAssets\AssetBundles\Windows\collage\shared")
for o in env.objects:
    if o.type.name == "MonoBehaviour":
        d = o.read()
        if d.m_Name == "CollageModeLockit":
            src = o.read_typetree()["mSource"]
            print("languages:", [(l["Name"], l["Code"]) for l in src["mLanguages"]])
            for t in src["mTerms"]:
                if any("geladen" in (x or "").lower() for x in t["Languages"]):
                    print("TERM", t["Term"], t["Languages"])
env = UnityPy.load(D + r"\resources.assets")
for o in env.objects:
    if o.byte_size > 3_000_000:
        continue
    r = o.get_raw_data()
    i = r.find(b"LOAD_SCREEN_PANEL")
    if i >= 0:
        print(o.type.name, o.path_id, o.byte_size, r[max(0, i - 60):i + 60])
