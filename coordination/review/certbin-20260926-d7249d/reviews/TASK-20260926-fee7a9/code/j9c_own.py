"""J9 (c) own-code computations (no crypto_autoresearcher import).
Usage: j9c_own.py <codedir> <run_dir> <out_jsonl> <keys comma-separated> [--w4]
Computes Q1..Q7 as declared in j9-pattern/c-artefact-signatures.yaml."""
import sys, json, gzip, time
sys.path.insert(0, sys.argv[1])
from rtlib19 import *
run, outp, keys = sys.argv[2], sys.argv[3], sys.argv[4].split(',')
do_w4 = '--w4' in sys.argv
do_w3 = '--w3' in sys.argv
Bc = 306147
inst = {}
for l in gzip.open(run + '/instances.jsonl.gz', 'rt'):
    r = json.loads(l)
    inst[r['key']] = r
M20_3 = Mono(20, 3); M20_4 = Mono(20, 4); M19_3 = Mono(19, 3); M19_4 = Mono(19, 4)
fo = open(outp, 'a')
for key in keys:
    t0 = time.time()
    r = inst[key]
    P = decode_E_hex(r['E_hex'])
    res = {'key': key, 'arm': r['arm'], 'x_R': r.get('x_R')}
    # Q1 construction
    if r['arm'] in ('S3-U400', 'S3-SAT100', 'F-RANDX19'):
        own = s3_descent(r['x_R'], Bc)
        res['Q1_E_equal'] = (own == P)
    elif r['arm'] == 'N-CONV19':
        own = s3_descent(r['x_R'], Bc)
        qo = [{m for m in f if bin(m).count('1') == 2} for f in own]
        qa = [{m for m in f if bin(m).count('1') == 2} for f in P]
        res['Q1_quadratic_part_equal'] = (qo == qa)
        res['Q1_lower_part_differs_from_S3'] = ([{m for m in f if bin(m).count('1') < 2} for f in own] != [{m for m in f if bin(m).count('1') < 2} for f in P])
    # Q2 M_3, M_4
    E3 = macaulay(P, M20_3, 3)
    res['M_3'] = {'rank': E3.dim(), 'one': E3.has_one(), 'dims_by_deg': E3.dims_by_deg(M20_3)}
    E4 = macaulay(P, M20_4, 4)
    res['M_4'] = {'rank': E4.dim(), 'one': E4.has_one(), 'dims_by_deg': E4.dims_by_deg(M20_4)}
    # Q3 kernel / ell
    K = quad_kernel(P)
    res['kernel_dim'] = len(K)
    if len(K) >= 1:
        c = K[0]
        if r.get('x_R'):
            inv2 = finv(fmul(r['x_R'], r['x_R']))
            cexp = [ftr(fmul(1 << k, inv2)) for k in range(19)]
            res['c_equals_trace_vector'] = (c == cexp) if len(K) == 1 else None
            res['Tr_B_over_xR2'] = ftr(fmul(Bc, inv2))
        ell = combo(P, c)
        res['ell_masks'] = sorted(ell)
        res['ell_linear_support'] = sorted(i for i in range(20) if (1 << i) in ell)
        res['ell_const'] = 1 if 0 in ell else 0
        # Q4 ell_route directly
        Er = E4.copy()
        ellq = {m for m in ell}
        for m in M20_4.masks:
            if bin(m).count('1') <= 3:
                Er.add(M20_4.poly_from_masks(mul_masks({m}, ellq)))
        res['ell_route_direct'] = Er.has_one()
        res['dim_M4_plus_ellB3'] = Er.dim()
        # Q5 substitution
        if res['ell_linear_support'] and len(K) == 1:
            Ps, js, L, rel = substitute(P, ell)
            res['jstar'] = js
            res['L_masks'] = sorted(L)
            R3 = macaulay(Ps, M19_3, 3)
            R4 = macaulay(Ps, M19_4, 4)
            res['R3'] = {'rank': R3.dim(), 'one': R3.has_one(), 'dims_by_deg': R3.dims_by_deg(M19_3)}
            res['R4'] = {'rank': R4.dim(), 'one': R4.has_one(), 'dims_by_deg': R4.dims_by_deg(M19_4)}
            res['sigma'] = R4.dims_by_deg(M19_4)[3] - 360
            res['T5_applicable'] = (R4.dims_by_deg(M19_4)[3] == R3.dim())
            # Q6 fill decomposition on the substituted system
            fill = {}
            low2 = R4.low_rows(M19_4, 2)
            low3 = R4.low_rows(M19_4, 3)
            only3 = [x for x in low3 if M19_4.deg[x.bit_length() - 1] == 3]
            for name, rows in (('products_of_fallen_deg_le2', low2), ('products_of_fallen_deg3_only', only3), ('products_of_all_fallen_deg_le3', low3)):
                Ef = R4.copy()
                for p in M19_4.times_all_vars_batch(rows):
                    Ef.add(p)
                fill[name] = {'n_multiplicands': len(rows), 'dim': Ef.dim(), 'one': Ef.has_one(), 'dims_by_deg': Ef.dims_by_deg(M19_4)}
            # R'_3 rows alone (sanity: products of R'_3 rows are R'_4 rows)
            Ef = R4.copy()
            r3rows = list(R3.piv.values())
            # R3 is in Mono(19,3) order; re-embed into Mono(19,4)
            r3rows4 = [M19_4.poly_from_masks(M19_3.masks_of(x)) for x in r3rows]
            for p in M19_4.times_all_vars_batch(r3rows4):
                Ef.add(p)
            fill['products_of_R3_span_only'] = {'n_multiplicands': len(r3rows4), 'dim': Ef.dim(), 'one': Ef.has_one()}
            res['fill_substituted_iteration1'] = fill
            # Q6 literal W'_4
            recp, EWp = literal_W(Ps, M19_4, 4, start=R4)
            res["W'_4"] = recp
    # Q7 own literal W_4 at nv = 20
    if do_w4:
        rec4, EW4 = literal_W(P, M20_4, 4, start=E4)
        res['W_4'] = rec4
        # fill decomposition at nv = 20 (n = 17 O-8 analogue)
        low3 = E4.low_rows(M20_4, 3)
        res['M4_fallen_dim'] = len(low3)
    if do_w3:
        rec3, EW3 = literal_W(P, M20_3, 3, start=E3)
        res['W_3'] = rec3
    res['seconds'] = round(time.time() - t0, 2)
    fo.write(json.dumps(res) + '\n'); fo.flush()
    print(key, res['seconds'], {k: res.get(k) for k in ('Q1_E_equal', 'Q1_quadratic_part_equal', 'M_4', 'ell_route_direct', 'R4', "W'_4", 'W_4', 'W_3')}, flush=True)
