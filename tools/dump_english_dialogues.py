"""Extract English dialogue text from the addressable DialogueDatabase (dialoguebundle) -> work/glossary/en_DialoguesLockit.json
keys mimic lockit terms: 'Dialogue Text/<Articy Id>' (also other text-bearing fields as '<field>/<id>'). Read-only."""
import sys, glob, json, UnityPy
sys.stdout.reconfigure(encoding="utf-8")
f = glob.glob(r"D:\Games\SteamLibrary\steamapps\common\Disco Elysium\disco_Data\StreamingAssets\aa\StandaloneWindows64\dialoguebundle*")[0]
env = UnityPy.load(f)
o = [x for x in env.objects if x.type.name == "MonoBehaviour"][0]
tt = o.read_typetree()
out = {}
for c in tt["conversations"]:
    for e in c["dialogueEntries"]:
        fl = {x["title"]: x["value"] for x in e["fields"]}
        aid = fl.get("Articy Id")
        if not aid: continue
        for k in ["Dialogue Text"] + [f"Alternate{i}" for i in range(1, 5)] + [f"tooltip{i}" for i in range(1, 11)]:
            if fl.get(k): out[f"{k}/{aid}"] = fl[k]
json.dump(out, open("work/glossary/en_DialoguesLockit.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(out))
