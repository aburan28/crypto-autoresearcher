"""J10 (2): decompose sigma = dim(R'_4 cap B'_{<=3}) - 360 on archived systems (own code).
Chain (all subspaces of B'_{<=3}, F3 := R'_4 cap B'_{<=3}, F2 := R'_4 cap B'_{<=2}):
  s0 = rank R'_3 (semi-regular reference 360)
  s1 = dim(R'_3 + F2)                                  [degree-<=2 falls]
  s2 = dim((R'_3 + F2 + lambda*B'_{<=2}) cap F3)       [linear forms lambda in R'_4, if any]
  s3 = dim((R'_3 + F2 + lambda*B'_{<=2} + v_j*F2) cap F3)  [products of degree-<=2 falls]
  residual = dim F3 - s3                               [degree-3 fall not generated from lower falls]
Also: a = dim span of substituted equations, r_q = rank of their quadratic parts."""
import sys, json, gzip
sys.path.insert(0, sys.argv[1])
from rtlib19 import *
run, outp, keys = sys.argv[2], sys.argv[3], sys.argv[4].split(',')
Bc = 306147
inst = {}
for l in gzip.open(run + '/instances.jsonl.gz', 'rt'):
    r = json.loads(l); inst[r['key']] = r
M19_3 = Mono(19, 3); M19_4 = Mono(19, 4)
fo = open(outp, 'w')
def span_dim(rows):
    e = Echelon()
    for x in rows:
        e.add(x)
    return e
def inter_dim(EA, EB):
    # dim(A cap B) = dim A + dim B - dim(A + B)
    S = EA.copy()
    for x in EB.piv.values():
        S.add(x)
    return EA.dim() + EB.dim() - S.dim()
for key in keys:
    r = inst[key]
    P = decode_E_hex(r['E_hex'])
    K = quad_kernel(P)
    ell = combo(P, K[0]) if r['arm'] != 'N-ELL19' else set(P[18])
    Ps, js, L, rel = substitute(P, ell)
    # span of substituted equations and quadratic rank
    eq = span_dim([M19_4.poly_from_masks(f) for f in Ps])
    quad = span_dim([M19_4.poly_from_masks({m for m in f if bin(m).count('1') == 2}) for f in Ps])
    R3 = macaulay(Ps, M19_3, 3); R4 = macaulay(Ps, M19_4, 4)
    dbd = R4.dims_by_deg(M19_4)
    F3rows = R4.low_rows(M19_4, 3); F2rows = R4.low_rows(M19_4, 2); F1rows = R4.low_rows(M19_4, 1)
    EF3 = span_dim(F3rows)
    r3rows = [M19_4.poly_from_masks(M19_3.masks_of(x)) for x in R3.piv.values()]
    E0 = span_dim(r3rows)
    E1 = E0.copy()
    for x in F2rows: E1.add(x)
    E2 = E1.copy()
    lam = [x for x in F1rows]
    deg2 = [m for m in M19_4.masks if bin(m).count('1') <= 2]
    for x in lam:
        xm = set(M19_4.masks_of(x))
        for m in deg2:
            E2.add(M19_4.poly_from_masks(mul_masks({m}, xm)))
    E3 = E2.copy()
    for p in M19_4.times_all_vars_batch(F2rows):
        E3.add(p)
    s0 = E0.dim(); s1 = E1.dim()  # both inside F3
    s2 = inter_dim(E2, EF3); s3 = inter_dim(E3, EF3)
    res = {'key': key, 'arm': r['arm'], 'jstar': js,
           'dim_span_substituted_eqs': eq.dim(), 'rank_quadratic_parts': quad.dim(),
           'affine_forms_in_span': eq.dim() - quad.dim(),
           'R3_rank': R3.dim(), 'R4_dims_by_deg': dbd, 'sigma': dbd[3] - 360,
           'sigma_split': {'deg_le2_excess (d2-18)': dbd[2] - 18, 'exact_deg3_excess (d3-d2-342)': dbd[3] - dbd[2] - 342},
           'chain': {'s0_rankR3': s0, 's1_plus_F2': s1, 's2_plus_linear_form_multiples': s2, 's3_plus_vj_F2_products': s3, 'dimF3': EF3.dim(),
                     'residual_genuine_deg3': EF3.dim() - s3},
           'n_linear_forms': len(lam)}
    fo.write(json.dumps(res) + '\n'); fo.flush()
    print(json.dumps(res), flush=True)
