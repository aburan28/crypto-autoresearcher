#!/usr/bin/env python3
"""Synchronous immutable S3 checkpoint publication hook; qualification pending.

Environment: SEMAEV_CHECKPOINT_S3_PREFIX, SEMAEV_CHECKPOINT_CONTEXT (JSON path),
SEMAEV_CHECKPOINT_DIR. Optional SEMAEV_CHECKPOINT_PRUNE_LOCAL=1 removes only the
submitted snapshot after both complete readbacks pass. Never removes S3 data.
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


def aws(argv, **kwargs):
    return subprocess.run(['aws', *map(str, argv)], capture_output=True, **kwargs)


def put_once(bucket, key, path):
    # A relation snapshot for the selected n47 input is below the 5 GiB PUT
    # limit. Larger snapshots require a separately qualified multipart path.
    if path.stat().st_size > 5_000_000_000:
        raise ValueError('checkpoint exceeds qualified single-PUT interface')
    p = aws(['s3api', 'put-object', '--bucket', bucket, '--key', key,
             '--body', path, '--if-none-match', '*'])
    if p.returncode and b'PreconditionFailed' not in p.stderr:
        raise RuntimeError('conditional S3 PUT failed: ' + p.stderr.decode(errors='replace'))
    # Existing object is allowed only if the following full GET hash matches.


def readback(bucket, key, expected_sha, expected_bytes):
    h, count = hashlib.sha256(), 0
    with tempfile.TemporaryFile() as errors:
        p = subprocess.Popen(['aws', 's3', 'cp', f's3://{bucket}/{key}', '-',
                              '--only-show-errors'], stdout=subprocess.PIPE, stderr=errors)
        try:
            while True:
                b = p.stdout.read(1 << 20)
                if not b:
                    break
                h.update(b)
                count += len(b)
            rc = p.wait()
        except BaseException:
            p.kill()
            p.wait()
            raise
        finally:
            p.stdout.close()
        if rc:
            raise RuntimeError('S3 checkpoint readback failed')
    if count != expected_bytes or h.hexdigest() != expected_sha:
        raise ValueError('S3 checkpoint readback content mismatch')


def inspect_snapshot(path):
    size = path.stat().st_size
    if size < 208:
        raise ValueError('short checkpoint')
    content_hash, full_hash = hashlib.sha256(), hashlib.sha256()
    with path.open('rb') as f:
        header = f.read(176)
        words = struct.unpack('<14Q', header[:112])
        if words[0] != 0x315450434c5153 or words[1] != 1:
            raise ValueError('unsupported checkpoint format')
        work, rank = words[4], words[12]
        if not work or rank > work or size != 208 + rank * ((work+63)//64) * 8:
            raise ValueError('checkpoint shape mismatch')
        f.seek(0)
        remaining = size - 32
        while remaining:
            b = f.read(min(1 << 20, remaining))
            if not b:
                raise ValueError('checkpoint changed during read')
            content_hash.update(b)
            full_hash.update(b)
            remaining -= len(b)
        footer = f.read(32)
        if content_hash.digest() != footer or f.read(1):
            raise ValueError('checkpoint footer mismatch')
        full_hash.update(footer)
    return dict(bytes=size, sha256=full_hash.hexdigest(), seed_sha256=header[112:144].hex(),
                binary_sha256=header[144:176].hex(), sequence=words[13], phase=words[8],
                next_variable=words[9], next_row=words[10], closure_rounds=words[11],
                relation_rank=rank, working_coordinates=work, chunk_rows=words[7])


def main():
    if len(sys.argv) != 2:
        raise ValueError('usage: publish_lift_checkpoint.py SNAPSHOT')
    snapshot = Path(sys.argv[1]).resolve(strict=True)
    directory = Path(os.environ['SEMAEV_CHECKPOINT_DIR']).resolve(strict=True)
    if snapshot.parent != directory or not re.fullmatch(r'checkpoint-[1-9][0-9]*\.bin', snapshot.name):
        raise ValueError('snapshot is outside the declared checkpoint directory')
    prefix = os.environ['SEMAEV_CHECKPOINT_S3_PREFIX'].rstrip('/')
    match = re.fullmatch(r's3://([a-z0-9][a-z0-9.-]+)/([^\s]+)', prefix)
    if not match:
        raise ValueError('invalid checkpoint S3 prefix')
    bucket, key_prefix = match.groups()
    context_bytes = Path(os.environ['SEMAEV_CHECKPOINT_CONTEXT']).read_bytes()
    context = json.loads(context_bytes)
    for key in ('request_sha256', 'protocol_sha256', 'seed_sha256', 'binary_sha256'):
        if not re.fullmatch('[0-9a-f]{64}', context[key]):
            raise ValueError('invalid checkpoint context digest: ' + key)
    metadata = inspect_snapshot(snapshot)
    if any(metadata[key] != context[key] for key in ('seed_sha256', 'binary_sha256')):
        raise ValueError('checkpoint does not match frozen request context')
    if snapshot.name != f'checkpoint-{metadata["sequence"]}.bin':
        raise ValueError('checkpoint sequence/name mismatch')
    key = f'{key_prefix}/objects/{metadata["sha256"]}.bin'
    put_once(bucket, key, snapshot)
    readback(bucket, key, metadata['sha256'], metadata['bytes'])
    manifest = dict(schema='semaev.durable-checkpoint/v1', snapshot=metadata,
        snapshot_uri=f's3://{bucket}/{key}', context=context,
        context_sha256=hashlib.sha256(context_bytes).hexdigest(),
        checks=['snapshot footer SHA256', 'conditional immutable PUT', 'complete GET size and SHA256'])
    data = (json.dumps(manifest, sort_keys=True, indent=2)+'\n').encode()
    sha = hashlib.sha256(data).hexdigest()
    manifest_key = f'{key_prefix}/manifests/{metadata["sequence"]:020d}-{sha}.json'
    # Tiny local manifest only; readback of matrix bytes is streamed to avoid
    # an additional full-size disk copy.
    with tempfile.TemporaryDirectory(prefix='semaev-checkpoint-manifest-') as td:
        local = Path(td)/'manifest.json'
        local.write_bytes(data)
        put_once(bucket, manifest_key, local)
        readback(bucket, manifest_key, sha, len(data))
    # No mutable latest pointer: restore enumerates complete compatible manifests.
    receipt = directory/(snapshot.stem+'.publication.json')
    ack = dict(manifest_uri=f's3://{bucket}/{manifest_key}', manifest_sha256=sha,
               snapshot=metadata, scope='Durable state only; no mathematical acceptance')
    if receipt.exists():
        if json.loads(receipt.read_text()) != ack:
            raise ValueError('local publication receipt collision')
    else:
        with receipt.open('x') as f:
            json.dump(ack, f, sort_keys=True, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
    if os.environ.get('SEMAEV_CHECKPOINT_PRUNE_LOCAL') == '1':
        snapshot.unlink()
    # Keep the producer's stdout a single mathematical result JSON object.
    print(json.dumps(ack), file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
