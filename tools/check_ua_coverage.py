import sys, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
UA = set("АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя'’")
for b in sys.argv[1:]:
    env = UnityPy.load(b)
    for o in env.objects:
        if o.type.name=="MonoBehaviour":
            try: tt=o.read_typetree()
            except: continue
            if 'm_CharacterTable' not in tt: continue
            have={chr(c['m_Unicode']) for c in tt['m_CharacterTable']}
            miss=''.join(sorted(UA-have))
            fb=len(tt.get('fallbackFontAssetTable') or [])
            print(f"{tt['m_Name']:34} missing UA: {miss or '-':20} fallbacks={fb}")
