"""Synthetic end-to-end test of the Windows + macOS variants (tiny fake files, no real game data needed).

Usage: python -I tools/test_installer_mac.py        (needs bsdiff4: pip install bsdiff4)
Builds a package with tools/build_package.py from random "game" files, then runs installer/installer.py in text mode against a
fake Windows game and a fake macOS game (disco.app/Contents/Resources/Data, AssetBundles/OSX): install, re-install, remove,
tampered original. Also checks the macOS Tk guard. Uses a temp folder only.
"""
import hashlib
import importlib.util
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parent.parent
fails = []


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{extra}]" if extra and not cond else ""))
    if not cond:
        fails.append(name)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def blob(seed, n):
    return random.Random(seed).randbytes(n)


def mutate(b, seed):
    r = random.Random(seed)
    b = bytearray(b)
    for _ in range(20):
        b[r.randrange(len(b))] ^= 0xFF
    return bytes(b + blob(seed, 40))  # also longer, like the real patches


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


tmp = Path(tempfile.mkdtemp(prefix="ua_mac_test_"))
try:
    B, BM = "StreamingAssets/AssetBundles/Windows/", "StreamingAssets/AssetBundles/OSX/"
    PATCH = ["resources.assets", "level0", "level2", "il2cpp_data/Metadata/global-metadata.dat"]
    BUNDLES = ["lockits/german", "images/german", "fonts/english"]
    # "repo" root for build_package: installer files + work/
    root = tmp / "repo"
    shutil.copytree(REPO / "installer", root / "installer")
    work = root / "work"
    win_orig, win_new, mac_orig, mac_new = {}, {}, {}, {}
    for i, rel in enumerate(PATCH + [B + "collage/shared"]):
        win_orig[rel] = blob(i, 5000)
        win_new[rel] = mutate(win_orig[rel], 100 + i)
    for i, rel in enumerate(PATCH + [BM + "collage/shared"]):
        mac_orig[rel] = blob(500 + i, 6000)  # different bytes than Windows, like the real builds
        mac_new[rel] = mutate(mac_orig[rel], 600 + i)
    bundles = {b: blob(900 + i, 3000) for i, b in enumerate(BUNDLES)}
    snap = work / "snapshot" / "x"
    for rel, d in win_new.items():
        write(snap / rel, d)
    for b, d in bundles.items():
        write(snap / (B + b), d)
    for rel, d in mac_orig.items():
        write(work / "mac_build" / "originals" / rel, d)
        write(work / "mac_build" / "files" / rel, mac_new[rel])
    for b, d in bundles.items():
        write(work / "mac_build" / "files" / (BM + b), d)
    report = {rel: {"orig": hashlib.sha256(mac_orig[rel]).hexdigest(), "new": hashlib.sha256(mac_new[rel]).hexdigest()} for rel in mac_orig}
    write(work / "mac_build" / "report.json", json.dumps(report).encode())

    # --- build the package with the real build_package.py, pointed at the synthetic data
    spec = importlib.util.spec_from_file_location("build_package", REPO / "tools" / "build_package.py")
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
    bp.ROOT, bp.MAC_DIR = root, work / "mac_build"
    wo = {rel: write(work / "winorig" / rel, d) or work / "winorig" / rel for rel, d in win_orig.items()}
    bp.FILES = [(rel, "patch", wo[rel]) for rel in PATCH + [B + "collage/shared"]] + [(B + b, "replace", None) for b in BUNDLES]
    sys.argv = ["build_package.py", str(snap), "--version", "9.9", "--dist", "dist"]
    bp.main()
    pkg = root / "dist" / "DiscoElysium_UA_installer"
    man = json.loads((pkg / "package" / "manifest.json").read_text(encoding="utf-8"))
    ids = [v["id"] for v in man["variants"]]
    check("manifest has Windows and macOS variants", ids == ["windows-steam-final-cut", "macos-steam-final-cut"], ids)
    check("bundle data is shared, not duplicated", len(list((pkg / "package" / "data").rglob("*"))) and
          sum(1 for p in (pkg / "package" / "data").rglob("*") if p.is_file()) == 3)

    def run(game, *args):
        p = subprocess.run([sys.executable, "-I", str(pkg / "installer.py"), "--lang", "en", "--game", str(game),
                            "--skip-running-check", *args], capture_output=True, text=True, encoding="utf-8")
        return p.returncode, p.stdout + p.stderr

    # --- fake games
    mac_game = tmp / "Mac" / "Disco Elysium"
    mdata = mac_game / "disco.app/Contents/Resources/Data"
    for rel, d in mac_orig.items():
        write(mdata / rel, d)
    for b in BUNDLES:
        write(mdata / (BM + b), blob(7000 + len(b), 2000))  # the original German etc. bundles
    win_game = tmp / "Win" / "Disco Elysium"
    for rel, d in win_orig.items():
        write(win_game / "disco_Data" / rel, d)
    for b in BUNDLES:
        write(win_game / "disco_Data" / (B + b), blob(8000 + len(b), 2000))

    for name, game, data, newmap, bpath in (("macOS", mac_game, mdata, mac_new, BM), ("Windows", win_game, win_game / "disco_Data", win_new, B)):
        orig_state = {p.relative_to(data).as_posix(): sha(p) for p in data.rglob("*") if p.is_file()}
        rc, out = run(game, "--cli", "info")
        check(f"{name}: info says original", rc == 0 and "original files" in out, out)
        rc, out = run(game, "--cli", "install", "-y")
        check(f"{name}: install ok", rc == 0, out)
        check(f"{name}: patched files equal expected", all(sha(data / rel) == hashlib.sha256(d).hexdigest() for rel, d in newmap.items()), out)
        check(f"{name}: bundles replaced", all((data / (bpath + b)).read_bytes() == bundles[b] for b in BUNDLES), out)
        rc, out = run(game, "--cli", "install", "-y")
        check(f"{name}: re-install ok", rc == 0, out)
        rc, out = run(game, "--cli", "remove", "-y")
        check(f"{name}: remove restores every file byte-for-byte",
              rc == 0 and {p.relative_to(data).as_posix(): sha(p) for p in data.rglob("*") if p.is_file()} == orig_state, out)
        check(f"{name}: backup dir deleted", not (game / "_ua_backup").exists())

    # tampered Mac original is refused and nothing changes
    victim = mdata / "level2"
    d = bytearray(victim.read_bytes())
    d[10] ^= 0xFF
    victim.write_bytes(bytes(d))
    before = sha(victim)
    rc, out = run(mac_game, "--cli", "install", "-y")
    check("macOS: unknown version refused", rc != 0 and "Unknown game version" in out and sha(victim) == before, out)

    # Windows layout is not mistaken for macOS and vice versa
    rc, out = run(tmp / "nonexistent", "--cli", "info")
    check("missing folder reports no game", rc == 2, out)

    # --- Tk guard
    spec = importlib.util.spec_from_file_location("inst", pkg / "installer.py")
    inst = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inst)
    xcode = "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9"
    org = "/Library/Frameworks/Python.framework/Versions/3.13"
    cases = [("Darwin", "26.3", xcode, True),   # the user's Mac: Apple's Python on macOS 26
             ("Darwin", "26.3", "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9", True),
             ("Darwin", "16.0", org, True),     # compat-mode version report
             ("Darwin", "26.3", org, False),    # python.org Python on macOS 26: not guarded
             ("Darwin", "15.5", xcode, False), ("Windows", "", "C:/Python312", False), ("Linux", "", "/usr", False)]
    real_prefix, real_exe, real_realpath = inst.sys.base_prefix, inst.sys.executable, inst.os.path.realpath
    inst.os.path.realpath = lambda p: p
    for system, ver, prefix, expect in cases:
        inst.platform.system = lambda s=system: s
        inst.platform.mac_ver = lambda v=ver: (v, ("", "", ""), "arm64")
        inst.sys.base_prefix = prefix
        os.environ.pop("DISCO_UA_FORCE_GUI", None)
        check(f"tk guard {system} {ver or '-'} {Path(prefix).parts[-1] if prefix else '-'} -> {expect}", inst.tk_would_abort() is expect)
    inst.sys.base_prefix, inst.os.path.realpath = real_prefix, real_realpath
    inst.platform.system = lambda: "Darwin"
    inst.platform.mac_ver = lambda: ("16.0", ("", "", ""), "arm64")
    os.environ["DISCO_UA_FORCE_GUI"] = "1"
    check("tk guard override DISCO_UA_FORCE_GUI", inst.tk_would_abort() is False)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n%d failure(s)" % len(fails) if fails else "\nALL PASSED")
sys.exit(1 if fails else 0)
