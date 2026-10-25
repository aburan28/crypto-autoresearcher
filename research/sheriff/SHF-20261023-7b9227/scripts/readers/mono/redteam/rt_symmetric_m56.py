"""Symmetric-base Frobenius cycle-type census at m = 5 and m = 6 -- the part of
KN-FIND-bdcd60 (2) that NO record measured (both reviews measured the symmetric base
only at m = 4; the orders 192 and 1920 and the primitivity statements rest on the
derivation plus a curve-free permutation computation).

For random monic squarefree g of degree n = m-1 over F_p with roots x_1..x_n in the
splitting field F_{p^k}, F(T) = S_m(x_1..x_n, T) has coefficients in F_p (checked),
and its factor pattern over F_p is the Frobenius cycle type on the fibre.  The
observed distribution is compared with the Chebotarev class densities of the group
predicted by rt_groups.py (file rt_groups_out.json).  A cycle type of predicted
density 0 on an admissible fibre refutes the group; a chi-square beyond the declared
bound is a mismatch.
"""
import json, sys, time, random
from sage.all import GF, PolynomialRing, lcm, Integer
from rt_semaev import fibre_poly, cycle_type

OUT = sys.argv[1] if len(sys.argv) > 1 else 'rt_symmetric_m56_out.json'
PRED = json.load(open(sys.argv[2] if len(sys.argv) > 2 else 'rt_groups_out.json'))
cfg = [  # (m, p, a, b, N, seed, label)
    (5, 1009, 2, 3, 6000, 5001, 'generic'),
    (5, 1009, 0, 7, 3000, 5002, 'j=0 (a=0), p=1 mod 3'),
    (5, 1013, 5, 0, 3000, 5003, 'j=1728 (b=0), p=1 mod 4'),
    (5, 1019, 0, 1, 3000, 5004, 'supersingular x^3+1, p=2 mod 3'),
    (6, 1009, 2, 3, 1200, 6001, 'generic'),
    (6, 1019, 0, 1, 600, 6002, 'supersingular x^3+1'),
]
if len(sys.argv) > 3 and sys.argv[3] == 'quick':
    cfg = [(5, 1009, 2, 3, 300, 1, 'quick'), (6, 1009, 2, 3, 40, 2, 'quick')]

t0 = time.time()
results = []
for (m, p, a, b, N, seed, label) in cfg:
    n = m - 1
    Fp = GF(p)
    Rg = PolynomialRing(Fp, 'X')
    rng = random.Random(seed)
    fields = {}
    pred = {tuple(json.loads(k)): v for k, v in PRED[str(m)]['symmetric_cycle_type_densities'].items()}
    tally = {}
    counts = dict(samples=0, g_not_squarefree=0, coeff_not_in_Fp=0, degree_drop=0, F_not_squarefree=0, admissible=0)
    impossible = []
    for _ in range(N):
        counts['samples'] += 1
        g = Rg([Fp(rng.randrange(p)) for _ in range(n)] + [Fp(1)])
        if not g.is_squarefree():
            counts['g_not_squarefree'] += 1
            continue
        k = int(lcm([h.degree() for h, e in g.factor()]))
        if k not in fields:
            fields[k] = GF(p ** k, 'w') if k > 1 else Fp
        Fk = fields[k]
        roots = [r for r, e in g.change_ring(Fk).roots()]
        assert len(roots) == n
        FT = fibre_poly(m, roots, a, b, Fk)
        cs = FT.list()
        if k > 1:
            if any(c ** p != c for c in cs):
                counts['coeff_not_in_Fp'] += 1
                continue
            RT = PolynomialRing(Fp, 'T')
            FT = RT([Fp(c.polynomial().constant_coefficient()) if c != 0 else Fp(0) for c in cs])
        if FT.degree() < 2 ** (m - 2):
            counts['degree_drop'] += 1
            continue
        ct = cycle_type(FT)
        if ct is None:
            counts['F_not_squarefree'] += 1
            continue
        counts['admissible'] += 1
        tally[ct] = tally.get(ct, 0) + 1
        if pred.get(ct, 0.0) == 0.0:
            impossible.append(dict(g=[int(c) for c in g.list()], pattern=list(ct)))
    # chi-square against predicted densities over admissible fibres (classes with expected >= 5 pooled)
    A = counts['admissible']
    rows = []
    chi2 = 0.0
    df = -1
    pooled_obs = pooled_exp = 0.0
    for ct, dens in sorted(pred.items(), key=lambda kv: -kv[1]):
        exp = dens * A
        obs = tally.get(ct, 0)
        rows.append(dict(pattern=list(ct), predicted_density=round(dens, 5), expected=round(exp, 1), observed=obs,
                         z=round((obs - exp) / (exp * (1 - dens)) ** 0.5, 2) if exp > 0 else None))
        if exp >= 5:
            chi2 += (obs - exp) ** 2 / exp
            df += 1
        else:
            pooled_obs += obs
            pooled_exp += exp
    if pooled_exp > 0:
        chi2 += (pooled_obs - pooled_exp) ** 2 / pooled_exp
        df += 1
    res = dict(m=m, p=p, a=a, b=b, label=label, predicted_group_order=PRED[str(m)]['symmetric_order'],
               predicted_primitive=PRED[str(m)]['symmetric_is_primitive'], counts=counts,
               observed_patterns_not_in_group=impossible, classes=rows, chi2=round(chi2, 2), df=df,
               n_observed_types=len(tally), n_predicted_types=len(pred), seconds=round(time.time() - t0, 1))
    results.append(res)
    print(json.dumps({k: v for k, v in res.items() if k != 'classes'}))
    for r in rows:
        print('   ', r)
    sys.stdout.flush()

json.dump(results, open(OUT, 'w'), indent=1)
print('wrote', OUT, 'seconds', round(time.time() - t0, 1))
