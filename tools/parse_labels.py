import sys, struct, UnityPy
sys.stdout.reconfigure(encoding='utf-8')

def parse_labels(raw):
    """Parse CharsheetSkillLabels* MonoBehaviour raw bytes -> (header, entries, tail)."""
    p = 28 + 0  # PPtr(12)+enabled(4)+PPtr(12)
    n = struct.unpack_from('<i', raw, p)[0]; p += 4
    p += (n + 3) // 4 * 4
    count = struct.unpack_from('<i', raw, p)[0]; p += 4
    entries = []
    for _ in range(count):
        eid = struct.unpack_from('<i', raw, p)[0]; p += 4
        ln = struct.unpack_from('<i', raw, p)[0]; p += 4
        text = raw[p:p+ln].decode('utf-8'); p += (ln + 3) // 4 * 4
        floats = struct.unpack_from('<9f', raw, p); p += 36
        entries.append((eid, text, floats))
    return count, entries, raw[p:]

env = UnityPy.load(sys.argv[1])
for o in env.objects:
    if o.path_id in (3005, 3010):
        c, e, tail = parse_labels(o.get_raw_data())
        print(o.path_id, c, 'tail bytes:', len(tail))
        for x in e: print(x[0], repr(x[1]), x[2][0], [round(v,2) for v in x[2][1:]])

