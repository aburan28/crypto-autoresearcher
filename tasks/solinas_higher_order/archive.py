#!/usr/bin/env python3
"""Lossless feature/record export and checksum-verified standalone data bundle."""
import argparse
import gzip
import hashlib
import json
import zipfile
from collections import defaultdict
from pathlib import Path
from research import canonical, digest, immutable, check_source


def export_records(root):
    root = Path(root); groups = defaultdict(list)
    for path in sorted((root/'records').glob('*.json')):
        record = json.loads(path.read_text()); job = record['job']
        key = job['case']+'-'+job.get('kind', job.get('mode', 'features'))
        groups[key].append(path.read_bytes())
    if not groups: raise ValueError('No records to archive')
    manifest = {'schema': 1, 'encoding': 'Lossless original canonical JSON records in gzip JSONL; original raw references preserved', 'shards': []}
    for key, values in sorted(groups.items()):
        data = gzip.compress(b''.join(values), compresslevel=6, mtime=0)
        path = root/'record-shards'/(key+'.jsonl.gz'); immutable(path, data)
        manifest['shards'].append({'path': str(path.relative_to(root)), 'records': len(values), 'bytes': len(data), 'sha256': digest(path)})
    immutable(root/'record-shards.json', canonical(manifest))
    return manifest


def archive(output, bundle=None):
    output = Path(output).resolve(); check_source(output)
    if not (output/'analysis.json').exists(): raise ValueError('Completed analyzed run required')
    export_records(output); export_records(output/'discovery')
    files = []
    for path in sorted(output.rglob('*')):
        if not path.is_file(): continue
        relative = path.relative_to(output)
        if any(part in ('records', 'build', '__pycache__', 'ml-models') for part in relative.parts): continue
        if path.name == 'runner.lock' or path.name.startswith('.') or path.suffix in ('.tmp', '.log'): continue
        if path.name == 'dataset-inventory.json': continue
        files.append(path)
    inventory = {'schema': 1, 'run_name': output.name, 'files': [{'path': str(p.relative_to(output)), 'bytes': p.stat().st_size,
                 'sha256': digest(p)} for p in files], 'excluded': 'Duplicate uncompressed records; build/cache; fitted ML binaries (locked training exactly reproducible); auxiliary mutable invocation logs',
                 'scope': 'All measured raw coordinates, lossless records/discovery features, inputs, source, environment, analysis, receipts'}
    immutable(output/'dataset-inventory.json', canonical(inventory))
    files.append(output/'dataset-inventory.json')
    if bundle:
        bundle = Path(bundle).resolve()
        if bundle.exists(): raise ValueError('Existing dataset bundle must not be overwritten')
        with zipfile.ZipFile(bundle, 'x', compression=zipfile.ZIP_STORED, allowZip64=True) as archive_file:
            for path in files:
                name = output.name+'/'+str(path.relative_to(output))
                info = zipfile.ZipInfo(name, date_time=(2026, 10, 12, 0, 0, 0)); info.compress_type = zipfile.ZIP_STORED
                info.external_attr = 0o644 << 16
                with path.open('rb') as src, archive_file.open(info, 'w', force_zip64=True) as dst:
                    while chunk := src.read(1 << 20): dst.write(chunk)
        # ZIP CRC and every entry's SHA are validated against the inventory.
        with zipfile.ZipFile(bundle) as archive_file:
            if archive_file.testzip() is not None: raise ValueError('ZIP CRC failed')
            for item in inventory['files']:
                with archive_file.open(output.name+'/'+item['path']) as stream:
                    h = hashlib.sha256()
                    while chunk := stream.read(1 << 20): h.update(chunk)
                if h.hexdigest() != item['sha256']: raise ValueError('Bundled content hash differs')
        receipt = {'schema': 1, 'bundle_name': bundle.name, 'bytes': bundle.stat().st_size, 'sha256': digest(bundle),
                   'inventory_sha256': digest(output/'dataset-inventory.json'), 'zip_crc_and_all_inventory_sha256': 'passed'}
        immutable(output.parent.parent/'publication'/(output.name+'-bundle.json'), canonical(receipt))
        print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--bundle', type=Path); args = parser.parse_args(); archive(args.output, args.bundle)
