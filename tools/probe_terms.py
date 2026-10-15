import sys, UnityPy, collections
sys.stdout.reconfigure(encoding='utf-8')
env = UnityPy.load(sys.argv[1])
for o in env.objects:
    if o.type.name=="MonoBehaviour":
        r=o.read()
        if r.m_Name in ("GeneralLockitRussian","GeneralLockitGerman","ImagesLockitRussian","ImagesLockitGerman"):
            tt=o.read_typetree(); ms=tt['mSource']
            print(r.m_Name, 'langs', [l['Name'] for l in ms['mLanguages']], 'terms', len(ms['mTerms']))
            c=collections.Counter(t['TermType'] for t in ms['mTerms']); print(' types', dict(c))
            for t in ms['mTerms']:
                if t['TermType']!=0 or 'ont' in t['Term']:
                    print('  ', t['TermType'], t['Term'], t['Languages'][:1], t.get('Flags'))
                    
