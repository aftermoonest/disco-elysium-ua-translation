import sys, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
ua={}
for name,b in (("ua",r"Disco Elysium  Ukrainian translation\lockits\german"),("ru",r"work\original\AssetBundles\lockits\russian")):
    env=UnityPy.load(b)
    for o in env.objects:
        if o.type.name=="MonoBehaviour" and o.read().m_Name.startswith("GeneralLockit"):
            d={t['Term']:(t['Languages'][0] if t['Languages'] else '') for t in o.read_typetree()['mSource']['mTerms']}
            ua[name]=d
for k,v in ua['ua'].items():
    if v.strip().lower() in ("інтелект","інтелект ") or v.strip().lower().startswith("інтелект"):
        print(k, repr(v), '| ru:', repr(ua['ru'].get(k)))
