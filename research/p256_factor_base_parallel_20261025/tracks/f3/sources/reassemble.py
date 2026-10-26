"""Reconstitute the exact retrieved source PDF from size-limited shards."""
from hashlib import sha256
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parent
manifest=json.loads((root/'aps2018.pdf.manifest.json').read_text())
chunks=[]
for shard in manifest['shards']:
    data=(root/shard['path']).read_bytes()
    assert len(data)==shard['bytes'] and sha256(data).hexdigest()==shard['sha256']
    chunks.append(data)
data=b''.join(chunks)
assert len(data)==manifest['bytes'] and sha256(data).hexdigest()==manifest['sha256']
if len(sys.argv)>1:
    with Path(sys.argv[1]).open('xb') as f: f.write(data)
print(json.dumps(dict(status='verified',bytes=len(data),sha256=sha256(data).hexdigest())))
