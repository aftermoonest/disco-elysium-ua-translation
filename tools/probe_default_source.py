"""Read-only: inspect the built-in I2 language source (resources.assets MonoBehaviour 2996)."""
import re
import sys
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
env = UnityPy.load(r"D:\Games\SteamLibrary\steamapps\common\Disco Elysium\disco_Data\resources.assets")
for o in env.objects:
    if o.path_id == 2996:
        raw = o.get_raw_data()
        print("size", len(raw))
        try:
            tt = o.read_typetree()
            src = tt["mSource"]
            print("langs", [(l["Name"], l["Code"]) for l in src["mLanguages"]])
            print("terms", len(src["mTerms"]))
            for t in src["mTerms"]:
                if re.search(r"LOAD|GELAD|WAIT", t["Term"], re.I) or any(re.search(r"geladen|loading", x or "", re.I) for x in t["Languages"]):
                    print(t["Term"], t["Languages"])
        except Exception as e:
            print("typetree failed:", e)
            i = raw.find(b"LOAD_SCREEN_PANEL")
            print(raw[i - 80:i + 400])
