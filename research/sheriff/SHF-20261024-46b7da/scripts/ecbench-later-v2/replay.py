#!/usr/bin/env python3
"""Independent read-only integrity checks for sessions after the sheriff's current prefix."""
import concurrent.futures
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

REPO = Path('/home/ec2-user/crypto-sheriff-main-20261024')
BINARY = REPO / 'target/release/ecbench'
OUT = Path('/home/ec2-user/scratch/validation-continuation-20261023/ecbench-later-sessions-v2-20261024')
MIN_PATH = 'research/isogeny-volcano-cost-v2_20261017/sessions/l3-s1001'
HEAD = '172f84c7b0143ff5b4a26d6d21ffed3bf0f0cf3b'
WORKERS = 4
PER_SESSION_TIMEOUT = 1200
BINARY_SHA = hashlib.sha256(BINARY.read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()


def run_one(path):
    rel = str(Path(path).parent)
    rid = hashlib.sha256(rel.encode()).hexdigest()[:20]
    receipt = OUT / f'{rid}.json'
    if receipt.exists():
        obj = json.loads(receipt.read_text())
        if obj.get('session_dir') == rel and obj.get('head') == HEAD:
            return obj['status']
        raise RuntimeError(f'receipt identity collision: {receipt}')
    result = OUT / f'{rid}.ecbench.json'
    started = time.time()
    source_dir = REPO / rel
    source_hashes = {}
    with tempfile.TemporaryDirectory(prefix='ecbench-verify-', dir='/var/tmp') as td:
        temp_dir = Path(td)
        for source in source_dir.iterdir():
            if not source.is_file():
                continue
            source_hashes[source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
            (temp_dir / source.name).symlink_to(source)
        for source in source_dir.glob('*.gz'):
            uncompressed = temp_dir / source.name[:-3]
            if not uncompressed.exists():
                with gzip.open(source, 'rb') as inp, uncompressed.open('wb') as out:
                    shutil.copyfileobj(inp, out)
        args = [str(BINARY), 'verify', '--dir', str(temp_dir), '--replay', '0', '--allow-interrupted', '--exit-code', '--out', str(result)]
        try:
            proc = subprocess.run(args, cwd=REPO, capture_output=True, text=True, errors='replace', timeout=PER_SESSION_TIMEOUT)
            status = 'pass' if proc.returncode == 0 else 'fail'
            code = proc.returncode
            stdout = proc.stdout[-3000:]
            stderr = proc.stderr[-3000:]
        except subprocess.TimeoutExpired as exc:
            status = 'timeout'; code = None
            stdout = (exc.stdout or b'')[-3000:]
            stderr = (exc.stderr or b'')[-3000:]
            if isinstance(stdout, bytes): stdout = stdout.decode('utf-8', 'replace')
            if isinstance(stderr, bytes): stderr = stderr.decode('utf-8', 'replace')
    if status == 'pass':
        try:
            audit = json.loads(result.read_text())
            if audit.get('ok') is not True or audit.get('records_bound') is not True or audit.get('problems') != []:
                status = 'fail'
                stderr += '\naudit receipt did not assert ok, bound records, and zero problems'
        except Exception as exc:
            status = 'instrument_error'
            stderr += f'\nmissing or invalid audit receipt: {type(exc).__name__}: {exc}'
    data = {
        'schema': 'ecbench.session.integrity.recheck/v1', 'head': HEAD,
        'session_dir': rel, 'session_json_sha256': hashlib.sha256((REPO/path).read_bytes()).hexdigest(),
        'binary_sha256': BINARY_SHA,
        'source_file_sha256': source_hashes,
        'normalization': 'temporary decompression of tracked gzip files; published checkout unchanged',
        'status': status, 'exit_code': code, 'elapsed_seconds': round(time.time()-started, 3),
        'result_file': result.name if result.exists() else None,
        'result_sha256': hashlib.sha256(result.read_bytes()).hexdigest() if result.exists() else None,
        'stdout_tail': stdout, 'stderr_tail': stderr,
    }
    tmp = OUT / f'.{rid}.{os.getpid()}.tmp'
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')
    tmp.replace(receipt)
    return status


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    head = git('rev-parse','HEAD')
    if head != HEAD: raise RuntimeError(f'checkout moved: {head}')
    names = git('ls-tree','-r','--name-only','HEAD').splitlines()
    paths = []
    for p in names:
        if not p.endswith('/session.json') or p < MIN_PATH: continue
        q = REPO/p
        if not q.is_file(): raise RuntimeError(f'tracked session missing: {p}')
        try: data = json.loads(q.read_text())
        except Exception as exc: raise RuntimeError(f'malformed tracked session: {p}') from exc
        if data.get('schema') == 'ecbench.session/v1': paths.append(p)
    print('start', datetime.datetime.now(datetime.timezone.utc).isoformat(), 'head', HEAD, 'selected', len(paths), 'workers', WORKERS, flush=True)
    counts = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(run_one,p):p for p in paths}
        for i,fut in enumerate(concurrent.futures.as_completed(futures),1):
            try: status = fut.result()
            except Exception as exc:
                status = 'instrument_error'
                print('instrument_error', futures[fut], type(exc).__name__, str(exc)[:300], flush=True)
            counts[status] = counts.get(status,0)+1
            if i%20 == 0 or i == len(paths): print('progress',i,len(paths),counts,flush=True)
    summary = {'schema':'ecbench.session.integrity.batch/v1','head':HEAD,'min_path':MIN_PATH,'selected':len(paths),'counts':counts,'workers':WORKERS,'per_session_timeout':PER_SESSION_TIMEOUT,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print('complete',summary,flush=True)
    return 0 if counts.get('pass')==len(paths) else 1

if __name__=='__main__': sys.exit(main())
