"""Proves-too-much controls for the sheriff case (reader validator-breakthrough).

A  Proper closed locus x_2 = x([2]P_1) (f(x_1) f(x_2) is a square): the generic group must
   shrink.  Symbolic: F factors over F_p(x_1) at m = 3 (trivial group) and over F_p(x_1, x_3)
   at m = 4 (intransitive Z/2).  Numeric: identity frequency 1 (m=3) and 1/2 (m=4) instead of
   1/2 and 1/4.  The cycle-type rule itself is expected to SURVIVE on this locus (chi_2 = chi_1
   automatically), so detection must come from the reducibility/frequency checks -- recorded.
B' Square-discriminant sub-cover of the symmetric base at m = 4: S_3 -> A_3, group -> A_4;
   the census must see A_4 (no 4-cycles, no transpositions) and reject S_4.
C  Singular cubics y^2 = x^3 and y^2 = (x-1)^2 (x+2): outside the claim's scope; record whether
   the degree / squarefree / Frobenius-rule conclusions survive (expected: yes, the f(x_i)
   are still independent mod squares) -- this tests only whether "nonsingular" is necessary.
D  p = 3 (outside the claim's "p > 3"): y^2 = x^3 + x + 1 over F_3 and F_27, same checks.
Usage: sage -python controls.py OUTDIR
"""
import sys, json, time, itertools, collections, os
from sage.all import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mono_lib import Cover, S3_expr, symbolic_S, labelled_root_check

set_random_seed(20261023)
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, 'controls.log'), 'w')


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s); log.write(s + '\n'); log.flush()


summary = {}


def dbl_x(a, b, x):
    return (x ** 4 - 2 * a * x ** 2 - 8 * b * x + a ** 2) / (4 * (x ** 3 + a * x + b))


# ------------------------------------------------------------------ A: locus x2 = x(2 P1)
say('== Control A: locus x_2 = x([2]P_1)')
A = {}
for (p, a, b) in [(101, 2, 3), (13, 2, 5), (1009, 5, 7)]:
    F = GF(p)
    R1 = PolynomialRing(F, 'x1'); x1 = R1.gen(); K1 = R1.fraction_field()
    PT = PolynomialRing(K1, 'T'); T = PT.gen()
    x2 = dbl_x(F(a), F(b), K1(x1))
    F3 = PT(S3_expr(F(a), F(b), K1(x1), x2, T))
    fac3 = F3.factor()
    # expected roots: x1 and x(3P1)
    rec = {'m3_factor_degrees_over_Fp(x1)': sorted(int(g.degree()) for g, e in fac3 for _ in range(e)),
           'm3_x1_is_root': bool(F3(K1(x1)) == 0)}
    # m = 4 over F_p(x1, x3)
    R2 = PolynomialRing(F, ['x1', 'x3']); X1, X3 = R2.gens(); K2 = R2.fraction_field()
    PT2 = PolynomialRing(K2, 'T'); T2 = PT2.gen()
    PTX2 = PolynomialRing(PT2, 'X'); X = PTX2.gen()
    x2g = dbl_x(F(a), F(b), K2(X1))
    Aq = PTX2(S3_expr(F(a), F(b), K2(X1), x2g, X))
    Bq = PTX2(S3_expr(F(a), F(b), K2(X3), T2, X))
    F4 = Aq.resultant(Bq)
    fac4 = F4.factor()
    rec['m4_degree'] = int(F4.degree())
    rec['m4_factor_degrees_over_Fp(x1,x3)'] = sorted(int(g.degree()) for g, e in fac4 for _ in range(e))
    # numeric census on the locus
    cov = Cover(p, a, b, mmax=4)
    for m in (3, 4):
        cnt = collections.Counter(); N = 3000 if p > 50 else 2000
        for _ in range(N):
            xa = F.random_element()
            if cov.f(xa) == 0:
                continue
            xb = dbl_x(F(a), F(b), xa)
            xs = [xa, xb] + ([F.random_element()] if m == 4 else [])
            st, chis, ct, pred = cov.classify(m, xs)
            cnt[st] += 1
            if st == 'ok':
                cnt['rule_match' if ct == pred else 'RULE_MISMATCH'] += 1
                cnt['identity' if len(set(ct)) == 1 and ct[0] == 1 else 'nonidentity'] += 1
        ok = cnt['ok']
        rec['m%d_census' % m] = {'counts': dict(cnt), 'identity_fraction_on_locus': float(cnt['identity'] / ok) if ok else None,
                                 'generic_identity_fraction': 1.0 / 2 ** (m - 2)}
    A['%d,%d,%d' % (p, a, b)] = rec
    say('  ', (p, a, b), rec)
summary['A_locus_x2_eq_x2P1'] = A

# ------------------------------------------------------------------ B': square-discriminant sub-cover at m = 4
say("== Control B': square-discriminant sub-cover of the symmetric base, m = 4 -> A_4")
Bp = {}
for (p, a, b) in [(1009, 5, 7), (101, 2, 3)]:
    F = GF(p)
    PX = PolynomialRing(F, 'x'); x = PX.gen()
    cnt = collections.Counter(); N = 4000
    Kc = {}
    for _ in range(N):
        g = x ** 3 + sum(F.random_element() * x ** i for i in range(3))
        if not g.is_squarefree() or not g.discriminant().is_square():
            continue
        degs = [int(h.degree()) for h, e in g.factor()]
        k = lcm(degs)
        K = Kc.setdefault(k, GF(p ** k, 'w') if k > 1 else F)
        roots = [r for r, e in g.change_ring(K).roots()]
        if any(r ** 3 + K(a) * r + K(b) == 0 for r in roots):
            continue
        PT = PolynomialRing(K, 'T'); T = PT.gen(); PTX = PolynomialRing(PT, 'X'); X = PTX.gen()
        Fq = PTX(S3_expr(K(a), K(b), roots[0], roots[1], X)).resultant(PTX(S3_expr(K(a), K(b), roots[2], T, X)))
        Fq = PolynomialRing(F, 'T')([F(c) for c in Fq.list()])
        if Fq.degree() != 4 or gcd(Fq, Fq.derivative()).degree() != 0:
            continue
        ct = tuple(sorted(int(h.degree()) for h, e in Fq.factor() for _ in range(e)))
        cnt[ct] += 1
    tot = sum(cnt.values())
    A4 = {(1, 1, 1, 1): 1 / 12, (2, 2): 3 / 12, (1, 3): 8 / 12}
    S4 = {(1, 1, 1, 1): 1 / 24, (2, 2): 3 / 24, (1, 3): 8 / 24, (1, 1, 2): 6 / 24, (4,): 6 / 24}

    def chi2(obs, probs):
        s = 0.0; imp = {}
        for k in set(obs) | set(probs):
            o = obs.get(k, 0); pk = probs.get(k, 0)
            if pk == 0:
                if o: imp[str(k)] = o
                continue
            s += (o - pk * tot) ** 2 / (pk * tot)
        return round(float(s), 1), imp
    Bp['%d,%d,%d' % (p, a, b)] = {'n': tot, 'observed': {str(k): v for k, v in cnt.items()},
                                  'chi2_vs_A4': chi2(cnt, A4), 'chi2_vs_S4': chi2(cnt, S4),
                                  'S4_only_types_seen': int(cnt[(1, 1, 2)] + cnt[(4,)])}
    say('  ', (p, a, b), Bp['%d,%d,%d' % (p, a, b)])
summary['Bprime_square_discriminant_A4'] = Bp

# ------------------------------------------------------------------ C: singular cubics; D: p = 3
say('== Controls C (singular cubics) and D (p = 3): outside scope, what survives?')
CD = {}
for (q, a, b, tag) in [(101, 0, 0, 'cusp y^2=x^3'), (101, -3, 2, 'node y^2=(x-1)^2(x+2)'),
                       (13, 0, 0, 'cusp'), (13, -3, 2, 'node'),
                       (3, 1, 1, 'p=3 nonsingular (disc=31)'), (27, 1, 1, 'F_27, same curve')]:
    cov = Cover(q, a, b, mmax=5)
    rec = {'tag': tag, 'singular': bool(cov.singular)}
    F = cov.F
    for m in (3, 4, 5):
        n = m - 1
        if q ** n <= 15000:
            tuples = itertools.product(F, repeat=n); N = q ** n; exh = True
        else:
            N = 3000 if m < 5 else 800; tuples = ([F.random_element() for _ in range(n)] for _ in range(N)); exh = False
        cnt = collections.Counter(); cts = collections.Counter()
        for xs in tuples:
            xs = list(xs)
            st, chis, ct, pred = cov.classify(m, xs)
            cnt[st] += 1
            if st == 'ok':
                cts[ct] += 1
                cnt['rule_match' if ct == pred else 'RULE_MISMATCH'] += 1
        rec['m=%d' % m] = {'exhaustive': exh, 'N': N, 'counts': dict(cnt), 'cycle_types': {str(k): v for k, v in cts.items()}}
        say('  ', (q, a, b, tag), 'm=%d' % m, rec['m=%d' % m])
    CD['%d,%d,%d' % (q, a, b)] = rec
summary['C_D_singular_and_p3'] = CD

with open(os.path.join(OUT, 'controls_summary.json'), 'w') as fh:
    json.dump(summary, fh, indent=1, default=str)
say('wrote', os.path.join(OUT, 'controls_summary.json'))
