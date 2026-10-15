import sys, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
def load(b):
    env=UnityPy.load(b); out={}
    for o in env.objects:
        if o.type.name=="MonoBehaviour":
            try: d=o.read()
            except Exception: continue
            if d.m_Name.startswith("GeneralLockit"):
                for t in o.read_typetree()['mSource']['mTerms']:
                    out[t['Term']]=t['Languages'][0] if t['Languages'] else ''
    return out
ua=load(r"Disco Elysium  Ukrainian translation\lockits\german")
ru=load(r"work\original\AssetBundles\lockits\russian")
mx=int(sys.argv[1]) if len(sys.argv)>1 else 12
for k,v in ua.items():
    if len(v)<=mx and v.strip() and k.split('/')[0] in ('Buttons','HUD','Inventory','Charsheet','Character','Journal','Cabinet','Interface','Stats','Tabs') or 'ABBREV' in k:
        print(k,'|',repr(v),'| ru:',repr(ru.get(k)))
