#!/usr/bin/env python3
"""Publish completed certificates additively, then hash anonymous downloads.

Run separately from the frozen computation driver. Existing release assets
are never replaced. A publication acknowledgement is written only after
both public bytes and the canonical store bytes have been downloaded and
hashed. The release must already exist; creating a new public destination
is a separate, explicit operation.
"""
import argparse
import datetime
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

from certificate_campaign import digest, save


def pack_certificate(source, target):
    if not target.exists():
        tmp = target.with_suffix(target.suffix + '.partial')
        with open(tmp, 'wb') as raw:
            with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as out:
                with open(source, 'rb') as inp:
                    shutil.copyfileobj(inp, out, length=1 << 20)
        os.replace(tmp, target)
    h = hashlib.sha256()
    with gzip.open(target, 'rb') as inp:
        for block in iter(lambda: inp.read(1 << 20), b''):
            h.update(block)
    if h.hexdigest() != digest(source):
        raise ValueError('compressed certificate does not match retained original')


def pack_evidence(attempt, campaign, item, target):
    if target.exists():
        return
    files = {f'attempt/{p.name}': p for p in attempt.iterdir()
             if p.is_file() and p.name != 'certificate.bin'}
    for p in attempt.parent.glob('inference-*.json'):
        files['inference/' + p.name] = p
    name = item['parameters']['record']['name']
    for p in (campaign / 'counts' / name).glob('attempt-*/*'):
        if p.is_file():
            files['count/' + p.parent.name + '/' + p.name] = p
    tmp = target.with_suffix(target.suffix + '.partial')
    with open(tmp, 'wb') as raw:
        with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode='w|') as archive:
                for name, path in sorted(files.items()):
                    info = tarfile.TarInfo(name)
                    info.size = path.stat().st_size
                    info.mode = 0o644
                    with open(path, 'rb') as inp:
                        archive.addfile(info, inp)
    os.replace(tmp, target)


def run(argv, **kwargs):
    return subprocess.run([str(x) for x in argv], check=True, **kwargs)


def public_readback(url, expected, temp):
    run(['curl', '-L', '--fail', '--silent', '--show-error', '--retry', '2',
         '--max-time', '600', '-o', temp, url])
    if digest(temp) != expected:
        raise ValueError('anonymous download hash mismatch: ' + url)


def publish(args):
    args.archive.mkdir(parents=True, exist_ok=True)
    with open(args.archive / 'publication.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        info = json.loads(run(['gh', 'release', 'view', args.tag, '--repo', args.repo,
                              '--json', 'assets,url'], capture_output=True, text=True).stdout)
        assets = {a['name']: a for a in info['assets']}
        eligible = []
        for campaign in args.run_roots:
            for path in sorted(campaign.glob('*/attempt-*/result.json')):
                result = json.loads(path.read_text())
                if result['status'] != 'certificate_verified':
                    continue
                # A fresh result is publishable with its inference record. Do
                # not race the short gap between closure and inference writes.
                if (campaign / 'plan.json').exists() and not list(path.parent.parent.glob('inference-*.json')):
                    continue
                name = result['id']
                acknowledgement = args.archive / (name + '.publication.json')
                if acknowledgement.exists():
                    old = json.loads(acknowledgement.read_text())
                    if old['certificate_sha256'] != result['certificate_sha256']:
                        raise ValueError('identity collision with an earlier publication')
                    continue
                for filename, entry in result['artifacts'].items():
                    source = path.parent / filename
                    if source.stat().st_size != entry['bytes'] or digest(source) != entry['sha256']:
                        raise ValueError('producer artifact changed: ' + str(source))
                certificate = args.archive / f'{name}.D{result["parameters"]["degree"]}.cert.gz'
                pack_certificate(path.parent / 'certificate.bin', certificate)
                receipt = args.archive / (name + '.receipt.json')
                if not receipt.exists():
                    save(receipt, dict(schema='semaev.published-certificate/v1', result=result,
                         checker_stdout=(path.parent / 'check.stdout.txt').read_text(),
                         checker_stderr=(path.parent / 'check.stderr.txt').read_text(),
                         compressed_sha256=digest(certificate), compressed_bytes=certificate.stat().st_size))
                old = json.loads(receipt.read_text())
                if old['result'] != result or old['compressed_sha256'] != digest(certificate):
                    raise ValueError('receipt differs from retained computation')
                evidence = args.archive / (name + '.evidence.tar.gz')
                pack_evidence(path.parent, campaign, result, evidence)
                eligible.append((name, result, [certificate, receipt, evidence], acknowledgement))
        if not eligible:
            print('No unpublished completed certificates.', flush=True)
            return
        # All writes go through the repository's conditional content-addressed
        # store helper. Its HEAD check is followed below by a complete GET/hash.
        store_files = [f for _, _, files, _ in eligible for f in files if f.suffix == '.gz']
        run([args.python, args.repo_root / 'tools/artifacts/artifacts.py', 'push', *store_files, '--jobs', '2'],
            cwd=args.repo_root, env={**os.environ, 'AWS_DEFAULT_REGION': args.region})
        with tempfile.TemporaryDirectory(prefix='semaev-public-readback-') as temporary:
            temp = Path(temporary) / 'download'
            for name, result, files, acknowledgement in eligible:
                verified = []
                for file in files:
                    sha = digest(file)
                    if file.name not in assets:
                        run(['gh', 'release', 'upload', args.tag, file, '--repo', args.repo])
                    url = f'https://github.com/{args.repo}/releases/download/{args.tag}/{file.name}'
                    public_readback(url, sha, temp)
                    if file.name.endswith('.cert.gz'):
                        h = hashlib.sha256()
                        with gzip.open(temp, 'rb') as inp:
                            for block in iter(lambda: inp.read(1 << 20), b''):
                                h.update(block)
                        if h.hexdigest() != result['certificate_sha256']:
                            raise ValueError('public decompressed certificate hash mismatch')
                    store_uri = None
                    if file.suffix == '.gz':
                        store_uri = f'{args.store.rstrip("/")}/sha256/{sha[:2]}/{sha}'
                        run(['aws', 's3', 'cp', store_uri, temp, '--region', args.region,
                             '--only-show-errors'])
                        if digest(temp) != sha:
                            raise ValueError('canonical store download hash mismatch')
                    verified.append(dict(name=file.name, sha256=sha, bytes=file.stat().st_size,
                                         anonymous_url=url, store_uri=store_uri))
                save(acknowledgement, dict(schema='semaev.publication-readback/v1', id=name,
                     checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     certificate_sha256=result['certificate_sha256'], files=verified,
                     checks=['anonymous HTTPS GET and SHA256 for every asset',
                             'gzip decompression and original certificate SHA256',
                             'S3 GET and SHA256 for each store-backed asset']))
                run(['gh', 'release', 'upload', args.tag, acknowledgement, '--repo', args.repo])
                print(json.dumps({'id': name, 'publication': 'anonymous_and_store_readback_verified'}), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-roots', type=Path, nargs='+', required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--repo-root', type=Path, required=True)
    p.add_argument('--repo', required=True)
    p.add_argument('--tag', required=True)
    p.add_argument('--store', default='s3://setec-astronomy-artifacts/store')
    p.add_argument('--region', default='us-east-2')
    p.add_argument('--python', default=sys.executable)
    publish(p.parse_args())
