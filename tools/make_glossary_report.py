"""Generate docs/glossary_report.md from work/glossary/{merged.json,changes.tsv,skipped.tsv}."""
import json, re, sys, collections, difflib
sys.stdout.reconfigure(encoding="utf-8")
rows = json.load(open("work/glossary/merged.json", encoding="utf-8"))
rd = lambda p: [l.rstrip("\n").split("\t") for l in open(p, encoding="utf-8")][1:]
ch, sk = rd("work/glossary/changes.tsv"), rd("work/glossary/skipped.tsv")
tok = lambda s: re.findall(r"\S+", s)
strip = lambda s: s.strip(".,;:!?«»\"“”()")
import UnityPy
def _load_ru():
    out = {}
    for o in UnityPy.load("work/original/AssetBundles/lockits/russian").objects:
        if o.type.name == "MonoBehaviour":
            try: n = o.read().m_Name
            except Exception: continue
            if n.startswith(("GeneralLockit", "DialoguesLockit")):
                for t in o.read_typetree()["mSource"]["mTerms"]: out[t["Term"]] = t["Languages"][0] if t["Languages"] else ""
    return out
RU = _load_ru()
EN = {**json.load(open("work/glossary/en_GeneralLockit.json", encoding="utf-8")), **json.load(open("work/glossary/en_DialoguesLockit.json", encoding="utf-8"))}
CH = {t: (a, b) for t, a, b in ch}
def clip(x, a, n=230):
    i = x.find(a); i = 0 if i < 0 else max(0, i - 80)
    return x[i:i + n].replace("\n", " ").replace("|", "/")
pairs, ex = collections.Counter(), {}
for t, a, b in ch:
    ta, tb = tok(a), tok(b)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb).get_opcodes():
        if op == "replace":
            k = (strip(" ".join(ta[i1:i2])), strip(" ".join(tb[j1:j2]))); pairs[k] += 1; ex.setdefault(k, t)
cnt = collections.Counter(t.split("/")[0] for t, _, _ in ch)
dial = sum(v for k, v in cnt.items() if k.startswith(("Dialogue Text", "Alternate", "tooltip")))
V = collections.Counter(r["verdict"] for r in rows)
C = collections.Counter((r["category"], r["verdict"]) for r in rows)
man = {"Scab", "Scab Leader", "Shivers", "The Pigs", "Bench", "Fuck the World", "Pissf****t", "Cunoesse", "Man from Hjelmdall", "Bookstore", "Visual Calculus", "Prybar", "Radio", "Physical", "Operator", "Loader", "Endurance", "Perception", "Logic", "Rhetoric", "Volition", "Eugene", "Glen", "Evrart Claire", "Titus Hardie"}
L = []; A = L.append
A("# Звіт: уніфікація термінології (2026-10-15)\n")
A("## 1. Що зроблено\n")
A("1. Знайдено англійський оригінал у файлах гри: загальні рядки (5 476) у `resources.assets`, діалоги (72 893) у `dialoguebundle` (Pixel Crushers DialogueDatabase); 72 771 із 73 948 українських діалогових ключів мають EN-пару.")
A("2. `tools/build_term_table.py` зібрав 791 канонічну сутність (персонажі, предмети, думки, локації, навички…) у `work/glossary/terms.tsv` і знайшов 243 кандидати, де EN-назва є в рядку, а українського канонічного кореня немає.")
A("3. 235 кандидатів (без «abilities») розібрали 12 агентів Haiku; вердикти в `work/glossary/out/`, зведення в `merged.json` та `docs/glossary.md`.")
A("4. `tools/apply_glossary.py` застосував лише безпечну підмножину на копії `work/patched/lockits/german_glossary`; `tools/verify_glossary_patch.py` перевірив. **У гру нічого не встановлено.**\n")
A("## 2. Вердикти Haiku\n")
A("| Вердикт | К-сть |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in V.most_common()))
A("\n| Категорія | inconsistent | ok | unclear |\n|---|---|---|---|")
for c in sorted({r["category"] for r in rows}): A(f"| {c} | {C[(c,'inconsistent')]} | {C[(c,'ok')]} | {C[(c,'unclear')]} |")
A("\nЯкість Haiku змішана (вердикти за 4 зразками на сутність): високу впевненість приймав автоматично, середню лише для перевірених власних назв.\n")
A("## 3. Застосовано: було → стало\n")
A(f"Змінено термів: **{len(ch)}** (діалоги й альтернативи: {dial}; загальні рядки: {len(ch)-dial}). Теги, плейсхолдери та інші мовні колонки не змінені (перевірка: 0 проблем).\n")
A("| Було | Стало | Термів | EN (приклад) | RU (приклад) | UA було | UA стало | Ключ |\n|---|---|---|---|---|---|---|---|")
for (a, b), n in pairs.most_common(): A(f"| {a} | {b} | {n} | {clip(EN.get(ex[(a,b)],''), a, 140)} | {clip(RU.get(ex[(a,b)],''), a, 140)} | {clip(CH[ex[(a,b)]][0], a, 140)} | {clip(CH[ex[(a,b)]][1], b, 140)} | `{ex[(a,b)]}` |")
A("\n### Приклади (EN / RU / UA до / UA після)\n")
A("| Заміна | EN | RU | UA було | UA стало |\n|---|---|---|---|---|")
for (a, b), n in pairs.most_common():
    k = ex[(a, b)]; ua0, ua1 = CH[k]
    A(f"| {a} → {b} | {clip(EN.get(k,''), a)} | {clip(RU.get(k,''), a)} | {clip(ua0, a)} | {clip(ua1, b)} |")
A("\nПовний лог із рядками до/після: `work/glossary/changes.tsv`.\n\nНазви (Name/DisplayName), що змінилися:\n")
A("| Ключ | Було | Стало |\n|---|---|---|")
for t, a, b in ch:
    if t.endswith(("/Name", "/DisplayName")) or t.startswith("Area Names/"): A(f"| `{t}` | {a} | {b} |")
A("\n## 4. НЕ застосовано, потрібне твоє рішення\n")
CONF = {x["term"]: x for x in json.load(open("work/glossary/conflicts.json", encoding="utf-8"))}
A("**4.1 Свідомо залишено на ручне рішення**\n")
A("Для кожної сутності: що пропонує Haiku, які варіанти реально трапляються, і до 4 прикладів у тексті (EN → RU → UA як є зараз).\n")
for r in rows:
    if r["en"] not in man or r["verdict"] == "ok": continue
    A(f"#### {r['en']} ({r['category']})\n")
    A(f"- Поточна назва в lockit: **{r['current']}**; RU: {r.get('ru','')}")
    A(f"- Пропозиція Haiku: **{r.get('canonical_ua','') or '—'}** (впевненість: {r.get('confidence','')}); варіанти в тексті: {'; '.join(r.get('variants_to_replace') or []) or '—'}")
    A(f"- Збігів з канонічною формою: {r.get('hit')}, без неї: {r.get('miss')}")
    A(f"- Примітка Haiku: {(r.get('note') or '').strip()}\n")
    for sm in CONF.get(r["term"], {}).get("samples", [])[:4]:
        A(f"  - `{sm['key']}`")
        A(f"    - EN: {sm['en'].replace(chr(10), ' ')}")
        A(f"    - RU: {sm['ru'].replace(chr(10), ' ')}")
        A(f"    - UA (зараз): {sm['ua'].replace(chr(10), ' ')}")
    A("")
A("\nНавички (Endurance, Perception…) не чіпав: їхні назви вже вручну виправлені в `resources.assets`, зміна в lockit розсинхронізує інтерфейс. Імена (Євген/Ежен, Ґлен/Глен) та «Еврар Клер» проти «Еврарт» із твого глосарію потребують вибору.\n")
A("**4.2 Пропущено автоматикою**\n")
A("| Причина | К-сть |\n|---|---|\n" + "\n".join(f"| {k} | {v} |" for k, v in collections.Counter(s[3] for s in sk).most_common()))
A("\nЗаміни з відмінюванням (напр. «Тіта Харді» → «Тита Харді») автоматично не робив. Список: `work/glossary/skipped.tsv`.\n")
A("## 5. Інші знахідки (не термінологія)\n")
for x in ["`ABILITY_SHORT_INT` «Введення» (помилка Input) і HUD-скорочення виправлені раніше (`work/patched/lockits/german`).",
 "«ЖБК» замість «ЖК» у діалогах про квартири Капсайду (7 сутностей), потрібна правка.",
 "Barbell: «blini» (диски штанги) перекладено «Млинці» (оладки).",
 "«Horrific Necktie»: «краватка» (жін.) з чоловічими прикметниками; правильно «Жахлива краватка».",
 "«Visual Calculus»: у діалогах «Візуальна реконструкція», у назві «Візуальний аналіз» (є вже в російському оригіналі).",
 "tooltip2 «Don't let down Cunoesse!» перекладено «Підчепити»: імовірно зсув ключів RU/EN.",
 "Haiku запропонував «Тремтіння» → «Трепет» (актор Shivers); не застосовано."]: A("- " + x)
A("\n## 6. Файли\n\n- Копія з правками: `work/patched/lockits/german_glossary` (база: `work/patched/lockits/german` з HUD-скороченнями).\n- Скрипти: `tools/dump_english_lockits.py`, `dump_english_dialogues.py`, `build_term_table.py`, `apply_glossary.py`, `verify_glossary_patch.py`, `make_glossary_report.py`.\n- Дані: `work/glossary/` (terms.tsv, conflicts.json, merged.json, changes.tsv, skipped.tsv). `work/` не в git.")
open("docs/glossary_report.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(L), len(pairs))
