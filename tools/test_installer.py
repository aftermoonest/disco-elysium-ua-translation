"""End-to-end tests of installer/installer.py on a throw-away COPY of the game layout (never the real game).

Usage: python -I tools/test_installer.py
Builds work/testgame/Disco Elysium/disco_Data from the ORIGINAL files (work/backup) + the previous mod bundles from
the release folder, then runs the installer in text mode against it.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / os.environ.get("UA_DIST", "dist")  # UA_DIST=dist_next to test another build
PKG = DIST / "DiscoElysium_UA_installer"
EXE = os.environ.get("UA_EXE")  # test a built .exe instead of installer.py
MAN = json.loads((PKG / "package" / "manifest.json").read_text(encoding="utf-8"))
FILES = MAN["variants"][0]["files"]
GAME = ROOT / "work" / os.environ.get("UA_TESTGAME", "testgame") / "Disco Elysium"
DATA = GAME / "disco_Data"
BACKUP = ROOT / "work" / "backup"
REL = ROOT / "Disco Elysium  Ukrainian translation"
B = "StreamingAssets/AssetBundles/Windows/"
PREVIOUS_MOD = {B + "lockits/german": REL / "lockits/german", B + "images/german": REL / "images/german", B + "fonts/english": REL / "fonts/english"}
ORIG_SRC = {"resources.assets": BACKUP / "resources.assets", "level0": BACKUP / "level/level0", "level2": BACKUP / "level2",
            "il2cpp_data/Metadata/global-metadata.dat": BACKUP / "metadata/global-metadata.dat", B + "collage/shared": BACKUP / "collage/shared"}

CMD = [EXE] if EXE else [sys.executable, "-I", str(PKG / "installer.py")]
fails = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{extra}]" if extra and not cond else ""))
    if not cond:
        fails.append(name)


def make_game():
    if GAME.parent.exists():
        shutil.rmtree(GAME.parent)
    for rel, src in {**ORIG_SRC, **PREVIOUS_MOD}.items():
        dst = DATA / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return {rel: sha(DATA / rel) for rel in {**ORIG_SRC, **PREVIOUS_MOD}}


def run(*args, expect_ok=True):
    p = subprocess.run([*CMD, "--lang", "en", "--game", str(GAME), "--skip-running-check", *args],
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout + p.stderr


def snapshot_state():
    return {f["path"]: sha(DATA / f["path"]) for f in FILES}


start = make_game()
print("test game:", GAME)

rc, out = run("--cli", "info")
check("info on original game says original", rc == 0 and "original files" in out, out)

before = snapshot_state()
rc, out = run("--cli", "install", "--dry-run")
check("dry-run changes nothing", snapshot_state() == before and not (GAME / "_ua_backup").exists(), out)
check("dry-run lists actions", "Patch:" in out and "Copy:" in out, out)

t0 = __import__("time").time()
rc, out = run("--cli", "install", "-y")
print(f"   install took {__import__('time').time() - t0:.1f}s")
check("install exit code 0", rc == 0, out)
check("all files equal the package hashes", all(sha(DATA / f["path"]) == f["new"] for f in FILES), out)
check("backup dir + install.json written", (GAME / "_ua_backup" / "install.json").exists())
check("originals backed up", all(sha(GAME / "_ua_backup" / p) == h for p, h in start.items()), "")
rc, out = run("--cli", "info")
check("info says installed", f"installed (version {MAN['mod_version']})" in out, out)

rc, out = run("--cli", "install", "-y")
check("re-install (update) works", rc == 0 and all(sha(DATA / f["path"]) == f["new"] for f in FILES), out)
check("backups still hold the ORIGINALS after re-install", all(sha(GAME / "_ua_backup" / p) == h for p, h in start.items()))

rc, out = run("--cli", "remove", "-y")
check("remove exit code 0", rc == 0, out)
check("remove restores every file byte-for-byte", snapshot_state() == {k: start[k] for k in snapshot_state()} or all(sha(DATA / p) == h for p, h in start.items()), out)
check("backup dir deleted", not (GAME / "_ua_backup").exists())
rc, out = run("--cli", "remove", "-y")
check("remove twice is harmless", rc == 0 and "not installed" in out, out)

# unknown game version: flip one byte in a patch-kind file
victim = DATA / "level2"
data = bytearray(victim.read_bytes())
data[1000] ^= 0xFF
victim.write_bytes(bytes(data))
tampered = snapshot_state()
rc, out = run("--cli", "install", "-y")
check("unknown version is refused", rc != 0 and "Unknown game version" in out, out)
check("refused install changed nothing", snapshot_state() == tampered)
shutil.copy2(BACKUP / "level2", victim)

# mod installed by hand / backup lost: must be explained, not treated as "unknown version", and must not be touched
run("--cli", "install", "-y")
shutil.rmtree(GAME / "_ua_backup")
installed_state = snapshot_state()
rc, out = run("--cli", "info")
check("no-backup case is explained", "no installer backup" in out, out)
rc, out = run("--cli", "install", "-y")
check("no-backup install refused, nothing changed", rc != 0 and "no installer backup" in out and snapshot_state() == installed_state, out)
make_game()

# wrong folder
rc, out = run("--cli", "info")
rc2 = subprocess.run([*CMD, "--lang", "uk", "--game", str(ROOT), "--cli", "info"],
                     capture_output=True, text=True, encoding="utf-8")
check("wrong folder reported (uk)", rc2.returncode == 2 and "не знайдено" in rc2.stdout, rc2.stdout)

# collect-info
rc, out = run("--cli", "collect-info")
check("collect-info prints hashes", rc == 0 and "sha256" in out and "level0" in out, out)

# crash safety: no *.ua_tmp left behind
leftovers = list(GAME.rglob("*.ua_tmp"))
check("no temp files left", not leftovers, str(leftovers))

# GUI smoke test (builds the window, runs one event-loop pass, closes)
code = ("import sys; sys.path.insert(0, r'%s'); import tkinter as tk, installer\n"
        "tk.Tk.mainloop = lambda self: (self.update(), self.destroy())\n"
        "import argparse; a = argparse.Namespace(game=r'%s'); print('GUI rc', installer.run_gui(a, 'uk'))" % (PKG, GAME))
if not EXE:
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8")
    check("GUI builds and closes (tkinter)", "GUI rc 0" in p.stdout, p.stdout + p.stderr)

print("\nRESULT:", "ALL PASSED" if not fails else f"{len(fails)} FAILED: {fails}")
sys.exit(1 if fails else 0)
