import json,hashlib
from pathlib import Path
r=Path(__file__).parent;s=r/'preparation/matching-blocks';m=json.loads((s/'index.json').read_text());rows=[]
for p in m['parts']:
 b=(s/p['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==p['sha256'];rows.append(json.loads(b))
b=(json.dumps(rows,indent=2)+'\n').encode();assert len(b)==m['original_bytes'] and hashlib.sha256(b).hexdigest()==m['original_sha256']
p=r/'preparation/matching.json'
if p.exists():assert p.read_bytes()==b
else:
 with p.open('xb')as f:f.write(b)
print('Exact raw matching.json reconstructed/verified',len(b),'bytes')
