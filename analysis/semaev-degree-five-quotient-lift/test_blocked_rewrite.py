"""Exact software controls for block triangular substitution; no timing claim."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

from quotient_lift import write_certificate
from test_quotient_lift import oracle, independent_conditions


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    rows = []
    variants = ['batched', 'blocked_31', 'blocked_257', 'blocked_4096']
    binaries = {v: args.runtime/'bin'/('quotient_lift_'+v) for v in variants}
    cases = [(7, 3, [{3, 12, 16}]), (10, 4, [{3, 12, 16}, {5, 32}]),
             (16, 4, [{1, 2}]), (12, 4, [{3, 12, 16}, {5, 32}, {6, 64, 128}])]
    covered_internal = covered_external = False
    for index, (n, d, polys) in enumerate(cases):
        root = args.out/str(index)
        root.mkdir()
        seed, sq, _ = oracle(n, d, polys)
        source = root/'seed.bin'
        write_certificate(source, n, d, seed, sq)
        reference = None
        for variant, binary in binaries.items():
            output = root/(variant+'.bin')
            argv = [str(binary), str(source), str(output), '4096', str(2**30)]
            run = subprocess.run(argv, text=True, capture_output=True,
                                 timeout=240, check=True)
            (root/(variant+'.stdout.txt')).write_text(run.stdout)
            (root/(variant+'.stderr.txt')).write_text(run.stderr)
            observation = json.loads(run.stdout)
            assert observation['status'] == 'candidate_certificate'
            data = output.read_bytes()
            if reference is None:
                reference = data
            assert data == reference, (index, variant)
            nn, dd, cols, q = struct.unpack_from('<4q', data)
            assert (nn, dd) == (n, d+1)
            masks = struct.unpack_from('<' + str(cols) + 'Q', data, 32)
            width = 8*((q+63)//64)
            offset = 32+8*cols
            images = {m: int.from_bytes(data[offset+j*width:offset+(j+1)*width], 'little')
                      for j, m in enumerate(masks)}
            independent_conditions(n, d+1, images, q, polys)
            record = dict(case=index, variables=n, seed_degree=d, variant=variant,
                          certificate_sha256=hashlib.sha256(data).hexdigest(),
                          byte_identical=True, independent_conditions=True)
            if variant != 'batched':
                found = re.search(r'rewrite_blocks (\d+) internal_edges (\d+) external_edges (\d+)', run.stderr)
                assert found, run.stderr
                blocks, internal, external = map(int, found.groups())
                record.update(rewrite_blocks=blocks, internal_edges=internal,
                              external_edges=external)
                covered_internal |= internal > 0
                covered_external |= external > 0
                if index == 2 and variant == 'blocked_4096':
                    assert blocks > 1
                    assert cols % 4096 != 0 and q % 64 != 0
            rows.append(record)
        print('case', index, 'passed', flush=True)
    assert covered_internal and covered_external
    result = dict(scope='Software equivalence only; no frontier or speed claim',
                  cases=rows, internal_and_external_dependencies_covered=True,
                  source_sha256=hashlib.sha256(Path(__file__).with_name('quotient_lift_blocked.cpp').read_bytes()).hexdigest(),
                  binaries={k: hashlib.sha256(v.read_bytes()).hexdigest() for k,v in binaries.items()})
    (args.out/'summary.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
