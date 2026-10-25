#!/usr/bin/env python3
import hashlib
import json
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent


def prime(n):
    return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))


def main():
    out = HERE / 'fixtures'
    out.mkdir(exist_ok=False)
    raw = (HERE / 'attempts/checker-controls-v1/source-certif2.cert').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == 'c7db907b27b5bf5ec05d3780171a38b80c156848d672951b5cb606c340062d30'
    first, first_new = b'3167\n-1\n3\n1583\n2\n0\n', b'3167\n-1\n3\n2\n0\n'
    second, second_new = b'1583\n-1\n3\n113\n7\n2\n0\n', b'1583\n-1\n3\n7\n2\n0\n'
    assert raw.count(first) == raw.count(second) == 1
    variant = raw.replace(first, first_new, 1).replace(second, second_new, 1)
    (out / 'certif2_variant_current_reader.cformat').write_bytes(variant)
    rows = []
    for n, p, listed in [(3167, 1583, [1583, 2]), (1583, 113, [113, 7, 2])]:
        residue = n - 1
        for factor in listed:
            while residue % factor == 0:
                residue //= factor
        assert residue == 1
        original_b = pow(5, (n - 1) // 2, n)
        assert original_b == n - 1
        assert prime(n) and prime(p) and (2 * p + 1) ** 2 > n
        m = (n - 1) // p
        assert m * p == n - 1 and m % 2 == 0
        b = pow(5, m // 2, n)
        assert b != n - 1 and pow(b, p, n) == n - 1
        rows.append({'N': n, 'prime_factor': p, 'listed_factors_in_original': listed, 'cofactor_recovered_from_original': residue, 'original_wrong_cofactor_b': original_b, 'variant_m': m, 'variant_b': b, 'variant_b_to_p': pow(b, p, n), 'theorem3_conditions': True})
    receipt = {'scope': 'independent integer diagnosis of a bundled fixture/current-reader mismatch; no historical or curve-selection inference', 'original_sha256': hashlib.sha256(raw).hexdigest(), 'variant_sha256': hashlib.sha256(variant).hexdigest(), 'rows': rows, 'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out / 'diagnostic.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
