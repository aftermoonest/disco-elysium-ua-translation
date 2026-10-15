import sys, UnityPy
env = UnityPy.load(sys.argv[1])
names=[o.read().m_Name for o in env.objects if o.type.name in ("Texture2D","Sprite")]
print(len(names)); print([n for n in names if any(k in n.lower() for k in ("load","lade","wait","loading"))])
