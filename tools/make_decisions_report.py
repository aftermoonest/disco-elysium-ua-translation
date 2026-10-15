"""docs/glossary_decisions.md: what changed per user decision, with EN/RU/UA before/after examples."""
import sys, re, json, collections, UnityPy
sys.stdout.reconfigure(encoding="utf-8")
rows = [l.rstrip("\n").split("\t") for l in open("work/glossary/decisions_changes.tsv", encoding="utf-8")][1:]
en = {**json.load(open("work/glossary/en_GeneralLockit.json", encoding="utf-8")), **json.load(open("work/glossary/en_DialoguesLockit.json", encoding="utf-8"))}
ru = {}
for o in UnityPy.load("work/original/AssetBundles/lockits/russian").objects:
    if o.type.name == "MonoBehaviour":
        try: n = o.read().m_Name
        except Exception: continue
        if n.startswith(("GeneralLockit", "DialoguesLockit")):
            for t in o.read_typetree()["mSource"]["mTerms"]: ru[t["Term"]] = t["Languages"][0] if t["Languages"] else ""
G = {
 "Titus Hardie → Тітус Харді": r"Titus|Hardie",
 "Scab Leader → лідер антистрайкарів": r"scab.{0,12}lead|lead\w* of the scab",
 "Eugene → Євген": r"Eugene",
 "The Pigs → Мусор(а)": r"pigs?\b",
 "Prybar → Ломик": r"pry ?bar|crowbar",
 "Perception → Сприйняття": r"Perception",
}
cl = lambda s, n=260: s.replace("\n", " ").replace("|", "/")[:n]
L = ["# Рішення щодо термінів: що змінилося (2026-10-15)\n",
     f"Усього змінено термів: **{len(rows)}**. Копія: `work/patched/lockits/german_final` (у гру не встановлено). Лог: `work/glossary/decisions_changes.tsv`.\n"]
used = set()
for title, pat in G.items():
    ks = [r for r in rows if re.search(pat, en.get(r[0], ""), re.I) and r[0] not in used]
    used |= {r[0] for r in ks}
    L.append(f"## {title}: {len(ks)} термів\n")
    names = [r for r in ks if r[0].endswith(("/Name", "/DisplayName"))]
    for r in names: L.append(f"- Назва `{r[0]}`: {r[1]} → **{r[2]}**")
    L.append("")
    seen = set(); k = 0
    for r in ks:
        if r[0] in {x[0] for x in names} or k >= 6: continue
        key = r[2][:40]
        if key in seen: continue
        seen.add(key); k += 1
        L.append(f"**`{r[0]}`**\n- EN: {cl(en.get(r[0],''))}\n- RU: {cl(ru.get(r[0],''))}\n- UA було: {cl(r[1])}\n- UA стало: {cl(r[2])}\n")
L += ["## Примітки\n",
 "- «The Pigs»: назва актора = **Мусора** (за твоїм рішенням). У діалогах, де це звертання до однієї особи («патрульний Смітник»), вживаю однину **Мусор** (Мусора, Мусором, Мусоре), бо «патрульний Мусора» граматично невірно. Якщо хочеш скрізь «Мусора», скажи.",
 "- «Prybar»: за даними в діалогах більшість рядків уживала **лом** (≈49), а «ломик» ≈10 і «монтування» ≈9, тобто Haiku помилився у примітці. Я уніфікував усе до **ломик/ломика/ломиком…**, як ти погодив; прикметники узгоджено вручну в 3 фразах («непогана монтування» → «непоганий ломик» тощо).",
 "- «Perception»: у `resources.assets` (підписи навичок на листі персонажа) уже «Сприйняття»; змінено лише 2 рядки в lockit, де було «Увага» і «Відчуття».",
 "- «Тітус»: відмінкові форми Тіт/Тит → Тітус, Тіта/Тита → Тітуса, Тіту/Титу → Тітусу, Тітом/Титом → Тітусом, Тіте/Тите → Тітусе; Гарді → Харді (лише в рядках, де EN містить Titus/Hardie)."]
open("docs/glossary_decisions.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(L))
