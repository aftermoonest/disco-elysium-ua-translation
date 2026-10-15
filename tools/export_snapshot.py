r"""Snapshot the CURRENT modded state of the game into the project (read-only on the game folder).

1. Copies the mod's bundles and patched game files into work/snapshot/<date>/ (kept out of git) with a SHA-256 manifest.
2. Exports the Ukrainian text of lockits/german to translation/{general,dialogues}.tsv (committed): the source of truth.
   Columns: term <TAB> text, with \ \n \t escaped. Terms keep the order of the bundle.

Usage: python -I tools/export_snapshot.py [YYYY-MM-DD]
"""
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
GAME = Path(r"D:\Games\SteamLibrary\steamapps\common\Disco Elysium\disco_Data")
BUNDLES = "StreamingAssets/AssetBundles/Windows/"
FILES = [BUNDLES + "lockits/german", BUNDLES + "images/german", BUNDLES + "fonts/english", BUNDLES + "collage/shared",
         "resources.assets", "level0", "level2", "il2cpp_data/Metadata/global-metadata.dat"]


def esc(s):
    return s.replace("\\", "\\\\").replace("\n", "\n").replace("\r", "\r").replace("\t", "\t")


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    snap = ROOT / "work" / "snapshot" / tag
    manifest = {}
    for rel in FILES:
        src, dst = GAME / rel, snap / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        manifest[rel] = {"size": dst.stat().st_size, "sha256": hashlib.sha256(dst.read_bytes()).hexdigest()}
    (snap / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print("snapshot ->", snap)
    for rel, m in manifest.items():
        print(f"  {m['size']:>12,}  {m['sha256'][:12]}  {rel}")

    env = UnityPy.load(str(snap / BUNDLES / "lockits/german"))
    out = ROOT / "translation"
    out.mkdir(exist_ok=True)
    names = {"GeneralLockitGerman": "general.tsv", "DialoguesLockitGerman": "dialogues.tsv"}
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            n = o.read().m_Name
            if n in names:
                terms = o.read_typetree()["mSource"]["mTerms"]
                with open(out / names[n], "w", encoding="utf-8", newline="\n") as f:
                    for t in terms:
                        f.write(f"{t['Term']}\t{esc(t['Languages'][0] if t['Languages'] else '')}\n")
                print(f"  {names[n]}: {len(terms)} terms, {(out / names[n]).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
