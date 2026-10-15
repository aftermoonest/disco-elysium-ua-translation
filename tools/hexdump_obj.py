import sys, UnityPy
env = UnityPy.load(sys.argv[1])
for o in env.objects:
    if o.path_id in (3005,3010):
        r=o.get_raw_data()
        print(o.path_id,len(r), 'typetree:', bool(o.serialized_type.nodes) if o.serialized_type else None)
        for i in range(0,min(len(r),260),16):
            print('%04x'%i, r[i:i+16].hex(' '), ''.join(chr(b) if 32<=b<127 else '.' for b in r[i:i+16]))
