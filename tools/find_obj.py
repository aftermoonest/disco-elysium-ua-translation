import sys, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
env=UnityPy.load(sys.argv[1]); needle=sys.argv[2].encode()
for o in env.objects:
    raw=o.get_raw_data()
    if needle in raw:
        print(o.type.name, o.path_id, len(raw))
        print(''.join(chr(b) if 32<=b<127 else '.' for b in raw[:400]))
        print('---')
