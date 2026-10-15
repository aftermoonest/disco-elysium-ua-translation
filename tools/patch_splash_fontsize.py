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
obj = next(o for o in env.objects if o.path_id == 49 and o.type.name == "MonoBehaviour")
raw = obj.get_raw_data()
assert b"LOADING" in raw[:0x70], "not the LOADING text object"
fs, fb = struct.unpack_from("<ff", raw, 0x124)
assert (fs, fb) in ((110.0, 110.0),) or fs == fb, (fs, fb)
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
