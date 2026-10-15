"""Build glossary candidate tables (read-only on game/mod files).
Inputs: work/glossary/en_*.json (tools/dump_english_*.py), UA mod lockits, RU lockits.
Outputs: work/glossary/terms.tsv (canonical entities: category, term, EN, RU, UA)
         work/glossary/conflicts.json (entities whose UA name is often absent from UA lines where EN name occurs)
"""
import sys, json, re, collections, UnityPy
sys.stdout.reconfigure(encoding="utf-8")

def load(bundle, prefix):
    out = {}
    for o in UnityPy.load(bundle).objects:
        if o.type.name == "MonoBehaviour":
            try: n = o.read().m_Name
            except Exception: continue
            if n.startswith(prefix):
                for t in o.read_typetree()["mSource"]["mTerms"]:
                    out[t["Term"]] = t["Languages"][0] if t["Languages"] else ""
    return out

UA_B = r"Disco Elysium  Ukrainian translation\lockits\german"
RU_B = r"work\original\AssetBundles\lockits\russian"
ua_g, ru_g = load(UA_B, "GeneralLockit"), load(RU_B, "GeneralLockit")
ua_d, ru_d = load(UA_B, "DialoguesLockit"), load(RU_B, "DialoguesLockit")
en_g = json.load(open("work/glossary/en_GeneralLockit.json", encoding="utf-8"))
en_d = json.load(open("work/glossary/en_DialoguesLockit.json", encoding="utf-8"))

def category(term):
    p = term.split("/")
    if p[0] == "Actors" and term.endswith("/Name"): return "actor"
    if p[0] == "Items" and term.endswith("/DisplayName"): return "item"
    if p[0] == "Thoughts" and term.endswith("/DisplayName"): return "thought"
    if p[0] in ("Skills", "Abilities", "Area Names", "Archetypes", "Difficulties"): return p[0].lower().replace(" ", "_")
    return None

rows = []
for t, ua in ua_g.items():
    c = category(t)
    if c and ua.strip():
        rows.append((c, t, en_g.get(t, ""), ru_g.get(t, ""), ua))
with open("work/glossary/terms.tsv", "w", encoding="utf-8") as f:
    f.write("category\tterm\ten\tru\tua\n")
    for r in rows: f.write("\t".join(x.replace("\t", " ").replace("\n", " ") for x in r) + "\n")
print("terms:", len(rows), collections.Counter(r[0] for r in rows))

# conflict scan: EN name occurs in EN dialogue line, but UA canonical stem is absent from the UA line
keys = [k for k in en_d if k in ua_d]
en_low = {k: en_d[k].lower() for k in keys}
ua_low = {k: ua_d[k].lower() for k in keys}
def stems(ua):
    return [w[:max(4, len(w) - 3)] for w in re.findall(r"[а-яіїєґ'’ʼ-]+", ua.lower()) if len(w) >= 3]
res = []
for c, t, en, ru, ua in rows:
    name = en.strip().lower()
    if c not in ("actor", "item", "thought", "area_names", "archetypes", "skills", "abilities") or len(name) < 4 or not re.search(r"[a-z]", name):
        continue
    if "{" in name or "<" in name: continue
    pat = re.compile(r"(?<![a-z])" + re.escape(name) + r"(?![a-z])")
    st = stems(ua)
    if not st: continue
    hit = miss = 0; samples = []
    for k in keys:
        if name in en_low[k] and pat.search(en_low[k]):
            if all(s in ua_low[k] for s in st): hit += 1
            else:
                miss += 1
                if len(samples) < 6: samples.append({"key": k, "en": en_d[k][:260], "ru": ru_d.get(k, "")[:260], "ua": ua_d[k][:260]})
    if hit + miss >= 2 and miss >= 1:
        res.append({"category": c, "term": t, "en": en, "ru": ru, "ua": ua, "hit": hit, "miss": miss, "samples": samples})
res.sort(key=lambda r: -r["miss"])
json.dump(res, open("work/glossary/conflicts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("conflict candidates:", len(res), collections.Counter(r["category"] for r in res))
