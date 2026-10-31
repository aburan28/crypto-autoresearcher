#!/usr/bin/env python3
"""Project a checked local D4 attempt into the additive certificate publisher.

The source attempt and collection remain authoritative. This creates a separate,
write-once publication view and never changes the scientific result or inventory.
"""
import argparse
import json
import os
from pathlib import Path
import shutil

from collect_panel_result import digest, read, require, verify


def save(path, obj):
    with path.open('x') as stream:
        json.dump(obj, stream, indent=2, sort_keys=True)
        stream.write('\n')


def normalize(plan_path, protocol_path, collection, destination):
    root, result, checked = verify(plan_path, protocol_path)
    require(result['status'] == 'certificate_verified', 'No accepted certificate')
    manifest = read(collection / 'manifest.json')
    require(manifest['schema'] == 'semaev.panel-collection/v1', 'Wrong collection schema')
    require(manifest['id'] == checked['id'] and
            manifest['result_sha256'] == checked['result_sha256'] and
            manifest['plan_sha256'] == checked['plan_sha256'] and
            manifest['protocol_file_sha256'] == checked['protocol_file_sha256'],
            'Collection does not bind this attempt')
    archive = collection / 'raw-evidence.tar.gz'
    require(digest(archive) == manifest['raw_archive_sha256'], 'Collection archive mismatch')
    attempt = root / 'attempt-001'
    request = read(attempt / 'request.json')
    require(result['certificate_sha256'] == digest(attempt / 'certificate.bin'),
            'Certificate changed since collection')
    require(destination.name == 'attempt-001' and destination.parent.name == request['id'],
            'Destination must be ID/attempt-001 for the publisher')
    require(not destination.resolve().is_relative_to(root.resolve()),
            'Publication destination is inside raw attempt')
    destination.mkdir(parents=True, exist_ok=False)
    for source in sorted(attempt.iterdir()):
        if source.is_file() and source.name not in {'result.json', 'certificate.bin'}:
            shutil.copy2(source, destination / source.name)
    os.link(attempt / 'certificate.bin', destination / 'certificate.bin')
    shutil.copy2(attempt / 'result.json', destination / 'worker-result.json')
    os.link(archive, destination / 'complete-raw-evidence.tar.gz')
    provenance = {
        'original_result': str(attempt / 'result.json'),
        'original_result_sha256': checked['result_sha256'],
        'original_request_sha256': digest(attempt / 'request.json'),
        'collection_manifest': str(collection / 'manifest.json'),
        'collection_manifest_sha256': digest(collection / 'manifest.json'),
        'frozen_plan_sha256': checked['plan_sha256'],
        'protocol_file_sha256': checked['protocol_file_sha256'],
        'scope': 'Publication-format projection only; original worker evidence unchanged',
    }
    save(destination / 'origin.json', provenance)
    projected = {
        'schema': 'semaev.panel-publication/v1',
        'id': request['id'],
        'status': 'certificate_verified',
        'parameters': {'degree': 4, 'chain': False, 'record': request['record']},
        'certificate_sha256': result['certificate_sha256'],
        'certified_codimension_lower_bound': result['certified_codimension_lower_bound'],
        'exact_solutions': result['exact_solutions'],
        'last_fall_degree_lower_bound': checked['last_fall_degree_lower_bound'],
        'provenance': provenance,
        'artifacts': {source.name: {'bytes': source.stat().st_size,
                                    'sha256': digest(source)}
                      for source in sorted(destination.iterdir()) if source.is_file()},
    }
    save(destination / 'result.json', projected)
    return projected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--collection', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    result = normalize(args.plan, args.protocol, args.collection, args.destination)
    print(json.dumps({key: result[key] for key in
                      ('id', 'certified_codimension_lower_bound',
                       'exact_solutions', 'last_fall_degree_lower_bound')}, indent=2))


if __name__ == '__main__':
    main()
