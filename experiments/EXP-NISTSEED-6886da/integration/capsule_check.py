"""Separate capsule reader: no extraction and no trust in producer file lists."""
import hashlib
import json
import tarfile
from pathlib import Path, PurePosixPath


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check(output: Path):
    manifest_path = output / 'raw-artifact-inventory.json'
    capsule_path = output / 'raw-artifacts.tar.gz'
    if any(p.is_symlink() or not p.is_file() for p in (manifest_path, capsule_path)):
        raise ValueError('missing or unsafe capsule/inventory')
    manifest = json.loads(manifest_path.read_text())
    data = capsule_path.read_bytes()
    if manifest.get('schema') != 'crypto.autoresearch.ecpp_raw_capsule.v1' or manifest.get('capsule') != capsule_path.name:
        raise ValueError('capsule schema/name mismatch')
    if manifest.get('bytes') != len(data) or manifest.get('sha256') != sha(data):
        raise ValueError('capsule digest/size mismatch')
    actual = {}
    with tarfile.open(capsule_path, mode='r:gz') as archive:
        for entry in archive:
            name = PurePosixPath(entry.name)
            if entry.name in actual or name.is_absolute() or '..' in name.parts or str(name) != entry.name or not entry.isfile():
                raise ValueError('duplicate, unsafe or non-regular capsule member')
            if not (entry.name.startswith('legacy-child/') or entry.name in ('driver.stdout.log','driver.stderr.log','supplemental-trace.json')):
                raise ValueError('unexpected capsule member')
            body = archive.extractfile(entry).read()
            path = output / entry.name
            if path.is_symlink() or not path.is_file() or path.read_bytes() != body or len(body) != entry.size:
                raise ValueError('capsule/live raw bytes disagree')
            actual[entry.name] = dict(path=entry.name, bytes=len(body), sha256=sha(body))
    expected_paths = set()
    child = output / 'legacy-child'
    if child.exists():
        if child.is_symlink() or not child.is_dir():
            raise ValueError('unsafe raw tree')
        for path in child.rglob('*'):
            if path.is_symlink() or not (path.is_dir() or path.is_file()):
                raise ValueError('unsafe raw member')
            if path.is_file():
                expected_paths.add(path.relative_to(output).as_posix())
    expected_paths.update(('driver.stdout.log','driver.stderr.log'))
    if (output/'supplemental-trace.json').exists():
        expected_paths.add('supplemental-trace.json')
    if set(actual) != expected_paths or manifest.get('members') != [actual[k] for k in sorted(actual)]:
        raise ValueError('capsule membership or inventory mismatch')
    raw = output / 'raw-result.json'
    if raw.is_file():
        child_inventory = json.loads(raw.read_text()).get('driver_artifacts')
        if isinstance(child_inventory, dict):
            expected_child = {name.removeprefix('legacy-child/'): row['sha256'] for name,row in actual.items() if name.startswith('legacy-child/')}
            if child_inventory != expected_child:
                raise ValueError('V9 child inventory/capsule mismatch')
    return dict(accepted=True, members=len(actual), capsule_sha256=sha(data))
