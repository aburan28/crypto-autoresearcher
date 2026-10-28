"""Read-only diagnostics for retained, already verified relation matrices.

Usage: python -m crypto_autoresearcher.index_calculus.quality_cli INPUT.json
Input keys: modulus, columns, rows, rhs; optional targets and partials (B,U,rhs).
"""
import argparse
from dataclasses import asdict
import json

from .relation_quality import AffineRelations, cancel_outside


def analyze(data):
    rows, rhs = data['rows'], data['rhs']
    if len(rows) != len(rhs):
        raise ValueError('row/rhs counts differ')
    system = AffineRelations(data['modulus'], data['columns'])
    progress = []
    for i, (row, value) in enumerate(zip(rows, rhs)):
        independent = system.add(row, value)
        progress.append(dict(row=i, independent=independent, **system.summary()))
    out = dict(schema='prime-field-relation-quality/v1', **system.summary(),
               kernel=system.kernel(), progress=progress,
               targets=[asdict(system.identify(row)) for row in data.get('targets', [])],
               scope='algebraic diagnostics; input point/witness verification is the caller responsibility')
    if 'partials' in data:
        partial = data['partials']
        out['partials'] = cancel_outside(system, partial['B'], partial['U'], partial['rhs'])
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    args = parser.parse_args(argv)
    with open(args.input) as stream:
        result = analyze(json.load(stream))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
