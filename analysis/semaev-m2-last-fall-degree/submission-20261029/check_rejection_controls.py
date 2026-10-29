#!/usr/bin/env python3
"""Software validation: the independent checker must reject damaged copies.

The retained original is read only. These are negative acceptance controls,
not new algebraic instances or evidence for a fall-degree claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

from certificate_campaign import digest, save


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--certificate', type=Path, required=True)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--checker', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    receipt = json.loads(args.receipt.read_text())
    result = receipt['result']
    original = args.certificate.read_bytes()
    expected = result['certificate_sha256']
    assert hashlib.sha256(original).hexdigest() == expected
    nvars, degree, columns, nq = struct.unpack_from('<4q', original)
    wrong_dimension = bytearray(original)
    struct.pack_into('<q', wrong_dimension, 0, nvars + 1)
    duplicate_monomial = bytearray(original)
    duplicate_monomial[40:48] = duplicate_monomial[32:40]
    changed_map = bytearray(original)
    changed_map[32 + 8 * columns] ^= 1
    cases = [('truncated_header', original[:31]),
             ('wrong_variable_count', wrong_dimension),
             ('duplicate_monomial', duplicate_monomial),
             ('changed_constant_image', changed_map)]
    record = result['parameters']['record']
    rows = []
    with tempfile.TemporaryDirectory(prefix='semaev-negative-controls-') as temporary:
        for label, damaged in cases:
            path = Path(temporary) / (label + '.bin')
            path.write_bytes(damaged)
            argv = [sys.executable, str(args.checker)]
            if result['parameters'].get('chain'):
                argv.append('--t3')
            argv += [str(path), str(record['n']), record['modulus_hex'], str(record['a2']),
                     record['a6_hex'], record['z_hex'], *record['V_basis_hex']]
            run = subprocess.run(argv, capture_output=True, text=True, timeout=120)
            rejected = run.returncode != 0 and 'VALID:' not in run.stdout
            rows.append(dict(case=label, sha256=hashlib.sha256(damaged).hexdigest(),
                             returncode=run.returncode, rejected=rejected,
                             stdout=run.stdout, stderr=run.stderr))
    assert digest(args.certificate) == expected
    save(args.out, dict(schema='semaev.checker-negative-controls/v1',
         kind='software_validation', original_sha256=expected,
         checker_sha256=digest(args.checker), cases=rows,
         all_rejected=all(row['rejected'] for row in rows)))
    print(json.dumps({'cases': len(rows), 'all_rejected': all(row['rejected'] for row in rows)}))
    return int(not all(row['rejected'] for row in rows))


if __name__ == '__main__':
    sys.exit(main())
