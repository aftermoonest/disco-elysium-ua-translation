#!/usr/bin/env python3
"""Disco Elysium — Ukrainian translation installer / Інсталятор українського перекладу Disco Elysium.

Pure Python 3 (standard library only). Works on Windows, Linux (Steam Deck / Proton) and macOS.

    python3 installer.py                 graphical window (falls back to text mode when no display)
    python3 installer.py --cli install   text mode: install   (--game PATH, --dry-run, --yes)
    python3 installer.py --cli remove    text mode: restore the original files
    python3 installer.py --cli info      show what was detected
    python3 installer.py --cli collect-info   print hashes of the game files (to report an unsupported version)

How it works: the package next to this script contains small binary patches (bsdiff) for a few game files
and the translation bundles. Every file to patch is verified by SHA-256 against known original versions.
Originals are saved to <game>/_ua_backup/ first, so "remove" (and a re-install / update) always starts clean.
"""
import argparse
import bz2
import hashlib
import json
import locale
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

BACKUP_DIRNAME = "_ua_backup"
STATE_FILE = "install.json"

# --------------------------------------------------------------------------- i18n
T = {
    "uk": {
        "title": "Disco Elysium — український переклад",
        "version": "Версія перекладу: {0}",
        "game_dir": "Тека гри:",
        "browse": "Обрати…",
        "detect": "Знайти гру",
        "install": "Встановити / оновити",
        "remove": "Видалити (повернути оригінал)",
        "language": "Мова / Language:",
        "log": "Журнал",
        "no_game": "Гру не знайдено. Вкажіть теку вручну (у ній має бути тека disco_Data).",
        "found_game": "Знайдено гру: {0}",
        "bad_dir": "У теці «{0}» не знайдено файлів гри Disco Elysium.",
        "state_unknown": "Невідома версія гри (файли не збігаються з відомими). Нічого не змінено.",
        "state_unknown_help": "Перевірте цілісність файлів у Steam (Властивості → Інстальовані файли) і спробуйте знову.\n"
                              "Якщо це інша версія гри (GOG, Xbox, Mac), запустіть режим «collect-info» і надішліть результат автору.",
        "state_original": "Гра: оригінальні файли ({0}). Переклад не встановлено.",
        "state_installed": "Переклад встановлено (версія {0}).",
        "state_installed_old": "Переклад встановлено, але інша версія ({0}). Доступне оновлення до {1}.",
        "state_partial": "Гра у проміжному стані (частина файлів змінена). Встановлення виправить це.",
        "state_nobackup": "Файли гри вже містять переклад, але резервної копії інсталятора немає (мод ставили вручну). "
                          "Щоб встановити чи видалити через інсталятор, спочатку перевірте цілісність файлів у Steam "
                          "(Властивості → Інстальовані файли), потім запустіть інсталятор знову.",
        "game_running": "Гра запущена. Закрийте Disco Elysium і повторіть.",
        "dry": "[пробний запуск, нічого не змінюється] ",
        "backup": "Резервна копія: {0}",
        "patch": "Патч: {0}",
        "copy": "Копіювання: {0}",
        "restore": "Відновлення: {0}",
        "delete": "Видалення: {0}",
        "verify_fail": "Помилка перевірки: {0}. Зміни скасовано.",
        "done_install": "Готово! Тепер запустіть гру й оберіть мову Deutsch у налаштуваннях.",
        "done_remove": "Готово. Оригінальні файли повернуто.",
        "nothing_to_remove": "Переклад не встановлено (немає резервної копії) — нічого видаляти.",
        "confirm": "Продовжити? [y/N] ",
        "cancelled": "Скасовано.",
        "error": "Помилка: {0}",
        "wait": "Зачекайте…",
    },
    "en": {
        "title": "Disco Elysium — Ukrainian translation",
        "version": "Translation version: {0}",
        "game_dir": "Game folder:",
        "browse": "Browse…",
        "detect": "Find game",
        "install": "Install / update",
        "remove": "Remove (restore original)",
        "language": "Мова / Language:",
        "log": "Log",
        "no_game": "Game not found. Pick the folder manually (it must contain the disco_Data folder).",
        "found_game": "Game found: {0}",
        "bad_dir": "No Disco Elysium game files found in \"{0}\".",
        "state_unknown": "Unknown game version (files do not match any known version). Nothing was changed.",
        "state_unknown_help": "Verify the game files in Steam (Properties → Installed files) and try again.\n"
                              "If this is another build (GOG, Xbox, Mac), run \"collect-info\" and send the output to the author.",
        "state_original": "Game: original files ({0}). Translation is not installed.",
        "state_installed": "Translation is installed (version {0}).",
        "state_installed_old": "Translation is installed, but a different version ({0}). Update to {1} is available.",
        "state_partial": "Game is in an intermediate state (some files are modified). Installing will fix that.",
        "state_nobackup": "The game files already contain the translation, but there is no installer backup (installed by hand). "
                          "To install or remove it with this tool, first verify the game files in Steam "
                          "(Properties → Installed files), then run the installer again.",
        "game_running": "The game is running. Close Disco Elysium and try again.",
        "dry": "[dry run, nothing is changed] ",
        "backup": "Backup: {0}",
        "patch": "Patch: {0}",
        "copy": "Copy: {0}",
        "restore": "Restore: {0}",
        "delete": "Delete: {0}",
        "verify_fail": "Verification failed: {0}. Changes were rolled back.",
        "done_install": "Done! Now start the game and choose Deutsch (German) in the game settings.",
        "done_remove": "Done. Original files were restored.",
        "nothing_to_remove": "Translation is not installed (no backup) — nothing to remove.",
        "confirm": "Continue? [y/N] ",
        "cancelled": "Cancelled.",
        "error": "Error: {0}",
        "wait": "Please wait…",
    },
}


def detect_lang():
    try:
        code = (locale.getdefaultlocale()[0] or "").lower()
    except Exception:
        code = ""
    return "uk" if code.startswith("uk") else "en"


class Tr:
    def __init__(self, lang):
        self.lang = lang if lang in T else "en"

    def __call__(self, key, *args):
        s = T[self.lang].get(key) or T["en"].get(key, key)
        return s.format(*args) if args else s


# --------------------------------------------------------------------------- binary patching
def _offtin(b):
    y = int.from_bytes(b[:8], "little")
    return -(y & ((1 << 63) - 1)) if y & (1 << 63) else y


def bspatch(old, patch):
    """Apply a BSDIFF40 patch (as made by bsdiff4 / bsdiff) in pure Python."""
    if patch[:8] != b"BSDIFF40":
        raise ValueError("not a BSDIFF40 patch")
    lc, ld, new_size = _offtin(patch[8:16]), _offtin(patch[16:24]), _offtin(patch[24:32])
    ctrl = bz2.decompress(patch[32:32 + lc])
    diff = bz2.decompress(patch[32 + lc:32 + lc + ld])
    extra = bz2.decompress(patch[32 + lc + ld:])
    out = bytearray()
    op = di = ei = 0
    for ci in range(0, len(ctrl), 24):
        x, y, z = (_offtin(ctrl[ci + i:ci + i + 8]) for i in (0, 8, 16))
        seg_old = old[op:op + x]
        if len(seg_old) < x:
            seg_old = seg_old + bytes(x - len(seg_old))
        seg_diff = diff[di:di + x]
        if seg_diff.count(0) == x:
            out += seg_old
        else:
            out += bytes((a + b) & 255 for a, b in zip(seg_old, seg_diff))
        di += x
        op += x
        out += extra[ei:ei + y]
        ei += y
        op += z
    if len(out) != new_size:
        raise ValueError("patch produced a wrong size")
    return bytes(out)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".ua_tmp")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


# --------------------------------------------------------------------------- package / detection
def package_dir():
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "package"


def load_manifest(pkg=None):
    pkg = pkg or package_dir()
    return json.loads((pkg / "manifest.json").read_text(encoding="utf-8"))


def _steam_roots():
    roots = []
    home = Path.home()
    system = platform.system()
    if system == "Windows":
        try:
            import winreg
            for hive, key in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                              (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")):
                try:
                    with winreg.OpenKey(hive, key) as k:
                        for name in ("SteamPath", "InstallPath"):
                            try:
                                roots.append(Path(winreg.QueryValueEx(k, name)[0]))
                            except OSError:
                                pass
                except OSError:
                    pass
        except ImportError:
            pass
        roots += [Path(r"C:\Program Files (x86)\Steam"), Path(r"C:\Program Files\Steam")]
    elif system == "Darwin":
        roots.append(home / "Library/Application Support/Steam")
    else:
        roots += [home / ".local/share/Steam", home / ".steam/steam", home / ".steam/root",
                  home / ".var/app/com.valvesoftware.Steam/.local/share/Steam"]
    return [r for r in roots if r.exists()]


def candidate_game_dirs():
    cands = []
    for root in _steam_roots():
        libs = [root]
        vdf = root / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            try:
                for m in re.finditer(r'"path"\s+"([^"]+)"', vdf.read_text(encoding="utf-8", errors="replace")):
                    libs.append(Path(m.group(1).replace("\\\\", "\\")))
            except OSError:
                pass
        for lib in libs:
            cands.append(lib / "steamapps" / "common" / "Disco Elysium")
    system = platform.system()
    if system == "Windows":
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            d = Path(f"{letter}:\\")
            if d.exists():
                cands += [d / "XboxGames" / "Disco Elysium" / "Content",
                          d / "Games" / "Disco Elysium",
                          d / "GOG Games" / "Disco Elysium",
                          d / "Program Files (x86)" / "GOG Galaxy" / "Games" / "Disco Elysium",
                          d / "Program Files" / "Epic Games" / "DiscoElysium"]
    elif system == "Linux":
        for base in (Path("/run/media"), Path("/media"), Path("/mnt")):
            if base.exists():
                try:
                    for p in base.glob("*/*/steamapps/common/Disco Elysium"):
                        cands.append(p)
                    for p in base.glob("*/steamapps/common/Disco Elysium"):
                        cands.append(p)
                except OSError:
                    pass
    seen, out = set(), []
    for c in cands:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


class Variant:
    """One supported game build: where the data folder is and which files to patch/replace."""

    def __init__(self, spec):
        self.spec = spec
        self.id = spec["id"]
        self.files = spec["files"]

    def data_dir(self, game_dir):
        for rel in self.spec["data_dirs"]:
            d = Path(game_dir) / rel
            if d.is_dir():
                return d
        return None


def game_running():
    try:
        system = platform.system()
        if system == "Windows":
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq disco.exe"], capture_output=True, text=True, timeout=15).stdout
            return "disco.exe" in out.lower()
        if system == "Linux":
            out = subprocess.run(["pgrep", "-fi", "disco.exe"], capture_output=True, text=True, timeout=15).stdout.split()
            return any(int(p) != os.getpid() for p in out)
    except Exception:
        pass
    return False


class Engine:
    def __init__(self, game_dir, tr, log=print, dry_run=False, pkg=None, check_running=True):
        self.game_dir = Path(game_dir)
        self.tr = tr
        self.log = log
        self.dry = dry_run
        self.pkg = Path(pkg) if pkg else package_dir()
        self.manifest = load_manifest(self.pkg)
        self.variants = [Variant(v) for v in self.manifest["variants"]]
        self.check_running = check_running
        self.backup_dir = self.game_dir / BACKUP_DIRNAME

    # ---- helpers
    def _say(self, key, *args):
        self.log((self.tr("dry") if self.dry else "") + self.tr(key, *args))

    def _state_file(self):
        return self.backup_dir / STATE_FILE

    def installed_state(self):
        try:
            return json.loads(self._state_file().read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def _orig_candidates(self, data_dir, f):
        """Paths that may hold the original bytes of a patch-kind file: backup first, then the live file."""
        return [self.backup_dir / f["path"], data_dir / f["path"]]

    def analyse(self):
        """Return (variant, per-file info) for the first variant that matches, else (None, reason)."""
        for v in self.variants:
            data_dir = v.data_dir(self.game_dir)
            if data_dir is None:
                continue
            info, ok = [], True
            for f in v.files:
                live = data_dir / f["path"]
                entry = {"file": f, "live": live, "live_sha": sha256_file(live) if live.exists() else None, "orig_src": None}
                if f["kind"] == "patch":
                    for cand in self._orig_candidates(data_dir, f):
                        if cand.exists() and sha256_file(cand) == f["orig"]:
                            entry["orig_src"] = cand
                            break
                    if entry["orig_src"] is None:
                        ok = False
                info.append(entry)
            if ok:
                return v, info
        return None, None

    def status(self):
        """('none'|'unknown'|'original'|'installed'|'partial', variant, installed_version)"""
        if not any(v.data_dir(self.game_dir) for v in self.variants):
            return "none", None, None
        v, info = self.analyse()
        if v is None:
            return ("nobackup" if self._looks_installed() else "unknown"), None, None
        state = self.installed_state()
        done = all(e["live_sha"] == e["file"]["new"] for e in info)
        orig = all(e["live_sha"] == e["file"].get("orig", "-") or e["file"]["kind"] == "replace" for e in info)
        if done:
            return "installed", v, (state or {}).get("mod_version", "?")
        if orig and not state:
            return "original", v, None
        return "partial", v, (state or {}).get("mod_version")

    def _looks_installed(self):
        """All patch-kind files already hold the modded bytes (installed by hand / backup lost)."""
        for v in self.variants:
            data_dir = v.data_dir(self.game_dir)
            patched = [f for f in v.files if f["kind"] == "patch"]
            if data_dir and patched and all((data_dir / f["path"]).exists() and sha256_file(data_dir / f["path"]) == f["new"] for f in patched):
                return True
        return False

    def collect_info(self):
        lines = [f"platform: {platform.platform()}", f"game dir: {self.game_dir}", f"package version: {self.manifest['mod_version']}"]
        seen = set()
        for v in self.variants:
            data_dir = v.data_dir(self.game_dir)
            lines.append(f"variant {v.id}: data dir {'found: ' + str(data_dir) if data_dir else 'not found'}")
            if data_dir:
                for f in v.files:
                    p = data_dir / f["path"]
                    if f["path"] in seen:
                        continue
                    seen.add(f["path"])
                    lines.append(f"  {f['path']}: {p.stat().st_size if p.exists() else 'MISSING'} bytes sha256 {sha256_file(p) if p.exists() else '-'}")
        return "\n".join(lines)

    # ---- actions
    def install(self):
        if self.check_running and game_running():
            raise RuntimeError(self.tr("game_running"))
        v, info = self.analyse()
        if v is None:
            if self._looks_installed():
                raise RuntimeError(self.tr("state_nobackup"))
            raise RuntimeError(self.tr("state_unknown") + "\n" + self.tr("state_unknown_help"))
        data_dir = v.data_dir(self.game_dir)
        # 1) read + build everything in memory and verify BEFORE touching the game
        todo = []
        for e in info:
            f = e["file"]
            if f["kind"] == "patch":
                orig = e["orig_src"].read_bytes()
                new = bspatch(orig, (self.pkg / f["patch"]).read_bytes())
            else:
                new = (self.pkg / f["data"]).read_bytes()
            if sha256_bytes(new) != f["new"]:
                raise RuntimeError(self.tr("verify_fail", f["path"]))
            todo.append((e, new))
        # 2) backups
        files_state = []
        for e, new in todo:
            f, live = e["file"], e["live"]
            bak = self.backup_dir / f["path"]
            had_backup = bak.exists()
            created = not live.exists()
            if not had_backup and not created:
                self._say("backup", f["path"])
                if not self.dry:
                    bak.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(live, bak)
            files_state.append({"path": f["path"], "created": created and not had_backup,
                                "backed_up": had_backup or not created})
        # 3) write
        for e, new in todo:
            f, live = e["file"], e["live"]
            if f["kind"] == "patch":
                self._say("patch", f["path"])
            else:
                self._say("copy", f["path"])
            if not self.dry:
                atomic_write(live, new)
        if not self.dry:
            for e, new in todo:
                if sha256_file(e["live"]) != e["file"]["new"]:
                    raise RuntimeError(self.tr("verify_fail", e["file"]["path"]))
            old_state = self.installed_state()
            prev = {x["path"]: x for x in (old_state or {}).get("files", [])}
            for x in files_state:  # keep earlier backup/created flags when updating over an older install
                p = prev.get(x["path"])
                if p:
                    x["backed_up"] = x["backed_up"] or p["backed_up"]
                    x["created"] = x["created"] or p["created"]
            atomic_write(self._state_file(), json.dumps({
                "mod_version": self.manifest["mod_version"], "variant": v.id, "data_dir": str(data_dir.relative_to(self.game_dir)),
                "time": time.strftime("%Y-%m-%d %H:%M:%S"), "files": files_state}, indent=1).encode("utf-8"))
        self.log((self.tr("dry") if self.dry else "") + self.tr("done_install"))

    def remove(self):
        if self.check_running and game_running():
            raise RuntimeError(self.tr("game_running"))
        state = self.installed_state()
        if not state:
            self.log(self.tr("nothing_to_remove"))
            return
        data_dir = self.game_dir / state["data_dir"]
        for x in state["files"]:
            live, bak = data_dir / x["path"], self.backup_dir / x["path"]
            if x["backed_up"] and bak.exists():
                self._say("restore", x["path"])
                if not self.dry:
                    atomic_write(live, bak.read_bytes())
            elif x["created"] and live.exists():
                self._say("delete", x["path"])
                if not self.dry:
                    live.unlink()
        if not self.dry:
            shutil.rmtree(self.backup_dir, ignore_errors=True)
        self.log((self.tr("dry") if self.dry else "") + self.tr("done_remove"))


# --------------------------------------------------------------------------- front ends
def find_game(tr, explicit=None):
    manifest = load_manifest()
    variants = [Variant(v) for v in manifest["variants"]]
    cands = [Path(explicit)] if explicit else candidate_game_dirs()
    for c in cands:
        if any(v.data_dir(c) for v in variants):
            return c
    return None


def describe(engine, tr):
    st, v, ver = engine.status()
    mod = engine.manifest["mod_version"]
    if st == "none":
        return tr("bad_dir", engine.game_dir)
    if st == "nobackup":
        return tr("state_nobackup")
    if st == "unknown":
        return tr("state_unknown") + "\n" + tr("state_unknown_help")
    if st == "original":
        return tr("state_original", v.id)
    if st == "installed":
        return tr("state_installed", ver) if ver == mod else tr("state_installed_old", ver, mod)
    return tr("state_partial")


def run_cli(args, tr):
    game = find_game(tr, args.game)
    if game is None:
        print(tr("no_game"))
        return 2
    print(tr("found_game", game))
    eng = Engine(game, tr, print, dry_run=args.dry_run, check_running=not args.skip_running_check)
    if args.command == "collect-info":
        print(eng.collect_info())
        return 0
    print(describe(eng, tr))
    if args.command == "info":
        return 0
    try:
        if args.command == "install":
            if not args.yes and not args.dry_run and input(tr("confirm")).strip().lower() not in ("y", "yes", "т", "так"):
                print(tr("cancelled"))
                return 1
            eng.install()
        elif args.command == "remove":
            if not args.yes and not args.dry_run and input(tr("confirm")).strip().lower() not in ("y", "yes", "т", "так"):
                print(tr("cancelled"))
                return 1
            eng.remove()
    except Exception as e:  # noqa: BLE001 - show any failure to the user
        print(tr("error", e))
        return 1
    return 0


def run_gui(args, lang):
    import queue
    import tkinter as tk
    from tkinter import filedialog, ttk

    root = tk.Tk()
    tr = Tr(lang)
    q = queue.Queue()
    manifest = load_manifest()
    widgets = {}

    def retitle():
        root.title(tr("title"))
        widgets["ver"].config(text=tr("version", manifest["mod_version"]))
        widgets["dir_l"].config(text=tr("game_dir"))
        widgets["browse"].config(text=tr("browse"))
        widgets["detect"].config(text=tr("detect"))
        widgets["install"].config(text=tr("install"))
        widgets["remove"].config(text=tr("remove"))
        widgets["lang_l"].config(text=tr("language"))
        widgets["log_l"].config(text=tr("log"))
        refresh()

    def log(msg):
        q.put(msg)

    def pump():
        try:
            while True:
                m = q.get_nowait()
                widgets["log"].configure(state="normal")
                widgets["log"].insert("end", m + "\n")
                widgets["log"].see("end")
                widgets["log"].configure(state="disabled")
        except queue.Empty:
            pass
        root.after(100, pump)

    def engine():
        p = path_var.get().strip()
        return Engine(p, tr, log, check_running=True) if p else None

    def refresh():
        eng = engine()
        if eng is None or not Path(path_var.get()).exists():
            status_var.set(tr("no_game"))
            return
        try:
            status_var.set(describe(eng, tr))
        except Exception as e:  # noqa: BLE001
            status_var.set(tr("error", e))

    def detect():
        g = find_game(tr)
        if g:
            path_var.set(str(g))
            log(tr("found_game", g))
        else:
            log(tr("no_game"))
        refresh()

    def browse():
        d = filedialog.askdirectory(title=tr("game_dir"))
        if d:
            path_var.set(d)
            refresh()

    def act(name):
        eng = engine()
        if eng is None:
            log(tr("no_game"))
            return
        for b in ("install", "remove", "detect", "browse"):
            widgets[b].config(state="disabled")
        log(tr("wait"))

        def work():
            try:
                getattr(eng, name)()
            except Exception as e:  # noqa: BLE001
                log(tr("error", e))
            finally:
                root.after(0, done)

        def done():
            for b in ("install", "remove", "detect", "browse"):
                widgets[b].config(state="normal")
            refresh()

        threading.Thread(target=work, daemon=True).start()

    def on_lang(_=None):
        tr.lang = "uk" if lang_var.get() == "Українська" else "en"
        retitle()

    root.geometry("720x520")
    frm = ttk.Frame(root, padding=12)
    frm.pack(fill="both", expand=True)
    widgets["ver"] = ttk.Label(frm, font=("TkDefaultFont", 11, "bold"))
    widgets["ver"].grid(row=0, column=0, columnspan=3, sticky="w")
    widgets["dir_l"] = ttk.Label(frm)
    widgets["dir_l"].grid(row=1, column=0, sticky="w", pady=(10, 0))
    path_var = tk.StringVar()
    ttk.Entry(frm, textvariable=path_var).grid(row=2, column=0, columnspan=2, sticky="ew")
    widgets["browse"] = ttk.Button(frm, command=browse)
    widgets["browse"].grid(row=2, column=2, padx=(6, 0))
    widgets["detect"] = ttk.Button(frm, command=detect)
    widgets["detect"].grid(row=3, column=0, sticky="w", pady=6)
    status_var = tk.StringVar()
    ttk.Label(frm, textvariable=status_var, wraplength=680, justify="left").grid(row=4, column=0, columnspan=3, sticky="w", pady=6)
    widgets["install"] = ttk.Button(frm, command=lambda: act("install"))
    widgets["install"].grid(row=5, column=0, sticky="ew", pady=4)
    widgets["remove"] = ttk.Button(frm, command=lambda: act("remove"))
    widgets["remove"].grid(row=5, column=1, sticky="ew", pady=4, padx=6)
    widgets["lang_l"] = ttk.Label(frm)
    widgets["lang_l"].grid(row=6, column=0, sticky="w", pady=(10, 0))
    lang_var = tk.StringVar(value="Українська" if lang == "uk" else "English")
    cb = ttk.Combobox(frm, textvariable=lang_var, values=["Українська", "English"], state="readonly", width=14)
    cb.grid(row=6, column=1, sticky="w", pady=(10, 0))
    cb.bind("<<ComboboxSelected>>", on_lang)
    widgets["log_l"] = ttk.Label(frm)
    widgets["log_l"].grid(row=7, column=0, sticky="w", pady=(10, 0))
    widgets["log"] = tk.Text(frm, height=12, state="disabled", wrap="word")
    widgets["log"].grid(row=8, column=0, columnspan=3, sticky="nsew")
    frm.columnconfigure(0, weight=1)
    frm.columnconfigure(1, weight=1)
    frm.rowconfigure(8, weight=1)
    retitle()
    pump()
    if args.game:
        path_var.set(args.game)
        refresh()
    else:
        detect()
    root.mainloop()
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Disco Elysium Ukrainian translation installer")
    ap.add_argument("--cli", action="store_true", help="text mode instead of the window")
    ap.add_argument("command", nargs="?", choices=["install", "remove", "info", "collect-info"], help="text-mode action")
    ap.add_argument("--game", help="path to the game folder (skips auto-detection)")
    ap.add_argument("--lang", choices=["uk", "en"], help="interface language")
    ap.add_argument("--dry-run", action="store_true", help="show what would be done, change nothing")
    ap.add_argument("--yes", "-y", action="store_true", help="do not ask for confirmation")
    ap.add_argument("--skip-running-check", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # Cyrillic must survive cp1252 consoles and pipes
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    lang = args.lang or detect_lang()
    tr = Tr(lang)
    if args.command or args.cli:
        if not args.command:
            ap.error("--cli needs a command: install | remove | info | collect-info")
        return run_cli(args, tr)
    try:
        return run_gui(args, lang)
    except Exception as e:  # no tkinter / no display -> text mode
        print(f"(window is unavailable: {e}; use --cli install | remove | info)")
        return 3


if __name__ == "__main__":
    sys.exit(main())
