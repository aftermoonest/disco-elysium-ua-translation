import sys, json, UnityPy
sys.stdout.reconfigure(encoding='utf-8')

def terms_of(bundle):
    env = UnityPy.load(bundle)
    for o in env.objects:
        if o.type.name=="MonoBehaviour":
            r=o.read()
            if r.m_Name=="GeneralLockitGerman":
                return {t['Term']: t['Languages'] for t in o.read_typetree()['mSource']['mTerms']}

orig = terms_of(r"work\original\AssetBundles\lockits\german")
mod = terms_of(r"Disco Elysium  Ukrainian translation\lockits\german")
print(len(orig), len(mod))

k="Actors/0x010000040000076B/Name"
print(repr(orig.get(k)), repr(mod.get(k)))
print([t for t in orig if 'Actors/' in t][:3])
