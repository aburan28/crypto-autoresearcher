#!/usr/bin/env python3
"""Bounded generic-fixture quotient checks and exhaustive Boolean count."""
import json
from pathlib import Path
import struct
import sys

from test_quotient_lift import independent_conditions, oracle


def main():
    data = Path(sys.argv[1]).read_bytes()
    fixture = json.loads(Path(sys.argv[2]).read_text())
    n, d, cols, q = struct.unpack_from('<4q', data)
    assert n == fixture['n'] and d == fixture['degree'] and 0 < n <= 12
    assert 0 < q <= 1 << n and 0 < cols <= 1 << n
    width = 8 * ((q + 63) // 64)
    assert len(data) == 32 + cols * 8 + cols * width
    masks = struct.unpack_from('<'+str(cols)+'Q', data, 32)
    assert len(set(masks)) == cols
    offset = 32 + 8 * cols
    rows = {m:int.from_bytes(data[offset+j*width:offset+(j+1)*width], 'little')
            for j,m in enumerate(masks)}
    polynomials = [set(p) for p in fixture['polynomials']]
    independent_conditions(n,d,rows,q,polynomials)
    assert rows[0] != 0
    _, oracle_q, _ = oracle(n,d,polynomials)
    assert q == oracle_q
    count = 0
    for assignment in range(1 << n):
        if all(sum((assignment & m) == m for m in poly) % 2 == 0 for poly in polynomials):
            count += 1
    print(json.dumps(dict(codimension=q, oracle_codimension=oracle_q, solutions=count,
                         checks=['generic kernel closure', 'input annihilation', 'surjectivity',
                                 'constant survives', 'full-space oracle dimension', 'exhaustive count'],
                         scope='Fixed generic fixture only; not a Semaev frontier result')))


if __name__ == '__main__':
    main()
