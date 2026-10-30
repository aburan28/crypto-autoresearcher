#!/usr/bin/env python3
"""Source-guided replay of EncodedDivisors.lean's concrete loop, not a polynomial bridge."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
MASKS = (131081, 313, 471, 131073, 257)

def degree(x):
    return x.bit_length() - 1 if x else 0

def rem_fuel(fuel, p, d):
    steps = 0
    while fuel:
        if d == 0 or p == 0 or degree(p) < degree(d):
            break
        p ^= d << (degree(p) - degree(d))
        steps += 1
        fuel -= 1
    unfinished = p != 0 and d != 0 and degree(p) >= degree(d)
    return p, steps, unfinished

rows = []
summary = []
for p in MASKS:
    n = degree(p)
    candidates = [2**d + lower for d in range(1, n//2 + 1) for lower in range(2**d)]
    expected = [mask for d in range(1, n//2 + 1) for mask in range(2**d, 2**(d+1))]
    assert candidates == expected
    actual_tests = 0
    first_zero = None
    for d in candidates:
        rem, steps, unfinished = rem_fuel(n+1, p, d)
        rows.append({'p':p,'d':d,'degree_d':degree(d),'remainder':rem,'steps':steps,'unfinished':unfinished})
        if first_zero is None:
            actual_tests += 1
            if rem == 0:
                first_zero = d
    these = [r for r in rows if r['p'] == p]
    assert not any(r['unfinished'] for r in these)
    summary.append({
        'mask':p, 'degree':n, 'fuel':n+1,
        'candidate_count':len(candidates), 'first_zero_divisor':first_zero,
        'predicate':first_zero is None, 'actual_tests_before_short_circuit':actual_tests,
        'max_reduction_steps':max(r['steps'] for r in these),
        'unfinished_count':sum(r['unfinished'] for r in these)
    })
assert [(r['mask'],r['predicate'],r['candidate_count']) for r in summary[:3]] == [(131081,True,510),(313,True,30),(471,True,30)]
assert [(r['mask'],r['predicate'],r['first_zero_divisor']) for r in summary[3:]] == [(131073,False,3),(257,False,3)]
(OUT/'source-guided-reduction-rows.json').write_text(json.dumps(rows,indent=2)+'\n')
(OUT/'source-guided-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'summary':summary,'rows_sha256':hashlib.sha256((OUT/'source-guided-reduction-rows.json').read_bytes()).hexdigest()},indent=2))
