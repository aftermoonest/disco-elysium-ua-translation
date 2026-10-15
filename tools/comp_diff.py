import sys, struct, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
env=UnityPy.load(sys.argv[1])
targets={2950:'INT',1959:'PSY'}
objs={o.path_id:o for o in env.objects}
for o in env.objects:
    if o.type.name=="MonoBehaviour":
        raw=o.get_raw_data()
        if len(raw)<16: continue
        fid,pid=struct.unpack_from('<iq',raw,0)
        if pid in targets:
            print(targets[pid],'MB',o.path_id,len(raw))
            if len(raw)>400:
                # list PPtr-looking pairs
                import re
                text=re.findall(rb'[\x20-\x7e]{3,}',raw)[:5]
                print('   strings',[t.decode() for t in text])
                ps=[]
                for i in range(0,len(raw)-12,4):
                    f,p=struct.unpack_from('<iq',raw,i)
                    if f in (0,1,2,3) and p in objs and p!=pid: ps.append((i,f,p,objs[p].type.name))
                print('   pptrs',ps[:12])
