"""Materialize an ephemeral, hash-checked export cache outside native seals.

Original native pointers/receipts/custody remain authoritative. This helper
never changes them, creates no sidecar, and does not construct relations. A
future cache miss may GET through artifact_store's configured reader; local
engineering tests use planted files/local stores and mocked missing storage.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from export_width import ROOT, REQUIRED, ep, read_package
sys.path.insert(0, str(ROOT/'tools'))
import artifact_store

EXPERIMENT = 'EXP-ECDLP-a9b6a5'
ORIGINALS = {
    'RUN-ECDLP-967315': ROOT/'experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315',
    'RUN-ECDLP-ea49a6': ROOT/'experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6'}


def prepare(run_dir, output_dir, *, software=False):
    run_dir, output_dir = Path(run_dir).resolve(), Path(output_dir).resolve()
    if output_dir.exists():
        raise ep.Refused('export-input cache destination already exists; no overwrite or incomplete-cache reuse')
    if run_dir == output_dir or run_dir in output_dir.parents or output_dir in run_dir.parents:
        raise ep.Refused('export-input cache must be outside and separate from the native seal')
    receipt = ep.read_json(run_dir/'execution-receipt.json')
    native_id = receipt.get('run_id')
    if not software:
        expected = ROOT/f'experiments/{EXPERIMENT}/export-inputs/{native_id}'
        if ORIGINALS.get(native_id) != run_dir or output_dir != expected:
            raise ep.Refused('only the fixed native width/reference run and export-cache paths are admissible')
    originals = {}
    for name in REQUIRED:
        path = artifact_store.resolve(run_dir/name) if name in ['raw-result.json', 'events.jsonl'] else run_dir/name
        if path is None or not path.is_file() or path.is_symlink():
            raise ep.Refused('required native file/stored form unavailable: '+name)
        originals[name] = dict(path=path, sha256=ep.sha256_file(path))
        if name in ['raw-result.json', 'events.jsonl'] and name in receipt.get('artifact_storage', {}):
            entry = receipt['artifact_storage'][name]
            if not artifact_store.stored_matches(run_dir, name, entry, receipt['artifact_sha256'][name]):
                raise ep.Refused('native stored-form commitment differs: '+name)
            if path.name.endswith('.blob.json'):
                pointer = artifact_store.read_pointer(path)
                if any(pointer.get(k) != entry.get(k) for k in
                       ['sha256', 'size', 'encoding', 'content_sha256', 'content_size', 'uri']):
                    raise ep.Refused('native pointer and receipt metadata differ: '+name)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    # Validate complete staged bytes before reserving a write-once final cache.
    with tempfile.TemporaryDirectory(prefix='.prepare-width-export-', dir=output_dir.parent) as scratch:
        staged = Path(scratch)
        for name in REQUIRED:
            source = run_dir/name
            try:
                content = artifact_store.read_bytes(source) if name in ['raw-result.json', 'events.jsonl'] else source.read_bytes()
            except (OSError, ValueError) as error:
                raise ep.Refused('required native hydration failed: '+name) from error
            observed = sha256(content).hexdigest()
            expected = originals[name]['sha256'] if name == 'execution-receipt.json' else receipt.get('artifact_sha256', {}).get(name)
            if observed != expected:
                raise ep.Refused('hydrated/native logical content hash differs: '+name)
            stored = originals[name]['path']
            if stored.name.endswith('.blob.json'):
                pointer = artifact_store.read_pointer(stored)
                if observed != pointer['content_sha256'] or len(content) != pointer['content_size']:
                    raise ep.Refused('hydrated pointer content size/hash differs: '+name)
            with (staged/name).open('xb') as stream:
                stream.write(content)
        read_package(staged, software=software)
        for record in originals.values():
            if ep.sha256_file(record['path']) != record['sha256']:
                raise ep.Refused('original native bytes changed during preparation')
        output_dir.mkdir(exist_ok=False)
        for name in REQUIRED:
            with (staged/name).open('rb') as source, (output_dir/name).open('xb') as target:
                shutil.copyfileobj(source, target)
    return dict(status='passed', native_run_id=native_id, source=str(run_dir), cache=str(output_dir),
                cache_is_ephemeral=True, files={name: ep.sha256_file(output_dir/name) for name in REQUIRED},
                original_stored_form_sha256={name: record['sha256'] for name, record in originals.items()},
                originals_unchanged=True, native_seal_modified=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--software', action='store_true')
    args = parser.parse_args(argv)
    os.environ.setdefault('CRYPTO_AR_BLOB_CACHE', '/tmp/prym-width-export-blob-cache')
    result = prepare(args.run_dir, args.output_dir, software=args.software)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ep.Refused, OSError, artifact_store.StoreError) as error:
        print('REFUSED: '+str(error), file=sys.stderr)
        raise SystemExit(2)
