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
# German skill labels from resources.assets
labels = ["LOGIK","ENZYKLOPÄDIE","RHETORIK","SCHAUSPIELKUNST","KONZEPTBILDUNG","VISUELLES KALKÜL","WILLENSKRAFT","INNENLEBEN","EMPATHIE","AUTORITÄT","KORPSGEIST","SUGGESTION","AUSDAUER","SCHMERZGRENZE","KÖRPERAPPARAT","ELEKTROCHEMIE","SCHAUDER","ZWIELICHT","AUGE-HAND-KOORDINATION","WAHRNEHMUNG","REAKTIONSVERMÖGEN","GEWANDTHEIT","MECHANIK","BEHERRSCHUNG"]
for lab in labels:
    key = lab.replace("-","-").lower()
    hits=[t for t,l in orig.items() if t.startswith("Actors/") and t.endswith("/Name") and l and l[0] and l[0].lower().replace("\n"," ")==key]
    print(lab, hits[:2], [mod[h][0] if h in mod else None for h in hits[:2]])
