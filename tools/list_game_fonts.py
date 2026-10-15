import sys, struct, glob, os, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
root = sys.argv[1]
files = [os.path.join(root,'resources.assets'), os.path.join(root,'globalgamemanagers.assets')] + sorted(glob.glob(os.path.join(root,'sharedassets*.assets')))
seen = {}
for f in files:
    try: env = UnityPy.load(f)
    except Exception as e: print('skip', f, e); continue
    for o in env.objects:
        if o.type.name in ("MonoBehaviour","Font"):
            raw = o.get_raw_data() if o.byte_size < 3_000_000 else None
            if raw is None: continue
            try:
                n = struct.unpack_from('<i', raw, 28)[0]
                name = raw[32:32+n].decode('utf-8') if 0 < n < 100 else ''
            except Exception: continue
            if o.type.name == "Font" or name.endswith(' SDF') or 'SDF' in name:
                print(os.path.basename(f), o.type.name, o.path_id, repr(name), o.byte_size)
