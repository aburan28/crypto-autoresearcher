#!/usr/bin/env python3
"""Independent Sage recomputation from archived p,n and all small odd primes."""
import hashlib
import json
import sys
from pathlib import Path

from sage.all import Integer, kronecker, prime_range, version

ROOT = Path(__file__).resolve().parents[3]
OMITTED = ROOT / 'research/nist_seed_skipped_curves_20261016/assessed.json'
PUBLISHED = ROOT / 'research/nist_seed_skipped_curves_20261016/traits.json'
NAMES = ('prime192v1', 'prime192v2', 'prime192v3', 'prime239v1', 'prime239v2',
         'prime239v3', 'secp224r1', 'prime256v1')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert len(sys.argv) == 3
    raw_path, output_path = map(Path, sys.argv[1:])
    assert not output_path.exists(), 'write-once verification'
    raw = json.loads(raw_path.read_text())
    assert raw['sources'][str(OMITTED.relative_to(ROOT))] == sha(OMITTED)
    assert raw['sources'][str(PUBLISHED.relative_to(ROOT))] == sha(PUBLISHED)
    source_o = json.loads(OMITTED.read_text())['candidate_rows']
    source_p = json.loads(PUBLISHED.read_text())['published_controls']
    original = {r['identity']['curve_uid']: r for r in source_o + [source_p[n] for n in NAMES]}
    assert len(original) == 19 and len(raw['rows']) == 19
    primes = [int(p) for p in prime_range(3, 998)]
    assert len(primes) == 167 and primes == raw['odd_primes']
    for row in raw['rows']:
        r = original[row['curve_uid']]
        p = Integer(int(r['p_hex'], 16))
        n = Integer(int(r['n_hex'], 16))
        t = p + 1 - n
        delta = t * t - 4 * p
        assert delta < 0 and t*t <= 4*p
        assert int(delta) == int(row['delta_hex_signed'], 16)
        assert int(t) == int(row['trace_hex_signed'], 16)
        signs = ''.join('+' if kronecker(delta, ell) == 1 else
                        '-' if kronecker(delta, ell) == -1 else '0' for ell in primes)
        assert signs == row['signature'], row['name']
        m = Integer(1)
        first = None
        for ell, s in zip(primes, signs):
            if s == '+':
                m *= ell
            if first is None and m*m > 16*p:
                first = ell
        assert first == row['cutoff_ell']
        assert sum(s=='+' for ell,s in zip(primes,signs) if ell<=101) == row['elkies_through_101']
        assert sum(s=='+' for ell,s in zip(primes,signs) if ell<=251) == row['elkies_through_251']
    result = {'source_raw_sha256': sha(raw_path), 'sage_version': version(),
              'verified_curves': len(raw['rows']), 'verified_symbols': len(primes)*len(raw['rows']),
              'status': 'pass'}
    output_path.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
