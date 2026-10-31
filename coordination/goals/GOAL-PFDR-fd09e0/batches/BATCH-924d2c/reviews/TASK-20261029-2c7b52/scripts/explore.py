# Exploratory census of the raw jobs file: key sets, field types, statuses.
import json, sys, collections
path = sys.argv[1]
keys = collections.Counter(); status = collections.Counter(); cells = collections.Counter()
blocks = collections.Counter(); metakeys = collections.Counter(); types = collections.defaultdict(set)
nonok = []
with open(path) as fh:
    for ln, line in enumerate(fh, 1):
        rec = json.loads(line)
        keys[tuple(sorted(rec))] += 1
        status[rec.get('status')] += 1
        cells[rec.get('cell')] += 1
        blocks[rec.get('block')] += 1
        for k, v in rec.items():
            types[k].add(type(v).__name__)
        gm = rec.get('gap_meta')
        if isinstance(gm, dict):
            metakeys[tuple(sorted(gm))] += 1
        else:
            metakeys[repr(gm)] += 1
        if rec.get('status') != 'ok':
            nonok.append({k: rec[k] for k in rec if k not in ('null_C', 'null_D')})
print('key sets:', dict(keys))
print('status:', dict(status))
print('blocks:', dict(blocks))
print('gap_meta key sets:', dict(metakeys))
print('types:', {k: sorted(v) for k, v in types.items()})
print('n cells:', len(cells))
for c in sorted(cells, key=lambda s: (int(s.split('-')[0][1:]), int(s.split('-')[1][1:]), int(s.split('-')[2][1:]))):
    print(c, cells[c])
print('non-ok records:', len(nonok))
for r in nonok:
    print(json.dumps(r, sort_keys=True))
