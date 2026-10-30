#!/usr/bin/env python3
"""Retained software controls for consecutive native D3 -> D4 -> D5 lifts."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    checker = here.parent / 'semaev-m2-last-fall-degree/verify/cert_check.py'
    spec = importlib.util.spec_from_file_location('independent_checker', checker)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    args.out.mkdir(parents=True, exist_ok=False)
    summary = []
    for index, (field_n, modulus, basis) in enumerate([
        (6, 0x43, [1, 2, 4]), (8, 0x11b, [1, 2, 4]),
        (10, 0x409, [1, 2, 4, 8])
    ]):
        root = args.out / str(index)
        root.mkdir()
        n, polys = mod.descend(field_n, modulus, 0, 3, 2, basis)
        system = f'{n} {len(polys)}\n' + ''.join(
            ' '.join([str(len(p))] + [format(m, 'x') for m in p]) + '\n' for p in polys)
        (root / 'input.sys').write_text(system)
        steps = []

        def run(label, argv, stdin=None):
            argv = [str(x) for x in argv]
            result = subprocess.run(argv, input=stdin, text=True, capture_output=True, timeout=120)
            (root / (label + '.stdout.txt')).write_text(result.stdout)
            (root / (label + '.stderr.txt')).write_text(result.stderr)
            steps.append(dict(label=label, argv=argv, returncode=result.returncode))
            (root / 'steps.json').write_text(json.dumps(steps, indent=2) + '\n')
            if result.returncode:
                raise RuntimeError(f'{label} failed: {result.stderr}')
            return result.stdout

        seed = root / 'degree3.bin'
        run('dense3', [args.runtime / 'bin/lfdclose2', 3, 0, 20, seed], system)
        for degree in (3, 4, 5):
            current = root / f'degree{degree}.bin'
            if degree > 3:
                run(f'lift{degree}', [args.runtime / 'bin/quotient_lift', seed, current, 20, 2**30])
            checked = run(f'check{degree}', [sys.executable, checker, current, field_n,
                format(modulus, 'x'), 0, 3, 2, *[format(b, 'x') for b in basis]])
            assert f'VALID: 1 is not in W_{degree}' in checked
            direct = root / f'direct{degree}.bin'
            run(f'direct{degree}', [args.runtime / 'bin/lfdclose2', degree, 0, 20, direct], system)
            header = struct.unpack_from('<4q', current.read_bytes())
            reference = struct.unpack_from('<4q', direct.read_bytes())
            assert header == reference, (header, reference)
            summary.append(dict(fixture=index, field_n=field_n, degree=degree,
                                checked_codimension=header[3], direct_codimension=reference[3]))
            seed = current
        (root / 'steps.json').write_text(json.dumps(steps, indent=2) + '\n')
    receipt = dict(scope='Software controls only; no frontier outcome or timing claim',
        fixtures=summary, sha256={str(p.relative_to(args.out)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(args.out.rglob('*')) if p.is_file()},
        instruments={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__), checker, args.runtime/'bin/lfdclose2', args.runtime/'bin/quotient_lift']})
    (args.out / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
