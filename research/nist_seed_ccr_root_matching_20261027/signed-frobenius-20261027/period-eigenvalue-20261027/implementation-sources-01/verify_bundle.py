"""Verify archive bytes and every public member; original computation stays separate."""
import hashlib
import io
import json
from pathlib import Path
import tarfile

P = Path(__file__).resolve().parent
record = json.loads((P/'BUNDLE.json').read_text())
raw = (P/'public-evidence.tar.gz').read_bytes()
assert len(raw) == record['archive_bytes']
assert hashlib.sha256(raw).hexdigest() == record['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
    members = tar.getmembers()
    assert {m.name for m in members} == {'evidence/'+n for n in record['files']}
    assert len(members) == record['sealed_files']
    for member in members:
        assert member.isfile()
        name = member.name.removeprefix('evidence/')
        data = tar.extractfile(member).read()
        expected = record['files'][name]
        assert len(data) == expected['bytes']
        assert hashlib.sha256(data).hexdigest() == expected['sha256']
        assert (P/name).read_bytes() == data
print(json.dumps({'status': 'PASS', 'members_checked': len(members),
                  'archive_bytes': len(raw), 'new_scientific_trials': 0}))
