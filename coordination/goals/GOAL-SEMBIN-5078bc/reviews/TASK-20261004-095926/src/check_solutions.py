#!/usr/bin/env python3
"""W2: the dumped solution sets (two role assignments) must be identical and every point must satisfy every
generator AS WRITTEN (raw-exponent evaluation, field lines included), by an evaluation path that shares nothing
with the C counters."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msparse import *
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ok = True
for f in sorted(glob.glob(root + '/../experiments/**/*.ms', recursive=True), key=lambda p: (parse_ms(p)[0], p)):
    b = os.path.basename(f)[:-3]
    N, polysB, raws, info = parse_ms(f, drop_field_lines=False)   # field lines kept: they must also vanish
    s1 = [int(x) for x in open(f'{root}/results/V/{b}.solutions_E1.txt').read().split()]
    s2 = [int(x) for x in open(f'{root}/results/V/{b}.solutions_E2.txt').read().split()]
    same = (sorted(s1) == sorted(s2))
    sat = all(eval_raw(r, a) == 0 for a in s1 for r in raws) and all(eval_B(p, a) == 0 for a in s1 for p in polysB)
    # a flip of one coordinate of a solution must violate something (sanity: evaluation is not vacuous)
    nonvac = all(any(eval_raw(r, a ^ (1 << j)) for r in raws) for a in s1 for j in range(N)) if s1 else True
    print(b[:42], 'N=%d' % N, '|V|=%d' % len(s1), 'E1==E2' if same else 'E1!=E2', 'all satisfy generators(raw+B)' if sat else 'VIOLATION', 'every single-bit flip violates' if nonvac else 'some flip still a solution')
    ok &= same and sat
sys.exit(0 if ok else 1)
