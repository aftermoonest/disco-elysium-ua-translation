"""Change the font size of the startup splash text ("LOADING" TMP text, level0 MonoBehaviour path_id 49) on a COPY.

Usage: python -I tools/patch_splash_fontsize.py <src level0> <out level0> <new size>
Layout of the TMP fields in that object (found by hexdump): +0x124 fontSize (float), +0x128 fontSizeBase (float),
both 110.0 in the original. Verifies the old values before writing. Never writes to the game folder.
"""
import struct
import sys
from pathlib import Path

import UnityPy

src, dst, size = Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3])
env = UnityPy.load(str(src))
# Found by content (path_id 49 on Windows; ids differ in the macOS build): the TMP text "LOADING" with fontSize == fontSizeBase == 110
cands = []
for o in env.objects:
    if o.type.name != "MonoBehaviour":
        continue
    r = o.get_raw_data()
    if b"LOADING" in r[:0x70] and len(r) >= 0x130:
        cands.append((o, r, struct.unpack_from("<ff", r, 0x124)))
for o, r, fl in cands:
    print("candidate path_id", o.path_id, "size", len(r), "fontSize/base", fl)
cands = [c for c in cands if c[2] == (110.0, 110.0)]
assert len(cands) == 1, f"expected exactly one LOADING text with size 110, found {len(cands)}"
obj, raw, (fs, fb) = cands[0]
print("using path_id", obj.path_id)
print("old fontSize/base:", fs, fb)
new = bytearray(raw)
struct.pack_into("<ff", new, 0x124, size, size)
data = bytearray(src.read_bytes())
start = obj.byte_start
assert bytes(data[start:start + len(raw)]) == raw, "byte_start mismatch"
data[start:start + len(raw)] = new
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_bytes(bytes(data))
diff = [i for i in range(len(data)) if data[i] != src.read_bytes()[i]] if len(data) < 5_000_000 else []
print("written", dst, "size", len(data), "changed bytes:", len(diff), "new:", size)
