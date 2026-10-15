import sys, re, struct, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
env=UnityPy.load(sys.argv[1]); objs={o.path_id:o for o in env.objects}
gos={}
for o in env.objects:
    r=o.get_raw_data()
    if b'GulimChe' in r and o.type.name=="MonoBehaviour":
        strs=[s.decode() for s in re.findall(rb'[\x20-\x7e]{4,}',r)][:4]
        fid,gid=struct.unpack_from('<iq',r,0)
        print('Localize',o.path_id,'GO',gid,strs)
        # find sibling TMP text on same GameObject
        for p,q in objs.items():
            if q.type.name=="MonoBehaviour" and q.byte_size>300:
                rr=q.get_raw_data()
                if struct.unpack_from('<iq',rr,0)[1]==gid:
                    t=re.findall(rb'[\x20-\x7e]{3,}',rr)[:3]
                    print('   TMP',p,[x.decode() for x in t])
        # GameObject name
        go=objs.get(gid)
        if go: 
            try: print('   GO name', go.read().m_Name)
            except Exception as e: print('   GO?',e)
