"""Fetch named public files once, retaining every access outcome."""
from concurrent.futures import ThreadPoolExecutor
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

P = Path(__file__).resolve().parent
group = sys.argv[1]
assert group.replace('-', '').isalnum()
assert not (P/(group+'-ACCESS.json')).exists()
args = sys.argv[2:]
assert len(args) % 2 == 0
items = list(zip(args[::2], args[1::2]))


def get(item):
    name, url = item
    assert name.replace('-', '').isalnum() and url.startswith('https://')
    dst = P/'.work'/(name+'.bin')
    assert not dst.exists()
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cmd = ['/usr/bin/curl', '--fail', '--location', '--connect-timeout', '8',
           '--max-time', '35', '--output', str(dst), '--write-out',
           '%{http_code}\n%{url_effective}\n', url]
    result = subprocess.run(cmd, capture_output=True)
    (P/'.work'/(name+'.stdout')).write_bytes(result.stdout)
    (P/'.work'/(name+'.stderr')).write_bytes(result.stderr)
    row = {'name': name, 'url': url, 'started_at': start,
           'finished_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'command': cmd, 'returncode': result.returncode,
           'stdout': result.stdout.decode(errors='replace'),
           'stderr': result.stderr.decode(errors='replace')}
    if dst.exists():
        data = dst.read_bytes()
        row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                   header_hex=data[:16].hex())
    return row


with ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(get, items))
(P/(group+'-ACCESS.json')).write_text(json.dumps(records, indent=2, sort_keys=True)+'\n')
for row in records:
    print(json.dumps({k: v for k, v in row.items() if k in ['name','returncode','stdout','bytes']}))
