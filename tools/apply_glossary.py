"""Apply glossary replacements to a COPY of lockits/german (never touches the game or release folder).

Usage: python -I tools/apply_glossary.py [--write]    (dry run without --write)
Inputs : work/glossary/merged.json (Haiku verdicts), work/glossary/en_*.json (English alignment)
Outputs: work/glossary/changes.tsv (every change), work/glossary/skipped.tsv (not auto-applied),
         work/patched/lockits/german_glossary (with --write; started from the already patched work/patched/lockits/german)
Safety rules:
 * only 'inconsistent' verdicts: high confidence, or medium for whitelisted proper names; minus MANUAL (needs human decision)
 * a variant is replaced inside a UA line only if the aligned EN line contains the EN name (whole word)
 * a variant->canonical swap is automatic only when every differing word keeps its last 2 letters (so the case ending
   stays correct); otherwise it goes to skipped.tsv. Lowercase single-word variants are never auto-replaced.
 * USER rules (from CLAUDE.md glossary) are explicit stem swaps and always applied.
"""
import sys, re, json, collections, UnityPy
sys.stdout.reconfigure(encoding="utf-8")
WRITE = "--write" in sys.argv

MANUAL = {"Scab", "Scab Leader", "Shivers", "The Pigs", "Bench", "Fuck the World", "Pissf****t", "Cunoesse", "Man from Hjelmdall",
          "Bookstore", "Visual Calculus", "Prybar", "Radio", "Physical", "Operator", "Loader",
          # decisions left to the user: skill names (desync with resources.assets), names that conflict with the user glossary
          "Endurance", "Perception", "Logic", "Rhetoric", "Volition", "Eugene", "Glen", "Evrart Claire", "Titus Hardie"}
# medium-confidence verdicts are auto-applied only for these proper names / places; everything else needs high confidence
ALLOW_MEDIUM = {"Whirling-in-Rags", "Martinaise", "Doomed Commercial Area", "Detective Costeau", "Boiadeiro", "Dolores Dei",
                "Insulindian Phasmid", "Joyce Messier", "Map of Martinaise", "Remote Viewers Division", "Fishing village"}
# explicit user-glossary stem rules: (EN name or None for any line, old stem, new stem)
USER_RULES = [
    ("Whirling-in-Rags", "ганчір’ї", "лахмітті"), ("Whirling-in-Rags", "ганчір'ї", "лахмітті"),
    (None, "Мартинез", "Мартінез"), (None, "мартинез", "мартінез"),
]

rows = json.load(open("work/glossary/merged.json", encoding="utf-8"))
en_d = json.load(open("work/glossary/en_DialoguesLockit.json", encoding="utf-8"))
en_g = json.load(open("work/glossary/en_GeneralLockit.json", encoding="utf-8"))

def same_endings(v, c):
    vw, cw = v.split(), c.split()
    if len(vw) != len(cw): return False
    return all(a == b or (len(a) >= 3 and len(b) >= 3 and a[-2:].lower() == b[-2:].lower()) for a, b in zip(vw, cw))

rules, skipped = [], []
for r in rows:
    if r["verdict"] != "inconsistent" or r["en"] in MANUAL: continue
    if not (r.get("confidence") == "high" or (r.get("confidence") == "medium" and r["en"] in ALLOW_MEDIUM)):
        skipped.append((r["en"], "; ".join(r.get("variants_to_replace") or []), r.get("canonical_ua") or "", "medium confidence, not a whitelisted name")); continue
    c = (r.get("canonical_ua") or "").strip().strip("«»„”\"")
    for v in r.get("variants_to_replace") or []:
        vv = v.strip().strip("«»„”\"")
        why = None
        if not vv or not c or vv == c: continue
        if vv[0].islower() and " " not in vv: why = "lowercase single word"
        elif not same_endings(vv, c): why = "ending differs (needs inflection)"
        elif "*" in vv or "*" in c: why = "censored text"
        if why: skipped.append((r["en"], vv, c, why))
        else: rules.append((r["en"], vv, c))
rules += [(en, o, n) for en, o, n in USER_RULES]
rules = sorted(set(rules), key=lambda x: -len(x[1]))
print("auto/user rules:", len(rules), "skipped:", len(skipped))

def en_has(name, line):
    return name is None or re.search(r"(?<![a-z])" + re.escape(name.lower()) + r"(?![a-z])", line.lower())

def rewrite(term, ua, en_text, log):
    new = ua
    for en, old, repl in rules:
        if old not in new: continue
        if en is not None and not (en_text and en_has(en, en_text)): continue
        r2 = repl[:1].lower() + repl[1:] if old[:1].islower() and repl[:1].isupper() else repl  # keep case of first letter
        new2 = re.sub(r"(?<![А-Яа-яІіЇїЄєҐґ'’])" + re.escape(old), lambda m: r2, new)
        if new2 != new: new = new2
    if new != ua: log.append((term, ua, new))
    return new

def process(tt, en_map, log):
    for t in tt["mSource"]["mTerms"]:
        ua = t["Languages"][0]
        if not ua: continue
        new = rewrite(t["Term"], ua, en_map.get(t["Term"], ""), log)
        if new != ua: t["Languages"][0] = new

log = []
src = r"work\patched\lockits\german"
env = UnityPy.load(src)
for o in env.objects:
    if o.type.name == "MonoBehaviour":
        try: n = o.read().m_Name
        except Exception: continue
        if n.startswith("GeneralLockit") or n.startswith("DialoguesLockit"):
            tt = o.read_typetree()
            before = len(log)
            process(tt, en_g if n.startswith("General") else en_d, log)
            print(n, "changed terms:", len(log) - before)
            if WRITE and len(log) > before: o.save_typetree(tt)
with open("work/glossary/changes.tsv", "w", encoding="utf-8") as f:
    f.write("term\tbefore\tafter\n")
    for t, a, b in log: f.write(f"{t}\t{a.replace(chr(10), ' ')}\t{b.replace(chr(10), ' ')}\n")
with open("work/glossary/skipped.tsv", "w", encoding="utf-8") as f:
    f.write("en\tvariant\tcanonical\treason\n")
    for s in skipped: f.write("\t".join(s) + "\n")
if WRITE:
    out = r"work\patched\lockits\german_glossary"
    open(out, "wb").write(env.file.save(packer="lz4"))
    print("written", out)
