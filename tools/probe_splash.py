"""Read-only: export default loading textures and show the ImagesLockit terms for load/save panels."""
import sys
from pathlib import Path
import UnityPy
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
D = Path(r"D:\Games\SteamLibrary\steamapps\common\Disco Elysium\disco_Data")
Path("work/export/splash").mkdir(parents=True, exist_ok=True)
for f, names in (("sharedassets1.assets", {"loading-panel"}), ("sharedassets0.assets", {"Splash", "LoadingCircle"})):
    env = UnityPy.load(str(D / f))
    for o in env.objects:
        if o.type.name == "Texture2D":
            d = o.read()
            if d.m_Name in names:
                im = d.image.convert("RGBA")
                bg = Image.new("RGBA", im.size, (60, 60, 60, 255))
                bg.alpha_composite(im)
                fn = f"work/export/splash/{f}_{d.m_Name}.png"
                bg.save(fn)
                print(fn, im.size)
env = UnityPy.load(str(D / "StreamingAssets/AssetBundles/Windows/lockits/german"))
for o in env.objects:
    if o.type.name == "MonoBehaviour" and o.read().m_Name == "ImagesLockitGerman":
        src = o.read_typetree()["mSource"]
        print("langs", [(l["Name"], l["Code"]) for l in src["mLanguages"]])
        for t in src["mTerms"]:
            if "LOAD" in t["Term"].upper() or "SAV" in t["Term"].upper():
                print(t["Term"], t["Languages"])
