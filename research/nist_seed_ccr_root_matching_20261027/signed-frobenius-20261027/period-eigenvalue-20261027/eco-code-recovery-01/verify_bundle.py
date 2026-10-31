"""Check the public seal and compressed catalogs without private source bodies."""
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

P = Path(__file__).resolve().parent
r = json.loads((P/'BUNDLE.json').read_text())


def check(body, meta):
    assert len(body) == meta['bytes']
    assert hashlib.sha256(body).hexdigest() == meta['sha256']


raw = (P/r['archive']['path']).read_bytes()
check(raw,r['archive'])
for n, meta in r['external_components'].items():
    check((P/n).read_bytes(),meta)
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as tar:
    members = tar.getmembers()
    assert len(members) == r['sealed_files']
    assert {m.name for m in members} == {'evidence/'+n for n in r['files']}
    for m in members:
        assert m.isfile()
        n = m.name[len('evidence/'):]
        body = tar.extractfile(m).read()
        check(body,r['files'][n])
        assert (P/n).read_bytes() == body
rows = list(csv.DictReader(io.StringIO(gzip.decompress((P/'package-members.csv.gz').read_bytes()).decode())))
hashes = json.loads(gzip.decompress((P/'package-file-hashes.json.gz').read_bytes()))
assert len(rows) == 1461 and len(hashes) == 1285
assert {q['name'] for q in rows if q['type']=='0'} == {q['name'] for q in hashes}
assert len({q['name'] for q in hashes}) == 1285
print(json.dumps({'status':'PASS','sealed_files':r['sealed_files'],
                  'external_components':len(r['external_components']),
                  'members':len(rows),'regular_files':len(hashes),'new_scientific_trials':0}))
