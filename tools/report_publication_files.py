#!/usr/bin/env python3
"""Expand changed report manifests into verified, hydrated publication paths.

The reports-s3 workflow supplies a NUL-delimited Git path list. Large reports
are represented in Git by .artifacts.json, so their logical paths must be
included even though the hydrated bytes are ignored by Git. No network or
upload occurs here; canonical pull and verify precede this step.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile


def _path(value: str) -> PurePosixPath:
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or '\x00' in value:
        raise ValueError('publication paths must stay inside the repository')
    return p


def is_report(value: str) -> bool:
    p = _path(value)
    parts = p.parts
    return ((len(parts) >= 4 and parts[0] == 'experiments' and parts[2] == 'reports')
            or (len(parts) >= 3 and parts[:2] == ('docs', 'reports'))
            or (len(parts) >= 2 and parts[0] == 'research' and p.suffix == '.pdf'))


def _report_manifest(p: PurePosixPath) -> bool:
    return p.name == '.artifacts.json' and (
        is_report(str(p)) or (len(p.parts) >= 2 and p.parts[0] == 'research'))


def publication_files(initial: list[str], root: Path) -> list[str]:
    root = root.resolve()
    selected = set()
    for value in initial:
        p = _path(value)
        if is_report(str(p)):
            (root/str(p)).resolve().relative_to(root)
            selected.add(str(p))
        if not _report_manifest(p):
            continue
        manifest_path = root/str(p)
        manifest_path.resolve().relative_to(root)
        document = json.loads(manifest_path.read_text())
        entries = document.get('files') if isinstance(document, dict) else None
        if not isinstance(entries, dict):
            raise ValueError('report manifest must contain a files mapping')
        for name, entry in entries.items():
            if (not isinstance(name, str) or not name or name in {'.', '..'}
                    or PurePosixPath(name).name != name or '\x00' in name):
                raise ValueError('report manifest names must be single filenames')
            logical = str(p.parent/name)
            if not is_report(logical):
                continue
            if (not isinstance(entry, dict) or type(entry.get('bytes')) is not int
                    or entry['bytes'] < 0 or not isinstance(entry.get('sha256'), str)
                    or re.fullmatch('[0-9a-f]{64}', entry['sha256']) is None):
                raise ValueError('invalid report byte commitment')
            target = root/logical
            target.resolve().relative_to(root)
            if not target.is_file() or target.stat().st_size != entry['bytes']:
                raise ValueError('report is missing or its stored byte count differs: '+logical)
            digest = hashlib.sha256()
            with target.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024*1024), b''):
                    digest.update(chunk)
            if digest.hexdigest() != entry['sha256']:
                raise ValueError('report digest differs: '+logical)
            selected.add(logical)
    return sorted(selected)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--files', type=Path, required=True, help='NUL list, replaced atomically')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    values = [os.fsdecode(p) for p in args.files.read_bytes().split(b'\x00') if p]
    names = publication_files(values, args.root)
    data = b''.join(os.fsencode(p)+b'\x00' for p in names)
    fd, temporary = tempfile.mkstemp(prefix='.report-paths-', dir=args.files.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.replace(temporary, args.files)
    finally:
        Path(temporary).unlink(missing_ok=True)
    print(json.dumps(dict(publication_files=len(names))))


if __name__ == '__main__':
    main()
