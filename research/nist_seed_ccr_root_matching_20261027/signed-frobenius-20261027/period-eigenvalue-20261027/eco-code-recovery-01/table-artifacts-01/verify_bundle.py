"""Public source-metadata replay, requiring no original executable or network."""
import hashlib
import io
import json
from pathlib import Path
import tarfile

P=Path(__file__).resolve().parent
r=json.loads((P/'BUNDLE.json').read_text());raw=(P/r['archive']['path']).read_bytes()
assert len(raw)==r['archive']['bytes']
assert hashlib.sha256(raw).hexdigest()==r['archive']['sha256']
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as tar:
    a=tar.getmembers()
    assert len(a)==r['sealed_files']
    assert {m.name for m in a}=={'evidence/'+n for n in r['files']}
    for m in a:
        assert m.isfile()
        n=m.name[len('evidence/'):];b=tar.extractfile(m).read()
        assert len(b)==r['files'][n]['bytes']
        assert hashlib.sha256(b).hexdigest()==r['files'][n]['sha256']
        assert (P/n).read_bytes()==b
c=json.loads((P/'COLLATION.json').read_text())
w=c['printed_witness']
assert [[v%101 for v in row] for row in w['coefficient_rows']]==w['modulus101_rows']
coeff=[1]
for _ in range(3):
    out=[0]*(len(coeff)+2)
    for i,a in enumerate(coeff):
        for j,b in enumerate([5,10,1]):out[i+j]+=a*b
    coeff=out
assert coeff==[row[0] for row in w['coefficient_rows']]
h=json.loads((P/'HISTORY-REVIEW.json').read_text())['snapshot']
assert h['branches']=={} and h['next_branch'] is None
print(json.dumps({'status':'PASS','sealed_files':r['sealed_files'],
                  'printed_coefficients_checked':14,'new_scientific_trials':0}))
