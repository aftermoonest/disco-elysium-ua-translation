import sys, re, UnityPy
sys.stdout.reconfigure(encoding='utf-8')
env=UnityPy.load(sys.argv[1])
for o in env.objects:
    if o.type.name!="MonoBehaviour" or o.byte_size>600: continue
    raw=o.get_raw_data()
    m=re.search(rb'Abilities/ABILITY_NAME_(INT|PSY|PHY|MOT)|Actors/0x0100005[0-9A-F]+/Name',raw)
    if m:
        strs=re.findall(rb'[\x20-\x7e]{4,}',raw)
        print(o.path_id, o.byte_size, [s.decode() for s in strs][:6])
