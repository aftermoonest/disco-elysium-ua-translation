import sys, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
d={}
env=UnityPy.load(r"Disco Elysium  Ukrainian translation\lockits\german")
for o in env.objects:
    if o.type.name=="MonoBehaviour" and o.read().m_Name=="GeneralLockitGerman":
        d={t['Term']:t['Languages'][0] for t in o.read_typetree()['mSource']['mTerms']}
env=UnityPy.load(r"Disco Elysium  Ukrainian translation\fonts\english")
have=set()
for o in env.objects:
    if o.type.name=="MonoBehaviour":
        try: tt=o.read_typetree()
        except: continue
        if tt.get('m_Name')=="CoreSansES Light SDF": have={chr(c['m_Unicode']) for c in tt['m_CharacterTable']}
terms=["HUD_DAY","Buttons/PAWNSHOP_BUTTON_CLOSE_TEXT","HUD_JOURNAL_ABBREVIATION","HUD_CHARSHEET_ABBREVIATION","HUD_INVENTORY_ABBREVIATION","HUD_CABINET_ABBREVIATION"]
for t in terms:
    v=d.get(t); miss=sorted({c for c in (v or '') if c not in have and not c.isspace()})
    print(t, repr(v), 'missing:', ''.join(miss) or '-')
print('Cyrillic in font:', ''.join(sorted(c for c in have if '\u0400'<=c<='\u04ff')))
print('basic latin count', sum(1 for c in have if c<'\u0080'))
