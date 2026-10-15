"""Replace ONE string literal in il2cpp global-metadata.dat (version 27) on a COPY.

Usage: python -I tools/patch_metadata_literal.py <src global-metadata.dat> <out> <old text> <new text>

How: the literal table (Il2CppStringLiteral {u32 length; i32 dataIndex}) points into the literal data blob.
The new text (UTF-8, possibly longer than the old one) is appended at the END of the file and the table entry
is repointed (dataIndex = end_of_file - stringLiteralDataOffset, length = new byte length). Nothing else changes,
so no other offsets move. Verifies that exactly one table entry references the old text.
Never writes to the game folder.
"""
import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def main():
    src, dst, old, new = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
    b = bytearray(src.read_bytes())
    magic, ver = struct.unpack_from("<Ii", b, 0)
    assert magic == 0xFAB11BAF and ver == 27, (hex(magic), ver)
    sl_off, sl_size, sd_off, sd_size = struct.unpack_from("<4i", b, 8)
    old_b, new_b = old.encode("utf-8"), new.encode("utf-8")
    hits = []
    for i in range(sl_size // 8):
        ln, idx = struct.unpack_from("<Ii", b, sl_off + 8 * i)
        if ln == len(old_b) and bytes(b[sd_off + idx: sd_off + idx + ln]) == old_b:
            hits.append(i)
    assert len(hits) == 1, f"expected exactly one literal entry for {old!r}, found {len(hits)}"
    i = hits[0]
    while len(b) % 4:
        b.append(0)
    new_idx = len(b) - sd_off
    b += new_b + b"\x00" * (-len(new_b) % 4)
    struct.pack_into("<Ii", b, sl_off + 8 * i, len(new_b), new_idx)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(bytes(b))
    print(f"literal #{i}: {old!r} -> {new!r} ({len(old_b)} -> {len(new_b)} bytes), data index {new_idx}, file {src.stat().st_size} -> {len(b)}")


if __name__ == "__main__":
    main()
