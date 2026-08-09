"""F-1c: the admissible-shape test at m = 6, the last untested structural case.

    python3 experiments/EXP-FALSIFY-d770c1/falsify/run_m6.py

KN-FIND-a8990a Theorem A asserts monodromy (Z/2)^(m-2) for every m >= 3. Its own
run and RUN-FALSIFY-d770c1-001/-006 reach m = 5. At m = 6 the cover has degree
2^4 = 16 and admissible shapes are exactly [1]*16 and [2]*8; a single factor of
degree 3 or more, or any unequal-degree split, refutes it.

    S_6 = Res_X( S_5(x1,x2,x3,x4,X), S_3(x5,x6,X) )

built by two more resultant levels than F-1 needed. EVERY level asserts its full
nominal degree and returns None otherwise. That discipline is not optional here:
RUN-FALSIFY-d770c1-001 recorded a first, uncontrolled probe whose silent degree
drop at ONE level manufactured a 28% violation rate against a correct theorem.
With three nested levels there are three places for the same fault to hide.

Null object and positive control are both re-run here rather than inherited,
because the S_6 construction is new code.
"""

import json
import os
import random
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from falsify import ec, fp, probes                                  # noqa: E402
from falsify.run_mono5_compat import sylvester, interp              # noqa: E402

SEED = 20260808
ADM6 = {tuple([1] * 16), tuple([2] * 8)}


def nodes(k, avoid, p):
    """k distinct interpolation nodes avoiding `avoid`.

    A degree drop happens exactly when a node collides with one of the fixed
    parameters -- S3_in's leading coefficient is (u-v)^2. Choosing nodes clear
    of them keeps every level at full nominal degree, which RAISES yield without
    weakening the test: the strict degree assertions all remain in force.
    """
    out = [v for v in range(p) if v not in set(avoid)][:k]
    return out if len(out) == k else None


def S5_in_X(x1, x2, x3, x4, a, b, p, xs=None):
    """S5(x1,x2,x3,x4,X) as a poly in X, degree 8, or None on any degree drop."""
    xs = xs if xs is not None else list(range(9))
    ys = []
    f = ec.S4_in(x1, x2, x3, a, b, p)              # independent of X
    if f is None or fp.deg(f) != 4:
        return None
    for X in xs:
        g = ec.S3_in(x4, X, a, b, p)
        if fp.deg(g) != 2:
            return None
        ys.append(sylvester(f, g, p))
    poly = interp(xs, ys, p)
    return poly if fp.deg(poly) == 8 else None


def S6(x1, x2, x3, x4, x5, x6, a, b, p):
    inner = nodes(9, [x1, x2, x3, x4, x5, x6], p)
    if inner is None:
        return None
    f = S5_in_X(x1, x2, x3, x4, a, b, p, inner)
    if f is None:
        return None
    g = ec.S3_in(x5, x6, a, b, p)
    if fp.deg(g) != 2:
        return None
    return sylvester(f, g, p)


def S6_fibre(others, a, b, p):
    """x1 |-> S6(x1, others...) as a degree-16 poly, or None."""
    xs = nodes(17, others, p)
    if xs is None:
        return None
    ys = []
    for X in xs:
        v = S6(X, *others, a, b, p)
        if v is None:
            return None
        ys.append(v)
    poly = interp(xs, ys, p)
    return poly if fp.deg(poly) == 16 else None


def main():
    rng = random.Random(SEED)
    primes = [29, 31, 37, 41, 43, 47, 53]   # need >=17 nodes clear of 5 params

    print('F-1c  admissible-shape test at m=6 (cover degree 16)')
    print('      admissible: [1]*16 and [2]*8 only\n')

    # ---- positive control: S_6 must vanish on genuine 6-term relations -------
    ok = fail = 0
    for p in primes:
        for _ in range(8):
            a, b = rng.randrange(p), rng.randrange(p)
            if not ec.nonsingular(a, b, p):
                continue
            pts = ec.affine_points(a, b, p)
            if len(pts) < 7:
                continue
            chosen = [rng.choice(pts) for _ in range(5)]
            S = None
            for q in chosen:
                S = ec.add_points(S, q, a, p)
            if S is None:
                continue
            last = ec.negate(S, p)
            xs = [q[0] for q in chosen] + [last[0]]
            v = S6(*xs, a, b, p)
            if v is None:
                continue
            ok, fail = (ok + 1, fail) if v == 0 else (ok, fail + 1)
    print(f"  positive control  S_6 vanishes on real relations: {ok} ok / {fail} FAIL")

    # ---- null object: exponent-2 Galois group, degree 16 --------------------
    nviol = ntest = 0
    for p in primes:
        for _ in range(30):
            ds = [rng.randrange(1, p) for _ in range(4)]
            f = probes.null_c2_power(ds, p)
            if fp.deg(f) != 16 or not fp.is_squarefree(f, p):
                continue
            ntest += 1
            if tuple(fp.factor_pattern(f, p)) not in ADM6:
                nviol += 1
    print(f"  null object       exponent-2 group, degree 16: "
          f"{nviol}/{ntest} false violations")

    if fail or nviol or not ok or not ntest:
        print('\n  CONTROLS FAILED -- measurement is NOT reportable')
        return

    # ---- measurement --------------------------------------------------------
    shapes, used, skipped, wit = Counter(), 0, 0, None
    for p in primes:
        for _ in range(14):
            a, b = rng.randrange(p), rng.randrange(p)
            if not ec.nonsingular(a, b, p):
                continue
            others = [rng.randrange(p) for _ in range(5)]
            f = S6_fibre(others, a, b, p)
            if f is None or not fp.is_squarefree(f, p):
                skipped += 1
                continue
            s = tuple(fp.factor_pattern(f, p))
            shapes[s] += 1
            used += 1
            if s not in ADM6 and wit is None:
                wit = {'p': p, 'a': a, 'b': b, 'others': others, 'shape': list(s)}
    viol = sum(c for s, c in shapes.items() if s not in ADM6)
    print(f"\n  usable specialisations: {used}  (skipped degenerate: {skipped})")
    for s, c in shapes.most_common(6):
        print(f"    {str(list(s)):<42} {c:>4}  "
              f"{'ok' if s in ADM6 else '<== VIOLATION'}")
    print(f"\n  VIOLATIONS: {viol}/{used}")
    if wit:
        print(f"  witness: {wit}")

    out = {'experiment_id': 'EXP-FALSIFY-d770c1',
           'run_id': 'RUN-FALSIFY-d770c1-007', 'probe': 'monodromy_m6_f1c',
           'seed': SEED, 'primes': primes, 'm': 6,
           'controls': {'positive_vanish': ok, 'positive_fail': fail,
                        'null_false_violations': nviol, 'null_tested': ntest,
                        'all_passed': bool(fail == 0 and nviol == 0 and ok and ntest)},
           'usable': used, 'skipped': skipped, 'violations': viol,
           'shapes': {str(list(k)): v for k, v in shapes.items()},
           'witness': wit,
           'timestamp_utc': datetime.now(timezone.utc).isoformat(),
           'git_commit': subprocess.run(['git', 'rev-parse', 'HEAD'],
                                        capture_output=True, text=True).stdout.strip()}
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'runs', 'RUN-FALSIFY-d770c1-007', 'raw-result.json')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    json.dump(out, open(dest, 'w'), indent=2, sort_keys=True)
    print(f'\nresults written to {dest}')


if __name__ == '__main__':
    main()
