"""Read-only: dump CollageModeLockit terms (English / German / Russian columns) to a TSV for review.

Usage: python -I tools/dump_collage_lockit.py <out.tsv>
"""
import sys
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
D = r"D:\Games\SteamLibrary\steamapps\common\Disco Elysium\disco_Data"
env = UnityPy.load(D + r"\StreamingAssets\AssetBundles\Windows\collage\shared")
for o in env.objects:
    if o.type.name == "MonoBehaviour" and o.read().m_Name == "CollageModeLockit":
        src = o.read_typetree()["mSource"]
        codes = [l["Code"] for l in src["mLanguages"]]
        ie, ig, ir = codes.index("en"), codes.index("de"), codes.index("ru")
        rows = [(t["Term"], t["Languages"][ie], t["Languages"][ig], t["Languages"][ir]) for t in src["mTerms"]]
        with open(sys.argv[1], "w", encoding="utf-8") as f:
            f.write("term\ten\tde\tru\n")
            for r in rows:
                f.write("\t".join(x.replace("\n", "\n").replace("\t", " ") for x in r) + "\n")
        print(len(rows), "terms; de==en:", sum(1 for r in rows if r[1] == r[2]))
