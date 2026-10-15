import sys, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
env = UnityPy.load(sys.argv[1])
for o in env.objects:
    if o.path_id == 3005:
        raw = o.get_raw_data()
        print(raw.decode('utf-8','replace').replace('\x00','|')[:1500])
        try:
            print(o.read_typetree())
        except Exception as e: print('typetree fail', e)

