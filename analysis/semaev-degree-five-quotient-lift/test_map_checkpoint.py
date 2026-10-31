"""Exact local controls for the separate provisional-map checkpoint candidate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

from quotient_lift import write_certificate
from test_quotient_lift import independent_conditions, oracle


CASES = [
    (16, 4, [{1, 2}]),
    (10, 4, [{3, 12, 16}, {5, 32}]),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_certificate(path, n, degree, polys):
    data = path.read_bytes()
    nn, dd, cols, q = struct.unpack_from('<4q', data)
    assert (nn, dd) == (n, degree + 1)
    masks = struct.unpack_from('<' + str(cols) + 'Q', data, 32)
    width = 8 * ((q + 63) // 64)
    offset = 32 + 8 * cols
    images = {m: int.from_bytes(data[offset + j * width:offset + (j + 1) * width], 'little')
              for j, m in enumerate(masks)}
    independent_conditions(n, degree + 1, images, q, polys)


def run(binary, seed, output, relation_dir, map_dir=None, restore=False, expected=0):
    relation_dir.mkdir()
    env = os.environ.copy()
    for key in ('SEMAEV_MAP_DIR', 'SEMAEV_MAP_RESTORE', 'SEMAEV_MAP_CHUNK_ROWS',
                'SEMAEV_MAP_PUBLISH', 'SEMAEV_MAP_FETCH', 'SEMAEV_CHECKPOINT_RESTORE'):
        env.pop(key, None)
    env['SEMAEV_CHECKPOINT_DIR'] = str(relation_dir)
    if map_dir:
        env['SEMAEV_MAP_DIR'] = str(map_dir)
        env['SEMAEV_MAP_CHUNK_ROWS'] = '4096'
    if restore:
        env['SEMAEV_MAP_RESTORE'] = '1'
    process = subprocess.run([str(binary), str(seed), str(output), '4096', str(1 << 30)],
                             env=env, capture_output=True, text=True, timeout=240)
    assert process.returncode == expected, (process.returncode, process.stderr[-2000:])
    return process


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    rows = []
    for index, (n, degree, polys) in enumerate(CASES):
        root = args.out / str(index)
        root.mkdir()
        seed, sq, _ = oracle(n, degree, polys)
        source = root / 'seed.bin'
        write_certificate(source, n, degree, seed, sq)
        map_dir = root / 'map'
        map_dir.mkdir()
        baseline = root / 'baseline.bin'
        fresh = root / 'fresh.bin'
        restored = root / 'restored.bin'
        base_run = run(args.reference, source, baseline, root / 'base-relations')
        fresh_run = run(args.candidate, source, fresh, root / 'fresh-relations', map_dir)
        restore_run = run(args.candidate, source, restored, root / 'restore-relations', map_dir, True)
        assert baseline.read_bytes() == fresh.read_bytes() == restored.read_bytes()
        check_certificate(restored, n, degree, polys)
        chunks = sorted(map_dir.glob('map-*.bin'))
        assert chunks and all(chunk.stat().st_size > 100 for chunk in chunks)
        assert fresh_run.stderr.count('saved map chunk') == len(chunks)
        assert restore_run.stderr.count('restored map chunk') == len(chunks)
        if index == 0:
            assert len(chunks) > 1
            partial_dir = root / 'partial-map'
            partial_dir.mkdir()
            shutil.copyfile(chunks[-1], partial_dir / chunks[-1].name)
            partial = root / 'partial-restored.bin'
            partial_run = run(args.candidate, source, partial, root / 'partial-relations', partial_dir, True)
            assert partial.read_bytes() == baseline.read_bytes()
            assert 'restored map chunk' in partial_run.stderr and 'saved map chunk' in partial_run.stderr
            bad_dir = root / 'corrupt-map'
            shutil.copytree(map_dir, bad_dir)
            bad = bad_dir / chunks[-1].name
            with bad.open('r+b') as stream:
                stream.seek(150)
                byte = stream.read(1)
                stream.seek(150)
                stream.write(bytes([byte[0] ^ 1]))
            bad_run = run(args.candidate, source, root / 'bad.bin', root / 'bad-relations', bad_dir,
                          True, expected=2)
            assert 'map chunk digest mismatch' in bad_run.stderr
        rows.append(dict(case=index, n=n, degree=degree + 1, chunks=len(chunks),
                         certificate_sha256=digest(baseline), byte_identical=True,
                         independent_conditions=True, reference_status=json.loads(base_run.stdout)['status']))
    result = dict(scope='Local software equivalence and corruption control only; no frontier admission',
                  rows=rows, candidate_sha256=digest(args.candidate), reference_sha256=digest(args.reference))
    (args.out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
