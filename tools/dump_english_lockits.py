"""Read English General/Dialogues lockits from game data files (no typetree there) using the node
layout borrowed from the Russian lockit bundle. Writes work/glossary/en_<name>.json {Term: text}. Read-only."""
import sys, json, UnityPy
sys.stdout.reconfigure(encoding="utf-8")
D = r"D:\Games\SteamLibrary\steamapps\common\Disco Elysium\disco_Data"
ru = UnityPy.load(r"work\original\AssetBundles\lockits\russian")
nodes = {}
for o in ru.objects:
    if o.type.name == "MonoBehaviour":
        try: n = o.read().m_Name
        except Exception: continue
        if n in ("GeneralLockitRussian", "DialoguesLockitRussian"):
            nodes[n.replace("Russian", "")] = o._get_typetree_node()
for src, pid, name in ((D + r"\resources.assets", 2996, "GeneralLockit"), (D + r"\sharedassets1.assets", 9782, "DialoguesLockit")):
    env = UnityPy.load(src)
    o = [x for x in env.objects if x.path_id == pid][0]
    tt = o.read_typetree(nodes[name])
    s = tt["mSource"]
    print(name, [l["Code"] for l in s["mLanguages"]], len(s["mTerms"]))
    out = {t["Term"]: (t["Languages"][0] if t["Languages"] else "") for t in s["mTerms"]}
    json.dump(out, open(f"work/glossary/en_{name}.json", "w", encoding="utf-8"), ensure_ascii=False)
    for k in list(out)[:3]: print(" ", k, repr(out[k][:80]))
