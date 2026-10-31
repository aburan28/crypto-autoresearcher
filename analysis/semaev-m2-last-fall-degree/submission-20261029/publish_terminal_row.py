#!/usr/bin/env python3
"""Publish one completed non-certificate panel row with full readback."""
import argparse
import datetime
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def run(argv, **kwargs):
    return subprocess.run([str(x) for x in argv], check=True, **kwargs)


def write_once(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def pack(files, target):
    if target.exists():
        with tarfile.open(target, 'r:gz') as archive:
            members = {member.name: member for member in archive.getmembers()}
            if set(members) != set(files):
                raise ValueError('existing evidence member set mismatch')
            for name, path in files.items():
                member = members[name]
                if not member.isfile() or member.size != path.stat().st_size:
                    raise ValueError('existing evidence member size mismatch: ' + name)
                source = archive.extractfile(member)
                if source is None or hashlib.sha256(source.read()).hexdigest() != sha(path):
                    raise ValueError('existing evidence member hash mismatch: ' + name)
        return
    partial = target.with_name(target.name + '.partial')
    with partial.open('xb') as raw:
        with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode='w|') as archive:
                for name, path in sorted(files.items()):
                    info = tarfile.TarInfo(name)
                    info.size = path.stat().st_size
                    info.mode = 0o644
                    info.mtime = 0
                    with path.open('rb') as source:
                        archive.addfile(info, source)
    os.replace(partial, target)


def publish(args):
    result_path = args.result.resolve()
    attempt = result_path.parent
    result = json.loads(result_path.read_text())
    if result['status'] != 'closure_contains_one' or result['producer_contains_one'] != 1:
        raise ValueError('only terminal closure_contains_one rows are admitted')
    name = result['id']
    if name != result['parameters']['record']['name'] or '/' in name or name.startswith('.'):
        raise ValueError('invalid input identity')
    if args.inference.parent != attempt.parent or not args.inference.name.startswith('inference-'):
        raise ValueError('inference must belong to the same input')
    inference = json.loads(args.inference.read_text())
    if inference['id'] != name or inference['closure_result_canonical_sha256'] != hashlib.sha256(
            json.dumps(result, sort_keys=True).encode()).hexdigest():
        raise ValueError('inference does not bind the result')
    count = json.loads(args.count_result.read_text())
    if inference['count'] != count or count['status'] != 'completed' or count['parameters'] != result['parameters']['record']:
        raise ValueError('count does not bind the same input')
    if inference['last_fall_degree_lower_bound'] is not None:
        raise ValueError('non-certificate row cannot carry a lower-bound inference')
    if count['returncode'] != 0 or (args.count_result.parent / 'count.stdout.txt').read_text().strip() != str(count['ordered_solutions']):
        raise ValueError('exact count transcript mismatch')
    if f"W{result['parameters']['degree']}_one 1" not in (attempt / 'closure.stdout.txt').read_text():
        raise ValueError('closure transcript does not report one')
    for filename, entry in result['artifacts'].items():
        if Path(filename).name != filename:
            raise ValueError('unsafe artifact name')
        source = attempt / filename
        if source.stat().st_size != entry['bytes'] or sha(source) != entry['sha256']:
            raise ValueError('producer artifact mismatch: ' + filename)
    files = {'attempt/' + p.name: p for p in attempt.iterdir() if p.is_file()}
    files['inference/' + args.inference.name] = args.inference
    count_dir = args.count_result.parent
    for p in count_dir.iterdir():
        if p.is_file():
            files['count/' + p.name] = p
    args.archive.mkdir(parents=True, exist_ok=True)
    evidence = args.archive / (name + '.terminal.evidence.tar.gz')
    receipt = args.archive / (name + '.terminal.receipt.json')
    acknowledgement = args.archive / (name + '.terminal.publication.json')
    pack(files, evidence)
    expected_receipt = dict(schema='semaev.terminal-row-receipt/v1', id=name,
                            status=result['status'], ordered_solutions=count['ordered_solutions'],
                            result_sha256=sha(result_path), inference_sha256=sha(args.inference),
                            count_result_sha256=sha(args.count_result), evidence_sha256=sha(evidence),
                            evidence_bytes=evidence.stat().st_size,
                            scope='Terminal producer observation and exact count; no independently certified LFD bound.')
    if receipt.exists():
        if json.loads(receipt.read_text()) != expected_receipt:
            raise ValueError('existing receipt mismatch')
    else:
        write_once(receipt, expected_receipt)
    prior_ack = acknowledgement.exists()
    if prior_ack:
        old = json.loads(acknowledgement.read_text())
        listed = {entry['name']: entry['sha256'] for entry in old['files']}
        if old['evidence_sha256'] != sha(evidence) or listed != {
                evidence.name: sha(evidence), receipt.name: sha(receipt)}:
            raise ValueError('existing publication identity mismatch')
    release = json.loads(run(['gh', 'release', 'view', args.tag, '--repo', args.repo,
                              '--json', 'assets'], capture_output=True, text=True).stdout)
    existing = {asset['name'] for asset in release['assets']}
    run([args.python, args.repo_root / 'tools/artifacts/artifacts.py', 'push', evidence, '--jobs', '1'],
        cwd=args.repo_root, env={**os.environ, 'AWS_DEFAULT_REGION': args.region})
    checked = []
    with tempfile.TemporaryDirectory(prefix='semaev-terminal-readback-') as temporary:
        download = Path(temporary) / 'download'
        for file in (evidence, receipt):
            digest = sha(file)
            if file.name not in existing:
                run(['gh', 'release', 'upload', args.tag, file, '--repo', args.repo])
            url = f'https://github.com/{args.repo}/releases/download/{args.tag}/{file.name}'
            run(['curl', '-L', '--fail', '--silent', '--show-error', '--retry', '2',
                 '--max-time', '600', '-o', download, url])
            if sha(download) != digest:
                raise ValueError('anonymous readback hash mismatch: ' + file.name)
            store_uri = None
            if file == evidence:
                store_uri = f'{args.store.rstrip("/")}/sha256/{digest[:2]}/{digest}'
                run(['aws', 's3', 'cp', store_uri, download, '--region', args.region,
                     '--only-show-errors'])
                if sha(download) != digest:
                    raise ValueError('store readback hash mismatch')
            checked.append(dict(name=file.name, sha256=digest, bytes=file.stat().st_size,
                                anonymous_url=url, store_uri=store_uri))
    if not prior_ack:
        write_once(acknowledgement, dict(schema='semaev.terminal-publication-readback/v1', id=name,
                                         checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                         evidence_sha256=sha(evidence), files=checked,
                                         checks=['anonymous HTTPS GET and SHA256 for each asset',
                                                 'S3 GET and SHA256 for the evidence bundle']))
    if acknowledgement.name not in existing:
        run(['gh', 'release', 'upload', args.tag, acknowledgement, '--repo', args.repo])
    print(json.dumps({'id': name, 'publication': 'anonymous_and_store_readback_verified'}), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--inference', type=Path, required=True)
    p.add_argument('--count-result', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--repo-root', type=Path, required=True)
    p.add_argument('--repo', required=True)
    p.add_argument('--tag', required=True)
    p.add_argument('--store', default='s3://setec-astronomy-artifacts/store')
    p.add_argument('--region', default='us-east-2')
    p.add_argument('--python', default=sys.executable)
    args = p.parse_args()
    args.archive.mkdir(parents=True, exist_ok=True)
    with (args.archive / 'publication.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        publish(args)
