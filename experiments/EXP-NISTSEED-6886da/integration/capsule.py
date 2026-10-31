"""Deterministic custody capsule for variable driver-owned raw artifacts."""
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path, PurePosixPath

CAPSULE = 'raw-artifacts.tar.gz'
INVENTORY = 'raw-artifact-inventory.json'
DRIVER_LOGS = ('driver.stdout.log', 'driver.stderr.log')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def members(output: Path):
    result = {}
    child = output / 'legacy-child'
    if child.exists():
        if child.is_symlink() or not child.is_dir():
            raise ValueError('unsafe legacy-child root')
        for p in sorted(child.rglob('*')):
            if p.is_symlink():
                raise ValueError('symlink in raw custody tree')
            if p.is_dir():
                continue
            if not p.is_file():
                raise ValueError('non-regular raw custody member')
            result[p.relative_to(output).as_posix()] = p
    for name in DRIVER_LOGS:
        p = output / name
        if not p.is_file() or p.is_symlink():
            raise ValueError('missing or unsafe driver capture')
        result[name] = p
    trace = output / 'supplemental-trace.json'
    if trace.exists():
        if trace.is_symlink() or not trace.is_file():
            raise ValueError('unsafe supplemental trace')
        result[trace.name] = trace
    return dict(sorted(result.items()))


def create(output: Path):
    paths = members(output)
    if (output / CAPSULE).exists() or (output / INVENTORY).exists():
        raise ValueError('refusing capsule reuse')
    listing = []
    with (output / CAPSULE).open('xb') as target:
        with gzip.GzipFile(fileobj=target, mode='wb', filename='', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.USTAR_FORMAT) as archive:
                for name, path in paths.items():
                    data = path.read_bytes()
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    info.mode = 0o600
                    info.mtime = info.uid = info.gid = 0
                    info.uname = info.gname = ''
                    archive.addfile(info, io.BytesIO(data))
                    listing.append(dict(path=name, bytes=len(data), sha256=digest(data)))
    payload = (output / CAPSULE).read_bytes()
    result = dict(schema='crypto.autoresearch.ecpp_raw_capsule.v1',
                  capsule=CAPSULE, bytes=len(payload), sha256=digest(payload), members=listing,
                  excluded_reconstructible_cache='runtime-cache; frozen kernel/payload/catalog bindings remain separately required')
    (output / INVENTORY).write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result
