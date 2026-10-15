"""Build the Ukrainian game files for the macOS Steam build from the user's own Mac originals.

Usage (run on the Mac, from a clone of this repo, in a venv with UnityPy installed):
    python -I tools/build_mac_files.py [--game DIR] [--pkg DIR] [--out DIR]
    python -I tools/build_mac_files.py --install    # back up the originals, then copy the built files into the game
    python -I tools/build_mac_files.py --restore    # put the backed-up originals back

--game  Disco Elysium folder (default: the Steam path under ~/Library/Application Support)
--pkg   the `package` folder of the Windows installer zip (its data/ holds our bundles). Default: ~/Downloads/DiscoElysium_UA_installer/package
--out   default: work/mac_build

Game files are re-patched from the Mac originals with the same tools as on Windows (each asserts the bytes it expects);
the three translation bundles are taken from the Windows package as they are. The game folder is only written by
--install / --restore, and --install always makes a backup first (Steam "Verify integrity of game files" also restores it).
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
B_WIN, B_MAC = "StreamingAssets/AssetBundles/Windows/", "StreamingAssets/AssetBundles/OSX/"
GAME_FILES = ["resources.assets", "level0", "level2", "il2cpp_data/Metadata/global-metadata.dat", B_MAC + "collage/shared"]
BUNDLES = ["lockits/german", "images/german", "fonts/english"]


def opt(name, default):
    return Path(sys.argv[sys.argv.index(name) + 1]).expanduser() if name in sys.argv else default


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(script, *args):
    print("  $", Path(script).name, *[Path(str(a)).name for a in args])
    subprocess.run([sys.executable, "-I", str(script), *map(str, args)], check=True)


def data_dir(game):
    d = game / "disco.app/Contents/Resources/Data"
    if not d.is_dir():
        sys.exit(f"Data folder not found: {d}")
    return d


def main():
    game = opt("--game", Path("~/Library/Application Support/Steam/steamapps/common/Disco Elysium").expanduser())
    pkg = opt("--pkg", Path("~/Downloads/DiscoElysium_UA_installer/package").expanduser())
    out = opt("--out", ROOT / "work" / "mac_build")
    data = data_dir(game)
    files = out / "files"
    backup = out / "originals"

    if "--restore" in sys.argv:
        for rel in GAME_FILES + [B_MAC + b for b in BUNDLES]:
            if (backup / rel).is_file():
                shutil.copy2(backup / rel, data / rel)
                print("restored", rel)
        return 0

    try:
        import UnityPy  # noqa: F401
    except ImportError:
        sys.exit("UnityPy is missing: python3 -m venv .venv && .venv/bin/pip install UnityPy, then run with .venv/bin/python")
    for b in BUNDLES:
        if not (pkg / "data" / (B_WIN + b)).is_file():
            sys.exit(f"missing {pkg / 'data' / (B_WIN + b)} (pass --pkg <installer>/package)")

    shutil.rmtree(files, ignore_errors=True)
    for rel in GAME_FILES:
        (files / rel).parent.mkdir(parents=True, exist_ok=True)
    ab = data / B_MAC.rstrip("/")
    mod_lockit = pkg / "data" / (B_WIN + "lockits/german")
    translations = ROOT / "work" / "collage_ua.json"

    print("1/6 resources.assets (skill labels)")
    run(TOOLS / "patch_skill_labels.py", data / "resources.assets", files / "resources.assets",
        ab / "lockits/russian", mod_lockit)
    print("2/6 level0 (splash font size)")
    run(TOOLS / "patch_splash_fontsize.py", data / "level0", files / "level0", "80")
    print("3/6 level2 (INTELLECT label)")
    run(TOOLS / "patch_int_label.py", data / "level2", files / "level2")
    print("4/6 global-metadata.dat (loading text)")
    run(TOOLS / "patch_metadata_literal.py", data / "il2cpp_data/Metadata/global-metadata.dat",
        files / "il2cpp_data/Metadata/global-metadata.dat", "WIRD GELADEN", "ЗАВАНТАЖЕННЯ")
    print("5/6 collage/shared")
    run(TOOLS / "collage_translations.py")
    run(TOOLS / "patch_collage_lockit.py", ab / "collage/shared", translations, files / B_MAC / "collage/shared")
    print("6/6 translation bundles (from the Windows package)")
    for b in BUNDLES:
        dst = files / B_MAC / b
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pkg / "data" / (B_WIN + b), dst)

    report = {}
    for rel in GAME_FILES + [B_MAC + b for b in BUNDLES]:
        report[rel] = {"orig": sha(data / rel), "new": sha(files / rel), "size": (files / rel).stat().st_size}
    (out / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("\nBuilt into", files)
    for rel, r in report.items():
        print(f"  {rel:60} {r['size']:>11,}  changed={r['orig'] != r['new']}")

    if "--install" in sys.argv:
        print("\nInstalling (originals are backed up to", backup, ")")
        for rel in report:
            (backup / rel).parent.mkdir(parents=True, exist_ok=True)
            if not (backup / rel).exists():  # never overwrite the first backup with a patched file
                shutil.copy2(data / rel, backup / rel)
            shutil.copy2(files / rel, data / rel)
            print("  installed", rel)
        print("Done. Start the game and pick Deutsch. To undo: --restore (or Steam: Verify integrity).")
    else:
        print("\nNothing was changed in the game. Add --install to install (with backup).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
