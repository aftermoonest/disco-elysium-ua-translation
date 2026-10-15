"""Build the installer package (patches + data files) from the snapshot of the modded game.

Usage: python -I tools/build_package.py [snapshot dir] [--version X.Y.Z] [--dist DIR] [--exe path\to\installer.exe]

Output (git-ignored), DIR defaults to dist:
  DIR/DiscoElysium_UA_installer/installer.py, README.uk.md, README.en.md
  DIR/DiscoElysium_UA_installer/package/manifest.json
  DIR/DiscoElysium_UA_installer/package/patches/*.bsdiff   (game files: original -> modded)
  DIR/DiscoElysium_UA_installer/package/data/...           (our own bundles, copied as they are)
  DIR/DiscoElysium_UA_installer_v<version>_python.zip      (Mac / Linux / Steam Deck / any OS with Python 3)
  DIR/DiscoElysium_UA_installer_v<version>_windows.zip     (only with --exe: the .exe + package + READMEs)

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


B_MAC = "StreamingAssets/AssetBundles/OSX/"
MAC_DIR = ROOT / "work" / "mac_build"  # made on a Mac by tools/build_mac_files.py (+ --install, which keeps work/mac_build/originals)
MAC_PATCHES = ["resources.assets", "level0", "level2", "il2cpp_data/Metadata/global-metadata.dat", B_MAC + "collage/shared"]
MAC_BUNDLES = ["lockits/german", "images/german", "fonts/english"]  # byte-identical to the Windows bundles


def sha(b):
    return hashlib.sha256(b).hexdigest()


def mac_variant(out, win_files, inst):
    """Variant for the macOS Steam build: bsdiff patches from the Mac originals; the three bundles reuse the Windows data files."""
    report = json.loads((MAC_DIR / "report.json").read_text(encoding="utf-8"))
    by_path = {f["path"]: f for f in win_files}
    files = []
    for rel in MAC_PATCHES:
        old, new = (MAC_DIR / "originals" / rel).read_bytes(), (MAC_DIR / "files" / rel).read_bytes()
        assert sha(old) == report[rel]["orig"] and sha(new) == report[rel]["new"], f"mac_build/{rel} does not match report.json"
        patch = bsdiff4.diff(old, new)
        pname = "patches/mac__" + rel.replace("/", "__") + ".bsdiff"
        (out / "package" / pname).write_bytes(patch)
        assert inst.bspatch(old, patch) == new, f"pure-Python bspatch mismatch for mac {rel}"
        files.append({"path": rel, "kind": "patch", "new": sha(new), "size": len(new), "orig": sha(old), "orig_size": len(old), "patch": pname})
        print(f"  mac patch {rel:56} {len(old):>11,} -> {len(new):>11,}  patch {len(patch):>8,} B  (verified)")
    for b in MAC_BUNDLES:
        w = by_path[B + b]
        assert sha((MAC_DIR / "files" / (B_MAC + b)).read_bytes()) == w["new"], f"mac bundle {b} differs from the Windows one"
        files.append({"path": B_MAC + b, "kind": "replace", "new": w["new"], "size": w["size"], "data": w["data"]})
        print(f"  mac replace {B_MAC + b:54} shares {w['data']}")
    return {"id": "macos-steam-final-cut", "data_dirs": ["disco.app/Contents/Resources/Data"], "files": files}


def load_installer():
    spec = importlib.util.spec_from_file_location("installer", ROOT / "installer" / "installer.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def opt(name, default=None):
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return default


def main():
    version = opt("--version", "1.0")
    dist = ROOT / opt("--dist", "dist")
    exe = opt("--exe")
    skip = {version, opt("--dist"), exe, "--version", "--dist", "--exe"}
    args = [a for a in sys.argv[1:] if a not in skip]
    snaps = sorted((ROOT / "work" / "snapshot").iterdir())
    snap = Path(args[0]) if args else snaps[-1]
    print("snapshot:", snap, "| version:", version)
    inst = load_installer()

    out = dist / "DiscoElysium_UA_installer"
    if out.exists():
        shutil.rmtree(out)
    (out / "package" / "patches").mkdir(parents=True)
    (out / "package" / "data").mkdir(parents=True)
    for name in ("installer.py", "README.uk.md", "README.en.md"):
        shutil.copy2(ROOT / "installer" / name, out / name)

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

    variants = [{"id": "windows-steam-final-cut", "data_dirs": ["disco_Data"], "files": files}]
    if (MAC_DIR / "report.json").exists():
        variants.append(mac_variant(out, files, inst))
    else:
        print("!! work/mac_build/report.json not found: building WITHOUT the macOS variant")
    manifest = {"mod_version": version, "game": "Disco Elysium", "variants": variants}
    (out / "package" / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    def make_zip(path, extra, skip_names=()):
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for p in sorted(out.rglob("*")):
                if p.is_file() and p.name not in skip_names:
                    z.write(p, Path("DiscoElysium_UA_installer") / p.relative_to(out))
            for src, arc in extra:
                z.write(src, Path("DiscoElysium_UA_installer") / arc)
        print(f"{path.name}: {path.stat().st_size / 1e6:.1f} MB")

    total = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    print(f"package dir {total / 1e6:.1f} MB")
    make_zip(dist / f"DiscoElysium_UA_installer_v{version}_python.zip", [])
    if exe:
        make_zip(dist / f"DiscoElysium_UA_installer_v{version}_windows.zip", [(Path(exe), "DiscoElysium_UA_installer.exe")], skip_names=("installer.py",))


if __name__ == "__main__":
    main()
