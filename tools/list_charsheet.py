import sys, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
env = UnityPy.load(sys.argv[1])
for o in env.objects:
    if o.type.name=="MonoBehaviour":
        r=o.get_raw_data()
        i=r.find(b'Charsheet')
        if i>=0 and o.byte_size<20000:
            print(o.path_id,o.byte_size,r[i:i+60].split(b'\x00')[0].decode('utf-8','replace'))
