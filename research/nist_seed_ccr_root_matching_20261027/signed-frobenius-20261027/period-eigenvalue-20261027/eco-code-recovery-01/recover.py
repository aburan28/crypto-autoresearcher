"""Bounded public archive queries, with exact prefix semantics and receipts."""
from concurrent.futures import ThreadPoolExecutor
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.parse

P = Path(__file__).resolve().parent
W = P/'.work'
assert not (P/'ACCESS.json').exists(), 'Use a new recovery attempt; preserve receipts.'


def cdx(prefix, pattern=None):
    args = [('url', prefix), ('matchType', 'prefix'), ('output', 'json'),
            ('filter', 'statuscode:200'), ('collapse', 'urlkey'),
            ('fl', 'timestamp,original,mimetype,statuscode,digest'), ('limit', '100')]
    if pattern:
        args.append(('filter', 'original:'+pattern))
    return 'https://web.archive.org/cdx/search/cdx?'+urllib.parse.urlencode(args)


urls = [
    ('ti-software-filter', cdx('http://www.informatik.tu-darmstadt.de/ftp/pub/TI/',
                             '(?i).*(eco|lidia|elliptic).*')),
    ('ti-lidia-releases', cdx('http://www.informatik.tu-darmstadt.de/TI/LiDIA/ftp/LiDIA/')),
    ('ti-systems', cdx('http://www.informatik.tu-darmstadt.de/ftp/pub/TI/systems/')),
    ('ti-www-eco', cdx('http://www.informatik.tu-darmstadt.de/TI/',
                      '(?i).*(eco|choose_relations|buildLlist|compute_klist).*')),
    ('ti-ftp-index', 'https://web.archive.org/cdx/search/cdx?'+urllib.parse.urlencode({
        'url': 'http://www.informatik.tu-darmstadt.de/ftp/pub/TI/', 'output': 'json',
        'filter': 'statuscode:200', 'collapse': 'digest', 'limit': '20',
        'fl': 'timestamp,original,mimetype,statuscode,digest'})),
    ('ti-eco-gfp', cdx('http://www.informatik.tu-darmstadt.de/TI/LiDIA/',
                      '(?i).*(eco_gfp|eco\.tar|ECO-1|ECO-2).*')),
]


def get(item):
    name, url = item
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cmd = ['/usr/bin/curl', '--fail', '--location', '--connect-timeout', '8',
           '--max-time', '35', '--output', str(W/(name+'.bin')),
           '--write-out', '%{http_code}\n%{url_effective}\n', url]
    result = subprocess.run(cmd, capture_output=True)
    (W/(name+'.stderr')).write_bytes(result.stderr)
    (W/(name+'.stdout')).write_bytes(result.stdout)
    record = {'name': name, 'url': url, 'command': cmd, 'started_at': start,
              'finished_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'returncode': result.returncode, 'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace')}
    body = W/(name+'.bin')
    if body.exists():
        data = body.read_bytes()
        record.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        try:
            records = json.loads(data)
            record['cdx_rows'] = len(records)-1 if records else 0
            record['records'] = records
        except Exception:
            record['body_not_json'] = True
    return record


with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(get, urls))
(P/'ACCESS.json').write_text(json.dumps(results, indent=2, sort_keys=True)+'\n')
for record in results:
    print(json.dumps({k: v for k, v in record.items()
                      if k in ['name', 'returncode', 'bytes', 'cdx_rows', 'body_not_json']}))
