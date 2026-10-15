"""Read-only check: patched collage/shared vs original — only the German column may differ."""
import re
import sys
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")


def load(p):
    env = UnityPy.load(p)
    objs = {(o.type.name, o.path_id): o for o in env.objects}
    lock = next(o for o in objs.values() if o.type.name == "MonoBehaviour" and o.read().m_Name == "CollageModeLockit")
    return objs, lock.read_typetree()["mSource"]


oo, a = load(sys.argv[1])
po, b = load(sys.argv[2])
print("objects:", len(oo), len(po), "same ids:", set(oo) == set(po))
for k in oo:
    if oo[k].type.name != "MonoBehaviour" or oo[k].read().m_Name != "CollageModeLockit":
        assert oo[k].get_raw_data() == po[k].get_raw_data(), ("other object changed", k)
print("other objects byte-identical")
de = [l["Code"] for l in a["mLanguages"]].index("de")
assert [l["Code"] for l in b["mLanguages"]] == [l["Code"] for l in a["mLanguages"]]
assert len(a["mTerms"]) == len(b["mTerms"])
changed = bad = 0
for x, y in zip(a["mTerms"], b["mTerms"]):
    assert x["Term"] == y["Term"]
    for i, (u, v) in enumerate(zip(x["Languages"], y["Languages"])):
        if i != de:
            assert u == v, ("non-German column changed", x["Term"], i)
    en = x["Languages"][0]
    ua = y["Languages"][de]
    if x["Languages"][de] != ua:
        changed += 1
        if sorted(re.findall(r"\{\d\}", en)) != sorted(re.findall(r"\{\d\}", ua)):
            print("PLACEHOLDER MISMATCH", x["Term"]); bad += 1
        if re.findall(r"<[^>]+>", ua) and sorted(re.findall(r"</?(?:b|i|align)\b", ua)) == []:
            print("TAG?", x["Term"])
        if re.search(r"[äöüßÄÖÜ]", ua):
            print("GERMAN LEFT", x["Term"], ua[:60]); bad += 1
print("changed German terms:", changed, "problems:", bad)
for t in b["mTerms"]:
    if t["Term"] in ("Collage/BUTTON/LOADING", "Collage/HIDDEN/FASCIST"):
        print(t["Term"], "->", repr(t["Languages"][de][:90]))
# Latin-letter leftovers (should be only intentional proper names)
lat = [(t["Term"], t["Languages"][de]) for t in b["mTerms"] if t["Languages"][de] and re.search(r"[A-Za-z]{3,}", re.sub(r"<[^>]+>", "", t["Languages"][de])) and "CONTENT_POLICY" not in t["Term"]]
print("Latin text kept:", lat)
