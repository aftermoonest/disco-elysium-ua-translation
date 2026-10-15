import sys, UnityPy
env=UnityPy.load(sys.argv[1])
for o in env.objects:
    if o.path_id in (25140,26594):
        r=o.get_raw_data(); print(o.path_id,len(r))
        for i in range(0,len(r),16): print('%03x'%i, r[i:i+16].hex(' '), ''.join(chr(b) if 32<=b<127 else '.' for b in r[i:i+16]))
