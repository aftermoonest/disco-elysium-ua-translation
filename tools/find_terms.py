"""Read-only: search lockit terms by key or value substring across languages.

Usage: python -I tools/find_terms.py <substring> [<substring> ...]
Looks at GeneralLockit* in game lockits for russian/french/spanish/polish + the mod german (Ukrainian).
"""
import sys
from pathlib import Path
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
base = Path(r"D:\Games\SteamLibrary\steamapps\common\Disco Elysium\disco_Data\StreamingAssets\AssetBundles\Windows\lockits")
needles = [n.lower() for n in sys.argv[1:]]
for lang in ("german", "russian", "french", "spanish", "polish"):
    env = UnityPy.load(str(base / lang))
    for o in env.objects:
        if o.type.name == "MonoBehaviour" and o.read().m_Name.startswith("GeneralLockit"):
            for t in o.read_typetree()["mSource"]["mTerms"]:
                v = t["Languages"][0] if t["Languages"] else ""
                if any(n in t["Term"].lower() or n in v.lower() for n in needles):
                    print(lang, "|", t["Term"], "|", repr(v[:80]))
