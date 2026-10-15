"""Build a patched COPY of level2 where the INTELLECT label's I2 Localize component (path_id 25140)
no longer holds a direct PPtr to the base 'Dobra-Book SDF' (sharedassets1 #9785, no Cyrillic).
The PSY/MOT labels have that PPtr null and render Ukrainian fine.

Usage: python -I tools/patch_int_label.py <level2 in> <level2 out>
"""
import struct
import sys
from pathlib import Path

import UnityPy

OBJ_ID, OFFSET = 25140, 0x8C  # int fileID, long pathID

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
env = UnityPy.load(str(src))
# Windows: path_id 25140 with PPtr (2, 9785). Found by content so other builds (macOS) work too: the I2 Localize
# component of ABILITY_NAME_INT that holds a non-null PPtr into sharedassets1 (fileID 2) at OFFSET.
cands = []
for o in env.objects:
    if o.type.name != "MonoBehaviour":
        continue
    r = o.get_raw_data()
    if b"ABILITY_NAME_INT" in r and len(r) > OFFSET + 12:
        fid, pid = struct.unpack_from("<iq", r, OFFSET)
        print("candidate path_id", o.path_id, "size", len(r), "PPtr", (fid, pid))
        if fid == 2 and pid > 0:
            cands.append(o)
assert len(cands) == 1, f"expected exactly one INT Localize component with a PPtr, found {len(cands)}"
obj = cands[0]
raw = bytearray(obj.get_raw_data())
fid, pid = struct.unpack_from("<iq", raw, OFFSET)
print("using path_id", obj.path_id, "PPtr", (fid, pid))
struct.pack_into("<iq", raw, OFFSET, 0, 0)
obj.set_raw_data(bytes(raw))
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_bytes(env.file.save())
print("written", dst, dst.stat().st_size, "(source", src.stat().st_size, ")")
