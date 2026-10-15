"""Read-only: compare an old UABE JSON dump with a translation TSV (term -> text); list changed terms.
Usage: python -I tools/compare_dump_tsv.py <dump.json> <new.tsv> [<report.tsv>]
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def terms(node, out):
    if isinstance(node, dict):
        if "Term" in node and "Languages" in node:
            arr = node["Languages"]
            arr = arr.get("Array", arr) if isinstance(arr, dict) else arr
            out[node["Term"]] = arr[0] if arr else ""
        else:
            for v in node.values():
                terms(v, out)
    elif isinstance(node, list):
        for v in node:
            terms(v, out)


def esc(s):
    return s.replace("\\", "\\\\").replace("\n", "\n").replace("\r", "\r").replace("\t", "\t")


old = {}
terms(json.load(open(sys.argv[1], encoding="utf-8")), old)
new = {}
for line in open(sys.argv[2], encoding="utf-8"):
    k, _, v = line.rstrip("\n").partition("\t")
    new[k] = v
changed = [k for k in new if k in old and esc(old[k]) != new[k]]
print(f"old terms {len(old)}, new terms {len(new)}, only-old {len(set(old)-set(new))}, only-new {len(set(new)-set(old))}, CHANGED {len(changed)}")
if len(sys.argv) > 3:
    with open(sys.argv[3], "w", encoding="utf-8") as f:
        f.write("term\told\tnew\n")
        for k in changed:
            f.write(f"{k}\t{esc(old[k])}\t{new[k]}\n")
for k in changed[:12]:
    print(" -", k, "|", esc(old[k])[:60], "=>", new[k][:60])
