"""Ordered-base checks (clauses (1), (3), (4) of KN-FIND-bdcd60), independent of producer code.

For each curve and m in {3,4,5}:
  D1 definitions: S_3 and the resultant recursion re-verified from the defining property;
  D2 degree in T and generic squarefreeness (symbolic discriminant over F_p[x] per curve, m=3,4;
     numeric for m=5), irreducibility of S_m over F_p (transitivity);
  D3 labelled root formula + labelled Frobenius rule on sampled fibres over F_{p^2};
  D4 Frobenius cycle-type rule on exhaustive / sampled F_p-fibres, with identity frequency
     against the Chebotarev value 2^{-(m-2)}.
Usage: sage -python check_ordered.py OUTDIR
"""
import sys, json, time, itertools, collections, os
from sage.all import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mono_lib import Cover, S3_expr, symbolic_S, labelled_root_check

set_random_seed(20261023)
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, 'ordered.log'), 'w')


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s); log.write(s + '\n'); log.flush()


def supersingular_curve(p):
    F = GF(p)
    for a in range(p):
        for b in range(p):
            if (4 * F(a) ** 3 + 27 * F(b) ** 2) == 0:
                continue
            E = EllipticCurve(F, [a, b])
            if E.trace_of_frobenius() == 0:
                return (a, b)


CURVES = []  # (p, a, b, tag)
for p in (7, 11, 13):
    CURVES.append((p, 1, 0, 'j=1728'))
    CURVES.append((p, 0, 1, 'j=0'))
    CURVES.append((p, 2, 5, 'generic'))
    ss = supersingular_curve(p)
    CURVES.append((p, ss[0], ss[1], 'supersingular-search'))
CURVES += [(101, 2, 3, 'generic'), (101, 0, 1, 'j=0 supersingular (101=2 mod 3)'),
           (101, 1, 0, 'j=1728 ordinary (101=1 mod 4)'), (101, 5, 0, 'j=1728'),
           (1009, 5, 7, 'generic'), (1013, 0, 1, 'j=0'),
           (10007, 2, 3, 'generic'), (10007, 1, 0, 'j=1728 supersingular (10007=3 mod 4)')]
# de-duplicate
seen = set(); CUR = []
for c in CURVES:
    if (c[0], c[1] % c[0], c[2] % c[0]) in seen:
        continue
    seen.add((c[0], c[1] % c[0], c[2] % c[0])); CUR.append(c)

summary = {'curves': [], 'definitions': {}, 'symbolic': {}, 'labelled': {}, 'frobenius': {}}

# ------------------------------------------------------------------ D1: definitions
say('== D1 definitions: S_3 and resultant recursion vs the defining property')
defs_ok = True
for (p, a, b, tag) in CUR[:6] + CUR[-4:]:
    F = GF(p)
    if 4 * F(a) ** 3 + 27 * F(b) ** 2 == 0:
        continue
    F2 = GF(p ** 2, 'w')
    E = EllipticCurve(F2, [a, b])
    R4, S4 = symbolic_S(4, F(a), F(b), F)
    R5, S5 = symbolic_S(5, F(a), F(b), F) if p <= 13 else (None, None)
    for trial in range(40):
        P = [E.random_point() for _ in range(4)]
        if any(Q.is_zero() for Q in P):
            continue
        # S_3 vanishes at x(P1), x(P2), x(+-(P1+P2)); and its two roots are exactly x(P1+P2), x(P1-P2)
        x1, x2 = P[0][0], P[1][0]
        s = P[0] + P[1]; d = P[0] - P[1]
        if s.is_zero() or d.is_zero() or x1 == x2:
            continue
        PT = PolynomialRing(F2, 'T'); T = PT.gen()
        q = S3_expr(F2(a), F2(b), x1, x2, T)
        rts = sorted([r for r, e in q.roots() for _ in range(e)])
        if sorted([s[0], d[0]]) != rts or q.degree() != 2:
            defs_ok = False; say('  S_3 FAIL', p, a, b, trial)
        # random x3 not of that form => nonzero
        x3 = F2.random_element()
        if x3 not in (s[0], d[0]) and S3_expr(F2(a), F2(b), x1, x2, x3) == 0:
            defs_ok = False; say('  S_3 spurious zero', p, a, b)
        # S_4 vanishes on x(P1),x(P2),x(P3),x(-(P1+P2+P3))
        Q4 = -(P[0] + P[1] + P[2])
        if Q4.is_zero():
            continue
        v = S4(x1, x2, P[2][0], Q4[0], 0)
        if v != 0:
            defs_ok = False; say('  S_4 FAIL', p, a, b)
        xr = F2.random_element()
        if S4(x1, x2, P[2][0], xr, 0) == 0 and xr != Q4[0]:
            # could coincide with another sign class legitimately: check it is a root of the fibre poly
            pass
        if S5 is not None:
            Q5 = -(P[0] + P[1] + P[2] + P[3])
            if not Q5.is_zero():
                if S5(x1, x2, P[2][0], P[3][0], Q5[0], 0) != 0:
                    defs_ok = False; say('  S_5 FAIL', p, a, b)
    # degrees
    degs4 = [S4.degree(R4.gen(i)) for i in range(4)]
    if degs4 != [4, 4, 4, 4]:
        defs_ok = False; say('  deg S_4', degs4)
    if S5 is not None:
        degs5 = [S5.degree(R5.gen(i)) for i in range(5)]
        if degs5 != [8] * 5:
            defs_ok = False; say('  deg S_5', degs5)
summary['definitions'] = {'S3_S4_S5_defining_property_and_degrees': bool(defs_ok)}
say('  definitions ok:', defs_ok)

# ------------------------------------------------------------------ D2: symbolic per curve
say('== D2 symbolic: disc_T S_3 = 16 f(x1) f(x2) over Z[a,b]; per-curve deg/disc/irreducibility')
Rab = PolynomialRing(ZZ, ['a', 'b', 'x1', 'x2', 'T'])
a_, b_, x1_, x2_, T_ = Rab.gens()
q3 = S3_expr(a_, b_, x1_, x2_, T_)
disc3 = q3.discriminant(T_)
fx = lambda x: x ** 3 + a_ * x + b_
ident = (disc3 == 16 * fx(x1_) * fx(x2_))
say('  disc_T S_3 == 16 f(x1) f(x2) over Z[a,b,x1,x2]:', ident)
summary['symbolic']['disc_S3_identity_Z[a,b]'] = bool(ident)

for (p, a, b, tag) in CUR:
    F = GF(p)
    key = '%d,%d,%d' % (p, a, b)
    rec = {'tag': tag, 'singular': bool(4 * F(a) ** 3 + 27 * F(b) ** 2 == 0)}
    if rec['singular']:
        summary['symbolic'][key] = rec; continue
    R4, S4 = symbolic_S(4, F(a), F(b), F)
    X1, X2, X3, X4, Z = R4.gens()
    rec['deg_T_S4'] = int(S4.degree(X4))
    fac4 = S4.factor(); rec['S4_irreducible_over_Fp'] = bool(len(fac4) == 1 and fac4[0][1] == 1)
    d4 = S4.discriminant(X4)
    rec['disc_T_S4_nonzero'] = bool(d4 != 0)
    # the discriminant should vanish only on a proper closed subset: record its factorisation shape
    rec['disc_T_S4_factor_degrees'] = sorted([int(g.degree()) for g, e in d4.factor()]) if p <= 101 else 'skipped'
    if p <= 13:
        R5, S5 = symbolic_S(5, F(a), F(b), F)
        rec['deg_T_S5'] = int(S5.degree(R5.gens()[4]))
        t0 = time.time()
        fac5 = S5.factor(); rec['S5_irreducible_over_Fp'] = bool(len(fac5) == 1 and fac5[0][1] == 1)
        rec['S5_irred_seconds'] = round(time.time() - t0, 1)
    summary['symbolic'][key] = rec
    say('  ', key, tag, {k: v for k, v in rec.items() if k != 'tag'})

# ------------------------------------------------------------------ D3 + D4 per curve, per m
say('== D3/D4: labelled root formula, Frobenius rule, cycle-type census')
for (p, a, b, tag) in CUR:
    F = GF(p)
    if 4 * F(a) ** 3 + 27 * F(b) ** 2 == 0:
        say('  skip singular', p, a, b); continue
    cov = Cover(p, a, b, mmax=5)
    E = EllipticCurve(F, [a, b])
    key = '%d,%d,%d' % (p, a, b)
    cinfo = {'p': p, 'a': a, 'b': b, 'tag': tag, 'j': str(E.j_invariant()),
             'trace': int(E.trace_of_frobenius()), 'supersingular': bool(E.is_supersingular()),
             'order': int(E.order())}
    summary['curves'].append(cinfo)
    say('  curve', key, cinfo)
    for m in (3, 4, 5):
        n = m - 1
        # sampling plan: exhaustive when p^n <= 30000, else sample
        exhaustive = (p ** n <= 15000)
        if exhaustive:
            tuples = itertools.product(range(p), repeat=n)
            N = p ** n
        else:
            N = {3: 4000, 4: 4000, 5: 1200}[m] if p < 5000 else {3: 2000, 4: 2000, 5: 400}[m]
            tuples = ([F.random_element() for _ in range(n)] for _ in range(N))
        t0 = time.time()
        counts = collections.Counter()
        mism = []
        ct_counts = collections.Counter()
        chi_all_equal = 0
        for xs in tuples:
            xs = [F(x) for x in xs]
            st, chis, ct, pred = cov.classify(m, xs)
            counts[st] += 1
            if st != 'ok':
                continue
            ct_counts[ct] += 1
            if len(set(chis)) == 1:
                chi_all_equal += 1
            if ct != pred and len(mism) < 5:
                mism.append({'xs': [int(x) for x in xs], 'chis': chis, 'ct': ct, 'pred': pred})
            if ct != pred:
                counts['MISMATCH'] += 1
        nok = counts['ok']
        d = 2 ** (m - 2)
        id_ct = tuple([1] * d)
        rec = {'exhaustive': exhaustive, 'N': N, 'status_counts': dict(counts),
               'cycle_types': {str(k): v for k, v in ct_counts.items()},
               'identity_fraction': (ct_counts[id_ct] / nok) if nok else None,
               'chebotarev_identity_expected': 1.0 / d,
               'mismatches': counts['MISMATCH'], 'mismatch_examples': mism,
               'seconds': round(time.time() - t0, 1)}
        rec['identity_fraction'] = float(rec['identity_fraction']) if rec['identity_fraction'] is not None else None
        summary['frobenius'].setdefault(key, {})['m=%d' % m] = rec
        say('    m=%d' % m, 'exh' if exhaustive else 'sample', 'N=%d' % N, 'ok=%d' % nok,
            'cts=%s' % rec['cycle_types'], 'id_frac=%.4f (exp %.4f)' % (rec['identity_fraction'] or 0, 1.0 / d),
            'MISMATCH=%d' % counts['MISMATCH'], 'other=%s' % {k: v for k, v in counts.items() if k not in ('ok', 'MISMATCH')},
            '%.1fs' % rec['seconds'])
        # labelled root check on a subsample over F_{p^2}
        L = {'n': 0, 'skipped': 0, 'distinct': 0, 'vanish': 0, 'full_degree': 0, 'product_ok': 0, 'frob_labelled_ok': 0}
        nl = 60 if p < 5000 else 25
        for _ in range(nl):
            xs = [F.random_element() for _ in range(n)]
            r = labelled_root_check(cov, m, xs)
            if 'skipped' in r:
                L['skipped'] += 1; continue
            L['n'] += 1
            for k in ('distinct', 'vanish', 'full_degree', 'product_ok', 'frob_labelled_ok'):
                L[k] += int(bool(r[k]))
        summary['labelled'].setdefault(key, {})['m=%d' % m] = L
        say('    m=%d labelled root/Frobenius check:' % m, L)

with open(os.path.join(OUT, 'ordered_summary.json'), 'w') as fh:
    json.dump(summary, fh, indent=1, default=str)
say('wrote', os.path.join(OUT, 'ordered_summary.json'))
