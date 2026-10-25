"""Independent recomputation (disjoint code) of headline counts quoted in KN-FIND-bdcd60 / the
8aff64 and ccd10c reports, now that the producer reports have been read (post-blind phase):
  N1  exhaustive ordered base, y^2 = x^3 + 2x + 3 / F_53, m = 4: 148,877 tuples; claimed 95,328
      nondegenerate (squarefree, degree 4, all f(x_i) != 0) with 19,488 of type 1^4.
  N2  OBS-1 regeneration: all monic cubics g splitting over F_101 with multiplicity, i.e. multisets
      {x1 <= x2 <= x3} in F_101 (C(103,3) = 176,851 per curve), on C1 (101,2,3) and C2 (101,1,35);
      census label = factor degrees of F with multiplicity, padded with (4 - deg F) roots at
      infinity.  Claimed: label 2+1+1 counts 7,323 (C1) and 4,920 (C2), total 12,243, all
      non-squarefree (none a squarefree full-degree fibre); label 1^4: 44,759 / 50,161;
      label 2+2: 119,618 / 121,770; excluded (some f(x_i) = 0): 5,151 / 0.
  N3  exhaustive ordered base C1 (101,2,3), m = 4: claimed (ccd10c Table 5.1) 1,030,301 tuples,
      f(x_i)=0: 30,301, degree drop 9,836, not squarefree 58,628, admissible 931,536,
      1^4: 214,416, 2^2: 717,120, all-chi-equal count 252,700 = 47^3 + 53^3.
NOTE on N3 conventions: ccd10c's "degree drop" and "not squarefree" are counted on the TRUE
specialised S_4; my fibre_poly uses the specialised resultant, which differs from the true S_4
only when x_1 = x_2 (then it has lower degree).  So I compute the true S_4 fibre from the
symbolic S_4 for N2/N3 (slower but exact), and classify exactly as ccd10c does.
Usage: sage -python recompute_producer_numbers.py OUTDIR
"""
import sys, json, itertools, collections, os, time
from sage.all import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mono_lib import S3_expr, symbolic_S

OUT = sys.argv[1]
res = {}


def true_fibre_S4(S4, F, xs, PT):
    """S_4(x1,x2,x3,T) from the symbolic S_4 (exact even when x_i coincide)."""
    T = PT.gen()
    return PT(S4(F(xs[0]), F(xs[1]), F(xs[2]), T, 0))


def classify_true(Fp, deg_full=4):
    """Returns (degree, squarefree, factor-degree multiset with multiplicity)."""
    d = Fp.degree()
    if Fp == 0:
        return (-1, False, None)
    fac = Fp.factor()
    degs = sorted([int(g.degree()) for g, e in fac for _ in range(e)])
    sqf = all(e == 1 for g, e in fac)
    return (d, sqf, degs)


def run_exhaustive_ordered(p, a, b, label):
    t0 = time.time()
    F = GF(p); R4, S4 = symbolic_S(4, F(a), F(b), F)
    PT = PolynomialRing(F, 'T')
    f = lambda x: x ** 3 + F(a) * x + F(b)
    chi = {x: (0 if f(x) == 0 else (1 if f(x).is_square() else -1)) for x in F}
    # cache fibre polynomials by sorted tuple (S_4 symmetric) to cut work ~6x
    cache = {}
    cnt = collections.Counter(); types = collections.Counter(); allchi = 0
    for xs in itertools.product(list(F), repeat=3):
        chis = (chi[xs[0]], chi[xs[1]], chi[xs[2]])
        if 0 in chis:
            cnt['f_zero'] += 1; continue
        if len(set(chis)) == 1:
            allchi += 1
        key = tuple(sorted(xs, key=int))
        if key not in cache:
            cache[key] = classify_true(true_fibre_S4(S4, F, key, PT))
        d, sqf, degs = cache[key]
        if d < 4:
            cnt['degree_drop'] += 1; continue
        if not sqf:
            cnt['not_squarefree'] += 1; continue
        cnt['admissible'] += 1
        types[tuple(degs)] += 1
        pred = (1, 1, 1, 1) if len(set(chis)) == 1 else (2, 2)
        if tuple(degs) != pred:
            cnt['RULE_MISMATCH'] += 1
    out = {'tuples': p ** 3, 'counts': dict(cnt), 'types': {str(k): v for k, v in types.items()},
           'all_chi_equal_over_f_nonzero': allchi, 'seconds': round(time.time() - t0, 1)}
    print(label, out, flush=True)
    return out


def run_obs1(p, a, b, label):
    t0 = time.time()
    F = GF(p); R4, S4 = symbolic_S(4, F(a), F(b), F)
    PT = PolynomialRing(F, 'T')
    f = lambda x: x ** 3 + F(a) * x + F(b)
    labels = collections.Counter(); excluded = 0
    two11 = {'non_squarefree': 0, 'squarefree_deg4': 0, 'squarefree_deg3': 0, 'other': 0}
    mech = collections.Counter()
    elems = sorted(list(F), key=int)
    for i in range(p):
        for j in range(i, p):
            for k in range(j, p):
                xs = (elems[i], elems[j], elems[k])
                if any(f(x) == 0 for x in xs):
                    excluded += 1; continue
                d, sqf, degs = classify_true(true_fibre_S4(S4, F, xs, PT))
                if d < 0:
                    labels['zero_poly'] += 1; continue
                lab = tuple(sorted(degs + [1] * (4 - d)))   # pad roots at infinity
                labels[lab] += 1
                if lab == (1, 1, 2):
                    if not sqf:
                        two11['non_squarefree'] += 1
                        if xs[0] == xs[1] or xs[1] == xs[2]:
                            mech['repeated_x'] += 1
                        else:
                            mech['other_non_squarefree'] += 1
                    elif d == 4:
                        two11['squarefree_deg4'] += 1
                    elif d == 3:
                        two11['squarefree_deg3'] += 1
                    else:
                        two11['other'] += 1
    out = {'multisets': int(binomial(p + 2, 3)), 'excluded_f_zero': excluded,
           'labels': {str(k): v for k, v in sorted(labels.items())}, 'label_2+1+1_breakdown': two11,
           'mechanisms_of_non_squarefree_2+1+1': dict(mech), 'seconds': round(time.time() - t0, 1)}
    print(label, out, flush=True)
    return out


res['N1_exhaustive_53_2_3_m4'] = run_exhaustive_ordered(53, 2, 3, 'N1 (53,2,3) m=4')
json.dump(res, open(os.path.join(OUT, 'recompute_producer_numbers.json'), 'w'), indent=1, default=str)
res['N2_obs1_C1_101_2_3'] = run_obs1(101, 2, 3, 'N2 C1 (101,2,3)')
json.dump(res, open(os.path.join(OUT, 'recompute_producer_numbers.json'), 'w'), indent=1, default=str)
res['N2_obs1_C2_101_1_35'] = run_obs1(101, 1, 35, 'N2 C2 (101,1,35)')
json.dump(res, open(os.path.join(OUT, 'recompute_producer_numbers.json'), 'w'), indent=1, default=str)
res['N3_exhaustive_101_2_3_m4'] = run_exhaustive_ordered(101, 2, 3, 'N3 C1 (101,2,3) m=4')
json.dump(res, open(os.path.join(OUT, 'recompute_producer_numbers.json'), 'w'), indent=1, default=str)
print('done')
