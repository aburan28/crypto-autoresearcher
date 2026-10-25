"""Cheapest falsification of KN-FIND-bdcd60 (3) [Frobenius rule] and the support of (1):
EXHAUSTIVE over EVERY nonsingular curve y^2 = x^3 + ax + b at tiny primes, every
tuple of F_p^{m-1}, m = 3, 4 (and m = 5 at p = 5, 7; sampled at p = 11, 13).
The record measured only hand-picked curves at p >= 53.  Also runs the SAME
measurement on nearby objects outside the finding's scope: singular cubics (nodal
and cuspidal) and characteristic 3, to see whether the instrument distinguishes
an elliptic curve from a degenerate cubic at all.

Violation = an admissible fibre (every f(x_i) != 0, F of full degree 2^{m-2} and
squarefree) whose factor pattern is not {1^{2^{m-2}}, 2^{2^{m-3}}} or whose
pattern disagrees with the chi-rule (identity iff all chi(f(x_i)) equal).
"""
import json, sys, time, itertools, random
from sage.all import GF, PolynomialRing
from rt_semaev import S3_coeffs, res22, fibre_poly, cycle_type, chi

OUT = sys.argv[1] if len(sys.argv) > 1 else 'rt_sweep_small_p_out.json'
t_start = time.time()
report = {'violations': [], 'tables': []}


def allowed(m):
    return {tuple([1] * 2 ** (m - 2)), tuple([2] * 2 ** (m - 3))}


def run_curve(p, a, b, m, tuples, label):
    """Return a tally dict for one curve."""
    Fp = GF(p)
    a, b = Fp(a), Fp(b)
    f = lambda x: x ** 3 + a * x + b
    fx = {x: f(x) for x in Fp}
    tally = dict(tuples=0, some_f_zero=0, degree_drop=0, not_squarefree=0, admissible=0,
                 rule_agree=0, rule_disagree=0, outside_support=0, identity=0)
    RT = PolynomialRing(Fp, 'T')
    T = RT.gen()
    full = 2 ** (m - 2)
    for xs in tuples:
        tally['tuples'] += 1
        if any(fx[x] == 0 for x in xs):
            tally['some_f_zero'] += 1
            continue
        if m == 3:
            c = S3_coeffs(xs[0], xs[1], a, b)
            FT = c[0] + c[1] * T + c[2] * T ** 2
        elif m == 4:
            A = S3_coeffs(xs[0], xs[1], a, b)
            B = S3_coeffs(xs[2], T, a, b)  # S_3(x3, T, X) coefficients in X, as polys in T
            FT = res22([RT(c) for c in A], B)
        else:
            FT = fibre_poly(m, xs, a, b, Fp)
        if FT.degree() < full:
            tally['degree_drop'] += 1
            continue
        ct = cycle_type(FT)
        if ct is None:
            tally['not_squarefree'] += 1
            continue
        tally['admissible'] += 1
        chis = {chi(fx[x]) for x in xs}
        pred = tuple([1] * full) if len(chis) == 1 else tuple([2] * (full // 2))
        if ct not in allowed(m):
            tally['outside_support'] += 1
            report['violations'].append(dict(label=label, p=p, a=int(a), b=int(b), m=m, xs=[int(x) for x in xs], pattern=list(ct), kind='outside_support'))
        if ct == pred:
            tally['rule_agree'] += 1
        else:
            tally['rule_disagree'] += 1
            report['violations'].append(dict(label=label, p=p, a=int(a), b=int(b), m=m, xs=[int(x) for x in xs], pattern=list(ct), predicted=list(pred), kind='rule_mismatch'))
        if ct == tuple([1] * full):
            tally['identity'] += 1
    return tally


def sweep(p, m, curves, label, exhaustive=True, n_sample=0, seed=0):
    Fp = GF(p)
    agg = None
    rng = random.Random(seed)
    for (a, b) in curves:
        if exhaustive:
            tuples = itertools.product(list(Fp), repeat=m - 1)
        else:
            tuples = ([Fp(rng.randrange(p)) for _ in range(m - 1)] for _ in range(n_sample))
        t = run_curve(p, a, b, m, tuples, label)
        if agg is None:
            agg = dict(t)
        else:
            for k, v in t.items():
                agg[k] += v
    row = dict(label=label, p=p, m=m, n_curves=len(curves), exhaustive=exhaustive, **agg,
               seconds=round(time.time() - t_start, 1))
    report['tables'].append(row)
    print(json.dumps(row))
    sys.stdout.flush()
    return row


def nonsingular_curves(p):
    Fp = GF(p)
    return [(int(a), int(b)) for a in Fp for b in Fp if 4 * a ** 3 + 27 * b ** 2 != 0]


def singular_curves(p):
    Fp = GF(p)
    return [(int(a), int(b)) for a in Fp for b in Fp if 4 * a ** 3 + 27 * b ** 2 == 0]


# --- m = 3: every nonsingular curve, exhaustive, p <= 31 -------------------------------
for p in [5, 7, 11, 13, 17, 19, 23, 29, 31]:
    sweep(p, 3, nonsingular_curves(p), 'nonsingular_all_curves')

# --- m = 4: every nonsingular curve, exhaustive, p <= 13 -------------------------------
for p in [5, 7, 11, 13]:
    sweep(p, 4, nonsingular_curves(p), 'nonsingular_all_curves')

# --- m = 5: every nonsingular curve, exhaustive at p = 5, 7; sampled at 11, 13 ---------
for p in [5, 7]:
    sweep(p, 5, nonsingular_curves(p), 'nonsingular_all_curves')
for p in [11, 13]:
    sweep(p, 5, nonsingular_curves(p), 'nonsingular_all_curves_sampled', exhaustive=False, n_sample=120, seed=p)

# --- nearby objects: singular cubics (nodal and cuspidal), SAME measurement ------------
for p in [7, 11, 13]:
    sweep(p, 3, singular_curves(p), 'SINGULAR_cubics_all')
    sweep(p, 4, singular_curves(p), 'SINGULAR_cubics_all')
sweep(101, 4, [(0, 0), (101 - 3, 2)], 'SINGULAR_cuspidal_and_nodal_p101_sampled', exhaustive=False, n_sample=4000, seed=101)

# --- characteristic 3 (outside the finding's p > 3 scope) ------------------------------
for m in [3, 4, 5]:
    sweep(3, m, [(a, b) for a in [1, 2] for b in [0, 1, 2]], 'CHAR3_nonsingular_all_curves')

report['seconds'] = round(time.time() - t_start, 1)
report['n_violations'] = len(report['violations'])
json.dump(report, open(OUT, 'w'), indent=1)
print('violations:', len(report['violations']), 'seconds:', report['seconds'], 'wrote', OUT)
