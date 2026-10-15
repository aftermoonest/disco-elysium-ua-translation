import sys, struct, UnityPy
env=UnityPy.load(sys.argv[1])
d={}
for o in env.objects:
    if o.path_id in (19446,19784): d[o.path_id]=o.get_raw_data()
for pid,r in d.items():
    print(pid,len(r))
    for i in range(0,len(r),16): print('%03x'%i, r[i:i+16].hex(' '), ''.join(chr(b) if 32<=b<127 else '.' for b in r[i:i+16]))
