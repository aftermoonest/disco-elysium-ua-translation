import sys, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
env=UnityPy.load(r"Disco Elysium  Ukrainian translation\fonts\english")
for o in env.objects:
    if o.type.name=="MonoBehaviour":
        try: tt=o.read_typetree()
        except: continue
        if tt.get('m_Name')=="CoreSansES Light SDF":
            ct=tt['m_CharacterTable']
            print(ct[0]); 
            for u in "Iiİ\u00cf\u00ef\u0406\u0456":
                print(repr(u), hex(ord(u)), [c for c in ct if c['m_Unicode']==ord(u)])
            print([k for k in tt.keys()][:30])
for b in ("Disco Elysium  Ukrainian translation\\lockits\\german","work\\original\\AssetBundles\\lockits\\russian"):
    e=UnityPy.load(b)
    for o in e.objects:
        if o.type.name=="MonoBehaviour" and o.read().m_Name.startswith("GeneralLockit"):
            for t in o.read_typetree()['mSource']['mTerms']:
                if t['Term']=="Buttons/PAWNSHOP_BUTTON_CLOSE_TEXT": print(b.split('\\')[-1], repr(t['Languages'][0]))
