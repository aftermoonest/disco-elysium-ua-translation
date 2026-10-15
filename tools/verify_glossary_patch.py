"""Verify work/patched/lockits/german_glossary vs work/patched/lockits/german: only expected terms differ, tags/placeholders intact."""
import sys, re, UnityPy
sys.stdout.reconfigure(encoding="utf-8")
def load(b):
    out = {}
    for o in UnityPy.load(b).objects:
        if o.type.name == "MonoBehaviour":
            try: n = o.read().m_Name
            except Exception: continue
            if n.startswith(("GeneralLockit", "DialoguesLockit")):
                tt = o.read_typetree()
                out[n] = [(t["Term"], list(t["Languages"])) for t in tt["mSource"]["mTerms"]]
    return out
a, b = load(r"work\patched\lockits\german"), load(r"work\patched\lockits\german_glossary")
tag = lambda s: sorted(re.findall(r"<[^>]*>|\{\d+\}|\[[a-z_ ]+\]|\*", s))
exp = {l.split("\t")[0] for l in open("work/glossary/changes.tsv", encoding="utf-8").read().splitlines()[1:]}
bad = diff = 0
for n in a:
    assert [t for t, _ in a[n]] == [t for t, _ in b[n]], "term order/set changed"
    for (t, la), (_, lb) in zip(a[n], b[n]):
        if la != lb:
            diff += 1
            if t not in exp: bad += 1; print("UNEXPECTED", t)
            if tag(la[0]) != tag(lb[0]): bad += 1; print("TAG MISMATCH", t)
            if la[1:] != lb[1:]: bad += 1; print("OTHER COLUMN", t)
print("changed terms:", diff, "expected:", len(exp), "problems:", bad)
