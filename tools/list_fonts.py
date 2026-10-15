import sys, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
for b in sys.argv[1:]:
    print("==", b)
    env = UnityPy.load(b)
    for o in env.objects:
        t = o.type.name
        if t in ("MonoBehaviour","Font","Texture2D","TextAsset"):
            try: r=o.read(); n=getattr(r,'m_Name',None)
            except Exception as e: n='?'
            extra=''
            if t=="MonoBehaviour":
                try:
                    tt=o.read_typetree()
                    ch=tt.get('m_CharacterTable') or []
                    extra=f"chars={len(ch)} glyphs={len(tt.get('m_GlyphTable') or [])}"
                    cyr=sum(1 for c in ch if 0x400<=c.get('m_Unicode',0)<=0x4FF)
                    extra+=f" cyrillic={cyr}"
                except Exception as e: extra='no typetree'
            print(t, o.path_id, n, o.byte_size, extra)
