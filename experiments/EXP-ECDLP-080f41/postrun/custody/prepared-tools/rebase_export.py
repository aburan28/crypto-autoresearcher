#!/usr/bin/env python3
"""Create a fresh path-only experiment.export/v1 derivative after completion.

No experiment code is imported or executed. The source export is never edited.
This checks representation/path preservation, not protocol or file validity;
run the repository's unchanged check-export --verify-files at the new location.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
from typing import Any

SCHEMA = 'experiment.export/v1'
URI = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*://')


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'duplicate JSON key: ' + key)
        value[key] = item
    return value


def nonfinite(value):
    raise ValueError('nonfinite JSON value: ' + value)


def finite(value):
    number = float(value)
    require(math.isfinite(number), 'nonfinite JSON float')
    return number


def loads(data: bytes) -> Any:
    return json.loads(data, object_pairs_hook=unique, parse_constant=nonfinite, parse_float=finite)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local_absolute(path: str | Path, base: str | Path) -> str:
    require(isinstance(path, (str, Path)), 'local path must be text')
    path = str(path)
    require(bool(path) and '\x00' not in path and URI.match(path) is None,
            'local path must be nonempty and must not be a URI')
    return os.path.abspath(os.path.join(os.path.abspath(str(base)), path))


def path_slots(export: dict) -> list[tuple[dict, str, str]]:
    """Only schema-defined base-relative fields, including reviews_dir.

    backend_record is deliberately opaque, as required by experiment.export/v1.
    """
    require(type(export) is dict and export.get('schema') == SCHEMA,
            'expected experiment.export/v1 object')
    slots = []

    def obj(value, pointer):
        require(type(value) is dict, pointer + ' must be an object')
        return value

    def refs(value, pointer):
        require(type(value) is list, pointer + ' must be an array')
        for index, reference in enumerate(value):
            reference = obj(reference, pointer + '/' + str(index))
            require('path' in reference, pointer + '/' + str(index) + '/path missing')
            slots.append((reference, 'path', pointer + '/' + str(index) + '/path'))

    protocol = obj(export.get('protocol'), '/protocol')
    require('path' in protocol, '/protocol/path missing')
    slots.append((protocol, 'path', '/protocol/path'))
    host = obj(export.get('host'), '/host')
    require('path' in host, '/host/path missing')
    if host['path'] is not None:
        slots.append((host, 'path', '/host/path'))
    refs(export.get('files'), '/files')
    require(type(export.get('runs')) is list, '/runs must be an array')
    for index, run in enumerate(export['runs']):
        run = obj(run, '/runs/' + str(index))
        refs(run.get('artifacts'), '/runs/' + str(index) + '/artifacts')
    analysis = obj(export.get('analysis'), '/analysis')
    require('script' in analysis, '/analysis/script missing')
    if analysis['script'] is not None:
        reference = obj(analysis['script'], '/analysis/script')
        require('path' in reference, '/analysis/script/path missing')
        slots.append((reference, 'path', '/analysis/script/path'))
    refs(analysis.get('outputs'), '/analysis/outputs')
    require('reviews_dir' in export, '/reviews_dir missing')
    slots.append((export, 'reviews_dir', '/reviews_dir'))
    return slots


def rebase_export(export: dict, source_base: str | Path,
                  destination_base: str | Path) -> tuple[dict, list[dict]]:
    """Pure value transformation; does not read referenced files or live outputs."""
    result = copy.deepcopy(export)
    bindings = []
    source_base = os.path.abspath(str(source_base))
    destination_base = os.path.abspath(str(destination_base))
    for owner, key, pointer in path_slots(result):
        before = owner[key]
        require(type(before) is str, pointer + ' must be text')
        target = local_absolute(before, source_base)
        after = Path(os.path.relpath(target, destination_base)).as_posix()
        require(local_absolute(after, destination_base) == target,
                pointer + ' target changed')
        owner[key] = after
        bindings.append({'json_pointer': pointer, 'before': before, 'after': after,
                         'lexical_absolute_target': target, 'changed': before != after})
    return result, bindings


def completion_guard(path: Path) -> tuple[dict, str]:
    require(path.is_file() and not path.is_symlink(),
            'completion record must be a regular non-symlink file')
    data = path.read_bytes()
    value = loads(data)
    require(type(value) is dict and type(value.get('returncode')) is int,
            'completion record lacks actual integer returncode')
    require(type(value.get('finished_at')) is str,
            'completion record lacks actual finished_at; do not read live export')
    finished = dt.datetime.fromisoformat(value['finished_at'].replace('Z', '+00:00'))
    require(finished.tzinfo is not None, 'completion timestamp must be timezone-aware')
    return value, digest(data)


def write_derivative(source: Path, destination: Path, provenance_path: Path,
                     completion_record: Path) -> dict:
    """Write fresh administrative files; root calls only after actual completion."""
    completion, completion_sha = completion_guard(completion_record)
    source = Path(source).absolute()
    destination = Path(destination).absolute()
    provenance_path = Path(provenance_path).absolute()
    require(source != destination and source != provenance_path and
            destination != provenance_path, 'source, derivative and provenance must differ')
    require(source.is_file() and not source.is_symlink(),
            'source export must be a regular non-symlink file')
    require(not destination.exists() and not destination.is_symlink() and
            not provenance_path.exists() and not provenance_path.is_symlink(),
            'fresh derivative and provenance paths required')
    original = source.read_bytes()
    value = loads(original)
    rebased, bindings = rebase_export(value, source.parent, destination.parent)
    encoded = (json.dumps(rebased, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()
    require(source.read_bytes() == original, 'source export changed while preparing derivative')
    provenance = {
        'schema': 'classical.ecdlp.path-rebased-export-provenance/v1',
        'source_path': str(source), 'source_sha256': digest(original),
        'destination_path': str(destination), 'destination_sha256': digest(encoded),
        'completion_record_path': str(completion_record.absolute()),
        'completion_record_sha256': completion_sha,
        'actual_source_command_returncode': completion['returncode'],
        'actual_source_finished_at': completion['finished_at'],
        'transformation': 'Only schema-defined base-relative path fields; all nonpath values, IDs, outcomes, counts, hashes, seeds and opaque backend_record preserved.',
        'symlink_resolution': 'No referenced file is read or symlink-resolved by the transformation. Lexical absolute targets are preserved; actual file verification is separate.',
        'formal_path_bindings': bindings,
        'source_export_unchanged': True,
        'scientific_measurement_or_trial': False,
        'actual_schema_protocol_and_file_validation': 'Not performed by this helper; run unchanged check-export --verify-files at the actual destination.',
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(encoded)
    with provenance_path.open('xb') as stream:
        stream.write((json.dumps(provenance, indent=2, sort_keys=True) + '\n').encode())
    require(source.read_bytes() == original, 'source export changed during derivative write')
    return provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--provenance', type=Path, required=True)
    parser.add_argument('--completion-record', type=Path, required=True)
    args = parser.parse_args()
    value = write_derivative(args.source, args.destination, args.provenance,
                             args.completion_record)
    print(json.dumps({'source_sha256': value['source_sha256'],
                      'derivative_sha256': value['destination_sha256'],
                      'formal_path_fields': len(value['formal_path_bindings']),
                      'scientific_validation_performed': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
