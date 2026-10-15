import sys, re, UnityPy
sys.stdout.reconfigure(encoding='utf-8-sig')
exec(open('tools/parse_labels.py', encoding='utf-8-sig').read().split("env = UnityPy.load")[0])

def terms_of(bundle, name):
    env = UnityPy.load(bundle)
    for o in env.objects:
        if o.type.name == "MonoBehaviour" and o.read().m_Name == name:
            return {t['Term']: (t['Languages'][0] if t['Languages'] else '') for t in o.read_typetree()['mSource']['mTerms']}

ru = terms_of(r"work\original\AssetBundles\lockits\russian", "GeneralLockitRussian")
ua = terms_of(r"Disco Elysium  Ukrainian translation\lockits\german", "GeneralLockitGerman")
norm = lambda s: re.sub(r'[\s\-]', '', s).lower()
env = UnityPy.load(sys.argv[1])
for o in env.objects:
    if o.path_id == 3010:
        _, ents, _ = parse_labels(o.get_raw_data())
for eid, text, fl in ents:
    hits = [t for t, v in ru.items() if t.startswith('Actors/') and t.endswith('/Name') and norm(v) == norm(text)]
    print(eid, repr(text), hits, [ua.get(h) for h in hits])

