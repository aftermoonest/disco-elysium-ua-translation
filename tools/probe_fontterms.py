import sys, UnityPy, collections
sys.stdout.reconfigure(encoding='utf-8')
for b in sys.argv[1:]:
    env=UnityPy.load(b)
    for o in env.objects:
        if o.type.name=="MonoBehaviour":
            r=o.read()
            if 'Lockit' in r.m_Name and 'Dialogues' not in r.m_Name:
                tt=o.read_typetree(); ms=tt['mSource']
                c=collections.Counter(t['TermType'] for t in ms['mTerms'])
                print(b.split('\\')[-1], r.m_Name, dict(c))
                for t in ms['mTerms']:
                    if 'SDF' in t['Term'] or t['TermType'] in (3,4,6,7,8,9,10):
                        print('   ', t['TermType'], t['Term'], t['Languages'][:2], t['Flags'][:2] if t.get('Flags') else '')
