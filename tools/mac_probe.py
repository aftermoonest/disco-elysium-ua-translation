"""Read-only probe of a Disco Elysium game folder (written for the macOS Steam build, works anywhere).

Usage: python3 -I tools/mac_probe.py [game folder] > mac_report.txt
Default folder: ~/Library/Application Support/Steam/steamapps/common/Disco Elysium

Standard library only. Never writes into the game folder. Prints: the .app layout, which scripting backend is used
(IL2CPP vs Mono), SHA-256 + size of every file we patch or replace, the header of each Unity file (Unity version and,
for serialized files, the target platform), and the list of asset bundles. Paste the output to the author.
"""
import hashlib
import struct
import sys
from pathlib import Path

# Unity BuildTarget values (serialized file "targetPlatform")
PLATFORMS = {2: "StandaloneOSX", 5: "StandaloneWindows", 9: "StandaloneLinux", 13: "StandaloneLinux64",
             19: "StandaloneWindows64", 24: "StandaloneOSXIntel64?", 27: "StandaloneOSX(ARM?)"}

PATCHED = ["resources.assets", "level0", "level2", "il2cpp_data/Metadata/global-metadata.dat",
           "sharedassets0.assets", "sharedassets1.assets", "sharedassets2.assets", "globalgamemanagers"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cstr(b, pos):
    end = b.index(b"\0", pos)
    return b[pos:end].decode("ascii", "replace"), end + 1


def unityfs_header(path):
    with open(path, "rb") as f:
        b = f.read(256)
    if not b.startswith(b"UnityFS\0"):
        return "not UnityFS (first bytes %r)" % b[:8]
    ver = struct.unpack_from(">I", b, 8)[0]
    unity, p = cstr(b, 12)
    rev, _ = cstr(b, p)
    return "UnityFS v%d, unity %s / %s" % (ver, unity, rev)


def serialized_header(path):
    with open(path, "rb") as f:
        b = f.read(512)
    try:
        version = struct.unpack_from(">I", b, 8)[0]
        big = version >= 9 and b[16] != 0  # endian byte + 3 reserved follow the 16-byte legacy header
        pos = 48 if version >= 22 else 20  # v22+ adds metadata_size u32, file_size i64, data_offset i64, unknown i64
        unity, pos = cstr(b, pos) if version >= 7 else ("?", pos)
        plat = struct.unpack_from(">i" if big else "<i", b, pos)[0] if version >= 8 else None
        return "SerializedFile v%d, unity %s, targetPlatform %s (%s)" % (
            version, unity, plat, PLATFORMS.get(plat, "unknown"))
    except Exception as e:  # header layout differs: report raw bytes instead of guessing
        return "unparsed header (%s): %s" % (e, b[:32].hex())


def describe(path):
    with open(path, "rb") as f:
        magic = f.read(8)
    if magic.startswith(b"UnityFS"):
        return unityfs_header(path)
    if path.name == "global-metadata.dat":
        with open(path, "rb") as f:
            m, v = struct.unpack("<Ii", f.read(8))
        return "il2cpp metadata magic %#x version %d" % (m, v)
    return serialized_header(path)


def find_data_dir(game):
    for rel in ("disco.app/Contents/Resources/Data", "disco_Data", "Contents/Resources/Data", "Data"):
        d = game / rel
        if d.is_dir():
            return d
    for d in game.glob("*.app/Contents/Resources/Data"):
        return d
    return None


def main():
    game = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else \
        Path("~/Library/Application Support/Steam/steamapps/common/Disco Elysium").expanduser()
    print("game folder:", game)
    data = find_data_dir(game)
    if not data:
        print("!! no Data folder found; top level:", sorted(p.name for p in game.iterdir()))
        return 2
    print("data folder:", data)

    print("\n== layout (depth<=3 under Contents) ==")
    contents = next(game.glob("*.app/Contents"), None)
    if contents:
        for p in sorted(contents.rglob("*")):
            rel = p.relative_to(contents)
            if len(rel.parts) <= 2 and p.is_dir():
                print("  [dir]", rel)
        for p in sorted((contents / "Frameworks").glob("*")) if (contents / "Frameworks").is_dir() else []:
            print("  framework:", p.name)
        for p in sorted((contents / "MacOS").glob("*")) if (contents / "MacOS").is_dir() else []:
            print("  macos exe:", p.name, p.stat().st_size)
        print("  Info.plist:", (contents / "Info.plist").exists())
    print("  Data/ entries:")
    for p in sorted(data.iterdir()):
        print("   ", p.name + ("/" if p.is_dir() else ""), "" if p.is_dir() else p.stat().st_size)
    print("  scripting backend:", "IL2CPP" if (data / "il2cpp_data").is_dir() else
          "Mono" if (data / "Managed").is_dir() else "unknown")

    print("\n== files we patch / replace ==")
    for rel in PATCHED:
        p = data / rel
        if p.is_file():
            print("%-45s %11d  %s\n    %s" % (rel, p.stat().st_size, sha256(p), describe(p)))
        else:
            print("%-45s MISSING" % rel)
    for p in sorted(data.glob("level*")) + sorted(data.glob("sharedassets*")):
        if p.is_file() and p.suffix != ".resS" and p.name not in PATCHED:
            print("%-45s %11d  %s" % (p.name, p.stat().st_size, sha256(p)))

    print("\n== asset bundles ==")
    ab = data / "StreamingAssets" / "AssetBundles"
    if not ab.is_dir():
        print("  no AssetBundles dir")
    else:
        for p in sorted(ab.rglob("*")):
            if p.is_file() and p.suffix != ".manifest":
                rel = p.relative_to(ab)
                print("%-40s %11d  %s\n    %s" % (rel, p.stat().st_size, sha256(p), describe(p)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
