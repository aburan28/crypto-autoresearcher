"""Boundary controls for producer-only dimension stopping; no LFD inference."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--fixtures', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    rows = []
    for fixture, degree in [(0, 3), (1, 3), (2, 4)]:
        seed = a.fixtures / str(fixture) / f'degree{degree}.bin'
        reference = a.fixtures / str(fixture) / f'degree{degree+1}.bin'
        q = struct.unpack_from('<4q', reference.read_bytes())[3]
        for label, target in [('disabled', None), ('below', q-1), ('equal', q), ('above', q+1)]:
            name = f'{fixture}-{degree}-{label}'
            output = a.out / (name+'.bin')
            argv = [str(a.binary), str(seed), str(output), '20', str(2**30)]
            if target is not None:
                argv.append(str(target))
            run = subprocess.run(argv, text=True, capture_output=True, timeout=120)
            (a.out/(name+'.stdout.txt')).write_text(run.stdout)
            (a.out/(name+'.stderr.txt')).write_text(run.stderr)
            run.check_returncode()
            observed = json.loads(run.stdout)
            if target is None or target < q:
                assert observed['status'] == 'candidate_certificate'
                assert output.read_bytes() == reference.read_bytes()
            else:
                assert observed['status'] == 'target_codimension_unreachable'
                assert not output.exists()
                assert q <= observed['constructed_dimension_ceiling'] <= target
                assert observed['constructed_dimension_ceiling'] == observed['working_coordinates']-observed['relation_rank']
                assert 'codimension' not in observed and 'last_fall_degree_lower_bound' not in observed
            rows.append(dict(argv=argv,observation=observed,reference_codimension=q,passed=True))
    for bad in ['-1', '1x', '', '999999999999999999999999999']:
        output = a.out/'invalid.bin'
        argv = [str(a.binary),str(seed),str(output),'20',str(2**30),bad]
        run = subprocess.run(argv,text=True,capture_output=True,timeout=30)
        assert run.returncode == 2 and not output.exists() and not run.stdout
        rows.append(dict(argv=argv,returncode=run.returncode,stderr=run.stderr,passed=True))
    record = dict(scope='Software controls only: no frontier result, LFD bound, or performance claim',
                  cases=rows,binary_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(Path(__file__).with_name('quotient_lift_target.cpp').read_bytes()).hexdigest(),
                  fixture_sha256={str(f.relative_to(a.fixtures)):hashlib.sha256(f.read_bytes()).hexdigest()
                                  for f in a.fixtures.glob('*/degree*.bin')})
    (a.out/'summary.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(boundary_cases=12,invalid_argument_cases=4,passed=True)))


if __name__ == '__main__':
    main()
