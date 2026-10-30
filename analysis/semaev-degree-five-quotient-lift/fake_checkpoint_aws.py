#!/usr/bin/env python3
"""Filesystem-only AWS CLI double for frozen checkpoint software controls."""
import json
import os
from pathlib import Path
import sys


def main():
    args = sys.argv[1:]
    root = Path(os.environ['FAKE_CHECKPOINT_STORE']).resolve()
    fault = os.environ.get('FAKE_CHECKPOINT_FAULT', '')
    def option(name):
        return args[args.index(name)+1]
    def object_path(bucket, key):
        p = (root/bucket/key).resolve()
        if root not in p.parents:
            raise ValueError('fake store traversal')
        return p
    def fail(message):
        print(message, file=sys.stderr)
        return 1
    if args[:2] == ['s3api','put-object']:
        key = option('--key'); path = object_path(option('--bucket'), key)
        kind = 'manifest' if '/manifests/' in key else 'object'
        if fault == kind+'_put':
            return fail('Injected interrupted '+kind+' PUT')
        assert option('--if-none-match') == '*'
        if path.exists():
            return fail('PreconditionFailed')
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as f:
            f.write(Path(option('--body')).read_bytes())
        print('{}')
        return 0
    if args[:2] == ['s3','cp']:
        assert args[3] == '-'
        bucket, key = args[2].removeprefix('s3://').split('/',1)
        kind = 'manifest' if '/manifests/' in key else 'object'
        if fault == kind+'_get':
            return fail('Injected interrupted '+kind+' GET')
        path = object_path(bucket,key)
        if not path.exists():
            return fail('NoSuchKey')
        data = path.read_bytes()
        if fault == kind+'_corrupt_get':
            data = data[:-1]
        sys.stdout.buffer.write(data)
        return 0
    if args[:2] == ['s3api','list-objects-v2']:
        bucket, prefix = option('--bucket'), option('--prefix')
        base = root/bucket
        entries = [dict(Key=str(p.relative_to(base)), Size=p.stat().st_size)
                   for p in base.rglob('*') if p.is_file() and str(p.relative_to(base)).startswith(prefix)] if base.exists() else []
        print(json.dumps(dict(Contents=entries, IsTruncated=fault=='truncated_listing')))
        return 0
    return fail('Unsupported fake AWS command')


if __name__=='__main__':
    raise SystemExit(main())
