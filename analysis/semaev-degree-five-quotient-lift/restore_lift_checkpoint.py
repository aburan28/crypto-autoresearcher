#!/usr/bin/env python3
"""Restore the newest fully verified compatible immutable checkpoint manifest.

Unqualified candidate. Never starts the scientific producer itself. Rejections
are retained in a receipt, including when an older checkpoint can be restored.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import uuid

from publish_lift_checkpoint import aws, inspect_snapshot


def download(uri, path, expected):
    h, count = hashlib.sha256(), 0
    with tempfile.TemporaryFile() as errors, path.open('xb') as output:
        child = subprocess.Popen(['aws', 's3', 'cp', uri, '-', '--only-show-errors'],
                                 stdout=subprocess.PIPE, stderr=errors)
        try:
            while True:
                b = child.stdout.read(1 << 20)
                if not b:
                    break
                count += len(b)
                if count > expected['bytes']:
                    raise ValueError('snapshot download exceeds declared size')
                h.update(b)
                output.write(b)
            if child.wait():
                raise RuntimeError('snapshot GET failed')
            if count != expected['bytes'] or h.hexdigest() != expected['sha256']:
                raise ValueError('snapshot GET size/hash mismatch')
            output.flush()
            os.fsync(output.fileno())
        except BaseException:
            if child.poll() is None:
                child.kill()
            child.wait()
            raise
        finally:
            child.stdout.close()


def select(prefix, context_path, output_dir):
    match = re.fullmatch(r's3://([a-z0-9][a-z0-9.-]+)/([^\s]+)', prefix.rstrip('/'))
    if not match:
        raise ValueError('invalid checkpoint prefix')
    bucket, root = match.groups()
    context_bytes = context_path.read_bytes()
    context = json.loads(context_bytes)
    for key in ('request_sha256', 'protocol_sha256', 'seed_sha256', 'binary_sha256'):
        if not re.fullmatch('[0-9a-f]{64}', context[key]):
            raise ValueError('invalid context digest')
    p = aws(['s3api', 'list-objects-v2', '--bucket', bucket, '--prefix', root+'/manifests/'])
    if p.returncode:
        raise RuntimeError('checkpoint manifest listing failed')
    # AWS CLI default pagination is intentionally enabled. Do not silently
    # restrict selection to the first S3 page.
    listing = json.loads(p.stdout)
    if listing.get('IsTruncated') or listing.get('NextToken') or listing.get('NextContinuationToken'):
        raise RuntimeError('checkpoint manifest listing is incomplete')
    candidates = []
    for entry in listing.get('Contents', []):
        name = entry['Key'].removeprefix(root+'/manifests/')
        m = re.fullmatch(r'([0-9]{20})-([0-9a-f]{64})\.json', name)
        if m:
            candidates.append((int(m[1]), m[2], entry))
    receipt = dict(schema='semaev.checkpoint-restore/v1', status='no_compatible_checkpoint',
                   prefix=prefix, context_sha256=hashlib.sha256(context_bytes).hexdigest(),
                   rejected=[], scope='Verified state restoration only; no mathematical acceptance')
    for sequence, manifest_sha, entry in sorted(candidates, key=lambda x:(x[0],x[1]), reverse=True):
        partial = None
        try:
            if not 0 < entry['Size'] <= 1 << 20:
                raise ValueError('invalid manifest size')
            response = aws(['s3', 'cp', f's3://{bucket}/{entry["Key"]}', '-', '--only-show-errors'])
            if response.returncode:
                raise RuntimeError('manifest GET failed')
            if len(response.stdout) != entry['Size'] or hashlib.sha256(response.stdout).hexdigest() != manifest_sha:
                raise ValueError('manifest GET size/hash mismatch')
            manifest = json.loads(response.stdout)
            if manifest['schema'] != 'semaev.durable-checkpoint/v1':
                raise ValueError('unsupported manifest schema')
            if manifest['context'] != context or manifest['context_sha256'] != receipt['context_sha256']:
                raise ValueError('manifest belongs to a different frozen context')
            meta = manifest['snapshot']
            if meta['sequence'] != sequence or not re.fullmatch('[0-9a-f]{64}', meta['sha256']):
                raise ValueError('manifest sequence/hash invalid')
            if not 208 <= meta['bytes'] <= 5_000_000_000:
                raise ValueError('snapshot size outside qualified single-object interface')
            if any(meta[k] != context[k] for k in ('seed_sha256', 'binary_sha256')):
                raise ValueError('snapshot identity differs from frozen context')
            expected_uri = f's3://{bucket}/{root}/objects/{meta["sha256"]}.bin'
            if manifest['snapshot_uri'] != expected_uri:
                raise ValueError('snapshot URI escapes manifest content address')
            final = output_dir / f'restore-{sequence}-{meta["sha256"]}.bin'
            if final.exists():
                if inspect_snapshot(final) != meta:
                    raise ValueError('existing local restore differs')
            else:
                partial = output_dir / f'restore-{sequence}-{manifest_sha}-{uuid.uuid4().hex}.partial'
                download(expected_uri, partial, meta)
                if inspect_snapshot(partial) != meta:
                    raise ValueError('restored header differs from manifest')
                os.rename(partial, final)
                partial = None
                fd = os.open(output_dir, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            receipt.update(status='checkpoint_restored', manifest_uri=f's3://{bucket}/{entry["Key"]}',
                           manifest_sha256=manifest_sha, snapshot=meta, local_path=str(final))
            return receipt
        except Exception as error:
            receipt['rejected'].append(dict(manifest_key=entry['Key'], reason=str(error)))
            if partial is not None and partial.exists():
                # This is a failed transfer scratch file, never an accepted state.
                partial.unlink()
    return receipt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prefix', required=True)
    ap.add_argument('--context', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--receipt', type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    if a.receipt.exists():
        raise ValueError('restore receipt already exists; reconcile the recorded attempt')
    with (a.out/'restore.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = select(a.prefix, a.context, a.out.resolve())
        with a.receipt.open('x') as f:
            json.dump(result, f, sort_keys=True, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
    print(json.dumps(result), flush=True)
    return 0 if result['status']=='checkpoint_restored' else 3


if __name__=='__main__':
    raise SystemExit(main())
