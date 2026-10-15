"""Apply the user's explicit glossary decisions (2026-10-15) on top of work/patched/lockits/german_glossary.

Usage: python -I tools/apply_decisions.py [--write]
Output: work/glossary/decisions_changes.tsv, work/patched/lockits/german_final (with --write). Never touches the game.
Each rule applies only to UA lines whose aligned English line matches the rule's EN pattern.
"""
import sys, re, json, UnityPy
sys.stdout.reconfigure(encoding="utf-8")
WRITE = "--write" in sys.argv

CYR = "А-Яа-яІіЇїЄєҐґ'’"
def W(pat): return r"(?<![" + CYR + r"])" + pat + r"(?![" + CYR + r"])"

def keep_case(old, new):
    if old.isupper() and len(old) > 1: return new.upper()
    if old[:1].isupper(): return new[:1].upper() + new[1:]
    return new

# (EN regex, UA regex (case-insensitive), replacement (lowercase base) or callable)
def table(mapping):
    return lambda m: keep_case(m.group(0), mapping[m.group(0).lower()])

TITUS = {"тіт": "тітус", "тит": "тітус", "титус": "тітус", "тіта": "тітуса", "тита": "тітуса", "тіту": "тітусу", "титу": "тітусу",
         "тітом": "тітусом", "титом": "тітусом", "тіте": "тітусе", "тите": "тітусе", "титусе": "тітусе"}
EUGENE = {"ежен": "євген", "єжен": "євген", "ежена": "євгена", "ежену": "євгену", "еженом": "євгеном", "ежене": "євгене"}
PIGS = {"смітник": "мусор", "смітником": "мусором", "смітнику": "мусоре", "смітника": "мусора"}
PRYBAR = {"ломик": "лом", "ломика": "лома", "ломику": "лому", "ломиком": "ломом", "ломики": "ломи", "ломиків": "ломів",
          "монтувалкою": "ломом"}

RULES = [
    # Titus Hardie -> Тітус Харді
    (r"\bTitus\b|\bHardie", W("(?:" + "|".join(TITUS) + ")"), table(TITUS)),
    (r"\bHardie", W("гарді"), lambda m: keep_case(m.group(0), "харді")),
    # Scab Leader -> лідер антистрайкарів
    (r"scab.{0,12}lead|lead\w* of the scabs?", W(r"(лідер|командир)(а|у|ом|і)? (антипікетників|антиповстанців|антистрайкарів)"),
     lambda m: keep_case(m.group(1), "лідер" + (m.group(2) or "")) + " антистрайкарів"),
    (r"scab.{0,12}lead|lead\w* of the scabs?", W(r"лідер страйколомів"), lambda m: "Лідер антистрайкарів"),
    (r"scab.{0,12}lead|lead\w* of the scabs?", W(r"лідер страйкарів"), lambda m: "Лідер антистрайкарів"),
    (r"scab.{0,12}lead|lead\w* of the scabs?", W(r"лідер скабів"), lambda m: "лідер антистрайкарів".upper() if m.group(0).isupper() else "Лідер антистрайкарів"),
    (r"scab.{0,12}lead|lead\w* of the scabs?", W(r"лідер шахраїв"), lambda m: "Лідер антистрайкарів"),
    # Eugene -> Євген
    (r"\bEugene\b", W("(?:" + "|".join(EUGENE) + ")"), table(EUGENE)),
    # The Pigs -> Мусор (name term itself is set to «Мусора» below)
    (r"\bpigs?\b", W("(?:" + "|".join(PIGS) + ")"), table(PIGS)),
    # Prybar -> лом (phrases first: gender/number agreement)
    (r"pry ?bar|crowbar", W(r"непогана монтування"), lambda m: "непоганий лом"),
    (r"pry ?bar|crowbar", W(r"надійна монтування"), lambda m: "надійний лом"),
    (r"pry ?bar|crowbar", W(r"звичайні монтування"), lambda m: "звичайні ломи"),
    (r"pry ?bar|crowbar", W(r"зразок монтування"), lambda m: "зразок лома"),
    (r"pry ?bar|crowbar", W(r"вставляєш монтування"), lambda m: "вставляєш лом"),
    (r"pry ?bar|crowbar", W("монтування"), lambda m: keep_case(m.group(0), "лом")),
    (r"pry ?bar|crowbar", W("(?:" + "|".join(PRYBAR) + ")"), table(PRYBAR)),
    # any remaining diminutive ломик -> лом (nobody says ломик in Ukraine)
    (r".", W("(?:ломик|ломика|ломику|ломиком|ломики|ломиків)"), table(PRYBAR)),
    (r"^Prybar$|^pry ?bar", W("монтування"), lambda m: keep_case(m.group(0), "лом")),
    # Perception -> Сприйняття in skill lists / tooltips
    (r"\bPerception\b", W("увага"), lambda m: "Сприйняття"),
    (r"\bPerception\b", W("відчуття"), lambda m: "Сприйняття"),
]
RULES = [(re.compile(e, re.I), re.compile(u, re.I), f) for e, u, f in RULES]
NAME_OVERRIDES = {"Actors/0x0100002F0000F964/Name": "Мусора"}  # The Pigs

en = {**json.load(open("work/glossary/en_GeneralLockit.json", encoding="utf-8")),
      **json.load(open("work/glossary/en_DialoguesLockit.json", encoding="utf-8"))}

# gender/number agreement fixes after монтування (n.) -> лом (m.)
AGREE = {
    "Dialogue Text/0x010000060001A208": [("до неї претензій", "до нього претензій")],
    "Dialogue Text/0x0100005A00006640": [("Лом... не дало", "Лом... не дав")],
    "Dialogue Text/0x0100004500000734": [("виснеш на ній", "виснеш на ньому")],
    "Items/prybar/Description": [("Вона приємно", "Він приємно")],
}

APPEND = {"LEGAL_TEXT_PC": "\nПереклад зроблено AfterMoonest"}  # credit line at the end of the legal splash

def rewrite(term, ua):
    if term in APPEND: return ua.rstrip() + APPEND[term]
    if term in NAME_OVERRIDES: return NAME_OVERRIDES[term]
    e = en.get(term, "")
    new = ua
    for ere, ure, f in RULES:
        if ere.search(e): new = ure.sub(f, new)
    for a, b in AGREE.get(term, []):
        if new != ua: new = new.replace(a, b)
    return new

log = []
env = UnityPy.load(r"work\patched\lockits\german_glossary")
for o in env.objects:
    if o.type.name == "MonoBehaviour":
        try: n = o.read().m_Name
        except Exception: continue
        if n.startswith(("GeneralLockit", "DialoguesLockit")):
            tt = o.read_typetree(); ch = 0
            for t in tt["mSource"]["mTerms"]:
                ua = t["Languages"][0]
                if not ua: continue
                new = rewrite(t["Term"], ua)
                if new != ua:
                    log.append((t["Term"], ua, new)); t["Languages"][0] = new; ch += 1
            print(n, "changed:", ch)
            if WRITE and ch: o.save_typetree(tt)
with open("work/glossary/decisions_changes.tsv", "w", encoding="utf-8") as f:
    f.write("term\tbefore\tafter\n")
    for t, a, b in log: f.write(f"{t}\t{a.replace(chr(10), ' ')}\t{b.replace(chr(10), ' ')}\n")
if WRITE:
    out = r"work\patched\lockits\german_final"
    open(out, "wb").write(env.file.save(packer="lz4")); print("written", out)
