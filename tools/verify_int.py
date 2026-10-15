import sys, UnityPy, struct
env=UnityPy.load(sys.argv[1])
o=next(o for o in env.objects if o.path_id==25140); r=o.get_raw_data(); print(struct.unpack_from('<iq',r,0x8c), len(env.objects))
