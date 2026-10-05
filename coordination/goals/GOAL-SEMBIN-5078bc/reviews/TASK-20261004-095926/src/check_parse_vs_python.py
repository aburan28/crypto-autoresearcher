#!/usr/bin/env python3
"""W2: independent parse check on the twelve ACTUAL files: every generator line is evaluated by Python's own expression parser
(eval, '^' -> '**', variables bound to 0/1 integers, result mod 2) at 300 random points per polynomial and compared with the B-representation of
msparse (a different parser).  Also compares the count of terms per polynomial with a token count of '+'."""
import sys, os, glob, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msparse import *
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
ok = True
rng = random.Random(77)
for f in sorted(glob.glob(root + '/experiments/**/*.ms', recursive=True)):
    names, char, parts, empty_tail, sha = read_ms(f)
    N, B, R, info = parse_ms(f, drop_field_lines=False)
    bad = 0
    for s, p in zip(parts, B):
        code = compile(s.replace('^', '**'), '<poly>', 'eval')
        for _ in range(300):
            a = rng.getrandbits(N)
            env = {n: (a >> i) & 1 for i, n in enumerate(names)}
            v = eval(code, {'__builtins__': {}}, env) % 2
            if v != eval_B(p, a): bad += 1
    nterms_tokens = sum(s.count('+') + 1 for s in parts)
    nterms_raw = sum(len(r) for r in R)
    print(os.path.basename(f)[:42], 'polys', len(parts), 'eval mismatches vs python-eval', bad, '| raw term count equals token count:', nterms_tokens == nterms_raw, '| empty tail', empty_tail)
    ok &= (bad == 0) and nterms_tokens == nterms_raw
sys.exit(0 if ok else 1)
