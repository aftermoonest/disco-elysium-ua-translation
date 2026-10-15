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
obj = next(o for o in env.objects if o.path_id == OBJ_ID)
raw = bytearray(obj.get_raw_data())
fid, pid = struct.unpack_from("<iq", raw, OFFSET)
assert b"ABILITY_NAME_INT" in raw and (fid, pid) == (2, 9785), (fid, pid)
struct.pack_into("<iq", raw, OFFSET, 0, 0)
obj.set_raw_data(bytes(raw))
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_bytes(env.file.save())
print("written", dst, dst.stat().st_size, "(source", src.stat().st_size, ")")
