import sys, struct, glob, os, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
root=sys.argv[1]
files=sorted(glob.glob(os.path.join(root,'level*')))+sorted(glob.glob(os.path.join(root,'sharedassets*.assets')))+[os.path.join(root,'resources.assets')]
for f in files:
    if f.endswith(('.resS','.resource')): continue
    try: env=UnityPy.load(f)
    except Exception: continue
    for o in env.objects:
        if o.type.name!="MonoBehaviour" or o.byte_size>700: continue
        r=o.get_raw_data()
        if b'LocalizeTarget_TextMeshPro' not in r: continue
        p=32+0
        try:
            p=32
            n=struct.unpack_from('<i',r,p-4)[0] if False else None
            # term string at 0x1c (len) after 28-byte header (name len at 0x20?)
            p=0x20; n=struct.unpack_from('<i',r,p)[0]; term=r[p+4:p+4+n].decode(); p+=4+(n+3)//4*4
            n2=struct.unpack_from('<i',r,p)[0]; sec=r[p+4:p+4+n2].decode(); p+=4+(n2+3)//4*4
            fid,pid=struct.unpack_from('<iq',r,p+0x3c-4+0) if False else (0,0)
            # scan ints after secondary for a PPtr to a font object (pid>1000, fid in 1..9)
            tail=[(i,struct.unpack_from('<iq',r,i)) for i in range(p,len(r)-12,4)]
            cand=[(i,v) for i,v in tail if v[0] in (1,2,3,4,5,6) and 100<v[1]<100000 and i>=p+0x20 and i<p+0x60]
        except Exception as e:
            continue
        if cand:
            print(os.path.basename(f), o.path_id, term, '|', sec, '|', cand[:2])
