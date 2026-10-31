#!/usr/bin/env python3
"""Publish or fetch one immutable provisional-map chunk with complete S3 readback.

Hook API: ``map_chunk_store.py CHUNK`` publishes; ``map_chunk_store.py START END PATH``
fetches one chunk, exiting 2 only when no compatible manifest exists.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile


MAGIC = 0x31504D434C5153
HEADER = struct.Struct('<9Q')
CONTEXT_KEYS = ('request_sha256', 'protocol_sha256', 'seed_sha256', 'binary_sha256')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def aws(*args, stdout=None):
    result = subprocess.run(['aws', *map(str, args)], stdout=stdout or subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError('S3 command failed: ' + result.stderr.decode(errors='replace')[-1000:])
    return result.stdout


def context():
    path = Path(os.environ['SEMAEV_CHECKPOINT_CONTEXT'])
    data = path.read_bytes()
    value = json.loads(data)
    for key in CONTEXT_KEYS:
        if not re.fullmatch(r'[0-9a-f]{64}', value[key]):
            raise ValueError('invalid context digest: ' + key)
    return value, hashlib.sha256(data).hexdigest()


def destination():
    prefix = os.environ['SEMAEV_MAP_S3_PREFIX'].rstrip('/')
    match = re.fullmatch(r's3://([a-z0-9][a-z0-9.-]+)/([^\s]+)', prefix)
    if not match:
        raise ValueError('invalid map S3 prefix')
    return match.groups()


def inspect(path):
    path = Path(path)
    total = path.stat().st_size
    if total < HEADER.size + 96:
        raise ValueError('short map chunk')
    content = hashlib.sha256()
    with path.open('rb') as stream:
        raw = stream.read(HEADER.size + 64)
        if len(raw) != HEADER.size + 64:
            raise ValueError('short map header')
        magic, version, n, degree, high, work, start, end, width = HEADER.unpack(raw[:HEADER.size])
        if magic != MAGIC or version != 1 or not 3 <= n <= 52 or not 2 <= degree <= 5:
            raise ValueError('unsupported map format')
        if not 0 <= start < end <= high or width != (work + 63) // 64 or work < 1:
            raise ValueError('invalid map shape')
        if end - start > 65536 or total != HEADER.size + 64 + (end - start) * width * 8 + 32:
            raise ValueError('map chunk size mismatch')
        content.update(raw)
        remaining = total - len(raw) - 32
        while remaining:
            block = stream.read(min(1 << 20, remaining))
            if not block:
                raise ValueError('map chunk changed while reading')
            content.update(block)
            remaining -= len(block)
        if stream.read(32) != content.digest() or stream.read(1):
            raise ValueError('map chunk footer mismatch')
    return dict(n=n, degree=degree, high=high, work=work, start=start, end=end,
                width=width, bytes=total, sha256=sha(path),
                seed_sha256=raw[HEADER.size:HEADER.size + 32].hex(),
                binary_sha256=raw[HEADER.size + 32:HEADER.size + 64].hex())


def put_once(bucket, key, path):
    if Path(path).stat().st_size > 5_000_000_000:
        raise ValueError('map chunk exceeds qualified single-PUT interface')
    result = subprocess.run(['aws', 's3api', 'put-object', '--bucket', bucket,
                             '--key', key, '--body', str(path), '--if-none-match', '*'],
                            capture_output=True)
    if result.returncode and b'PreconditionFailed' not in result.stderr:
        raise RuntimeError('conditional map PUT failed: ' + result.stderr.decode(errors='replace')[-1000:])


def readback(bucket, key, expected_sha, expected_bytes):
    digest = hashlib.sha256()
    count = 0
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(['aws', 's3', 'cp', f's3://{bucket}/{key}', '-',
                                    '--only-show-errors'], stdout=subprocess.PIPE, stderr=errors)
        try:
            while True:
                block = process.stdout.read(1 << 20)
                if not block:
                    break
                digest.update(block)
                count += len(block)
            status = process.wait()
        except BaseException:
            process.kill()
            process.wait()
            raise
        finally:
            process.stdout.close()
        if status:
            raise RuntimeError('map readback failed')
    if count != expected_bytes or digest.hexdigest() != expected_sha:
        raise ValueError('map readback digest mismatch')


def publish(path):
    path = Path(path).resolve(strict=True)
    meta = inspect(path)
    if path.name != f'map-{meta["start"]}-{meta["end"]}.bin':
        raise ValueError('map chunk name/interval mismatch')
    ctx, ctx_sha = context()
    for key in ('seed_sha256', 'binary_sha256'):
        if meta[key] != ctx[key]:
            raise ValueError('map chunk context mismatch: ' + key)
    bucket, prefix = destination()
    object_key = f'{prefix}/objects/{meta["sha256"]}.bin'
    put_once(bucket, object_key, path)
    readback(bucket, object_key, meta['sha256'], meta['bytes'])
    manifest = dict(schema='semaev.provisional-map-chunk/v1', chunk=meta,
                    object_uri=f's3://{bucket}/{object_key}', context=ctx,
                    context_sha256=ctx_sha,
                    checks=['chunk footer SHA256', 'conditional immutable PUT',
                            'complete GET size and SHA256'])
    body = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    manifest_sha = hashlib.sha256(body).hexdigest()
    manifest_key = (f'{prefix}/manifests/{meta["start"]:010d}-{meta["end"]:010d}'
                    f'-{manifest_sha}.json')
    with tempfile.TemporaryDirectory(prefix='semaev-map-manifest-') as temporary:
        local = Path(temporary) / 'manifest.json'
        local.write_bytes(body)
        put_once(bucket, manifest_key, local)
    readback(bucket, manifest_key, manifest_sha, len(body))
    receipt = path.with_name(path.stem + '.publication.json')
    acknowledgement = dict(manifest_uri=f's3://{bucket}/{manifest_key}',
                           manifest_sha256=manifest_sha, chunk=meta,
                           scope='Provisional map state only; no mathematical acceptance')
    if receipt.exists():
        if json.loads(receipt.read_text()) != acknowledgement:
            raise ValueError('map publication receipt collision')
    else:
        with receipt.open('x') as stream:
            json.dump(acknowledgement, stream, sort_keys=True, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
    if os.environ.get('SEMAEV_MAP_PRUNE_LOCAL') == '1':
        path.unlink()
    print(json.dumps(acknowledgement), file=sys.stderr, flush=True)


def listed(bucket, key_prefix):
    token = None
    while True:
        args = ['s3api', 'list-objects-v2', '--bucket', bucket, '--prefix', key_prefix,
                '--output', 'json']
        if token:
            args += ['--continuation-token', token]
        page = json.loads(aws(*args))
        for item in page.get('Contents', []):
            yield item['Key']
        token = page.get('NextContinuationToken')
        if not token:
            break


def compatible_manifest(start, end):
    ctx, ctx_sha = context()
    bucket, prefix = destination()
    name_prefix = f'{prefix}/manifests/{start:010d}-{end:010d}-'
    candidates = []
    for key in listed(bucket, name_prefix):
        name = key.rsplit('/', 1)[-1]
        match = re.fullmatch(rf'{start:010d}-{end:010d}-([0-9a-f]{{64}})\.json', name)
        if not match:
            continue
        body = aws('s3', 'cp', f's3://{bucket}/{key}', '-', '--only-show-errors')
        if hashlib.sha256(body).hexdigest() != match.group(1):
            raise ValueError('map manifest digest mismatch')
        manifest = json.loads(body)
        if manifest['context'] == ctx and manifest['context_sha256'] == ctx_sha:
            candidates.append(manifest)
    if not candidates:
        return None
    digests = {item['chunk']['sha256'] for item in candidates}
    if len(digests) != 1:
        raise ValueError('conflicting map chunks for one context and interval')
    item = candidates[0]
    meta = item['chunk']
    if meta['start'] != start or meta['end'] != end or item['object_uri'] != (
            f's3://{bucket}/{prefix}/objects/{meta["sha256"]}.bin'):
        raise ValueError('map manifest object mismatch')
    return item


def fetch(start_text, end_text, target_text):
    start, end = int(start_text), int(end_text)
    target = Path(target_text).resolve()
    if target.exists() or target.name != f'map-{start}-{end}.bin':
        raise ValueError('map fetch target collision or name mismatch')
    item = compatible_manifest(start, end)
    if item is None:
        return 2
    meta = item['chunk']
    partial = target.with_name(target.name + '.partial')
    if partial.exists():
        partial.unlink()
    aws('s3', 'cp', item['object_uri'], partial, '--only-show-errors')
    try:
        if inspect(partial) != meta:
            raise ValueError('map fetched content mismatch')
        os.replace(partial, target)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    return 0


if __name__ == '__main__':
    try:
        if len(sys.argv) == 2:
            publish(sys.argv[1])
        elif len(sys.argv) == 4 and sys.argv[1] == 'probe':
            raise SystemExit(0 if compatible_manifest(int(sys.argv[2]), int(sys.argv[3])) else 2)
        elif len(sys.argv) == 4:
            raise SystemExit(fetch(*sys.argv[1:]))
        else:
            raise ValueError('usage: map_chunk_store.py CHUNK | START END PATH')
    except Exception as error:
        print(f'map chunk store refused: {error}', file=sys.stderr)
        raise SystemExit(1)
