"""Build the installer package (patches + data files) from the snapshot of the modded game.

Usage: python -I tools/build_package.py [snapshot dir] [--version X.Y.Z]

Output (git-ignored):
  dist/DiscoElysium_UA_installer/installer.py
  dist/DiscoElysium_UA_installer/package/manifest.json
  dist/DiscoElysium_UA_installer/package/patches/*.bsdiff   (game files: original -> modded)
  dist/DiscoElysium_UA_installer/package/data/...           (our own bundles, copied as they are)
  dist/DiscoElysium_UA_installer_v<version>.zip

"Original" versions of the patched game files come from work/backup/ (taken from an untouched game).
Every patch is re-applied here with the installer's own pure-Python bspatch and verified by SHA-256.
"""
import hashlib
import importlib.util
import json
import shutil
import sys
import zipfile
from pathlib import Path

import bsdiff4

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
BACKUP = ROOT / "work" / "backup"
B = "StreamingAssets/AssetBundles/Windows/"

# (path relative to disco_Data, kind, original source)
FILES = [
    ("resources.assets", "patch", BACKUP / "resources.assets"),
    ("level0", "patch", BACKUP / "level" / "level0"),
    ("level2", "patch", BACKUP / "level2"),
    ("il2cpp_data/Metadata/global-metadata.dat", "patch", BACKUP / "metadata" / "global-metadata.dat"),
    (B + "collage/shared", "patch", BACKUP / "collage" / "shared"),
    (B + "lockits/german", "replace", None),
    (B + "images/german", "replace", None),
    (B + "fonts/english", "replace", None),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load_installer():
    spec = importlib.util.spec_from_file_location("installer", ROOT / "installer" / "installer.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    version = "0.1.0"
    if "--version" in sys.argv:
        version = sys.argv[sys.argv.index("--version") + 1]
        args = [a for a in args if a != version]
    snaps = sorted((ROOT / "work" / "snapshot").iterdir())
    snap = Path(args[0]) if args else snaps[-1]
    print("snapshot:", snap, "| version:", version)
    inst = load_installer()

    out = ROOT / "dist" / "DiscoElysium_UA_installer"
    if out.exists():
        shutil.rmtree(out)
    (out / "package" / "patches").mkdir(parents=True)
    (out / "package" / "data").mkdir(parents=True)
    shutil.copy2(ROOT / "installer" / "installer.py", out / "installer.py")

    files = []
    for rel, kind, orig_path in FILES:
        new = (snap / rel).read_bytes()
        entry = {"path": rel, "kind": kind, "new": sha(new), "size": len(new)}
        if kind == "patch":
            old = orig_path.read_bytes()
            patch = bsdiff4.diff(old, new)
            pname = "patches/" + rel.replace("/", "__") + ".bsdiff"
            (out / "package" / pname).write_bytes(patch)
            assert inst.bspatch(old, patch) == new, f"pure-Python bspatch mismatch for {rel}"
            entry.update(orig=sha(old), orig_size=len(old), patch=pname)
            print(f"  patch   {rel:60} {len(old):>11,} -> {len(new):>11,}  patch {len(patch):>8,} B  (verified)")
        else:
            dname = "data/" + rel
            (out / "package" / dname).parent.mkdir(parents=True, exist_ok=True)
            (out / "package" / dname).write_bytes(new)
            entry["data"] = dname
            print(f"  replace {rel:60} {len(new):>11,} B")
        files.append(entry)

    manifest = {"mod_version": version, "game": "Disco Elysium",
                "variants": [{"id": "windows-steam-final-cut", "data_dirs": ["disco_Data"], "files": files}]}
    (out / "package" / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    zpath = ROOT / "dist" / f"DiscoElysium_UA_installer_v{version}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_LZMA) as z:
        for p in sorted(out.rglob("*")):
            if p.is_file():
                z.write(p, Path("DiscoElysium_UA_installer") / p.relative_to(out))
    total = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    print(f"package dir {total / 1e6:.1f} MB -> {zpath.name} {zpath.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
