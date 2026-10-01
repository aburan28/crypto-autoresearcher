"""J11 (2): own-code profiles of every UNSATISFIABLE N-F219 and N-AFF19 system
(M_3 and M_4: rank, one, dims_by_deg) and every UNSATISFIABLE N-ELL19 system
(R'_3 and R'_4 after v_{j*} := ell + v_{j*} with ell = f_18, the spec's c = e_18;
also the M_3/M_4 profile). Also checks structural constraints read from the
spec: N-ELL19 row 18 has no quadratic part (= ell_lin + c); support inside U is
checked elsewhere. No crypto_autoresearcher import.
Usage: j11_profiles.py <codedir> <run_dir> <out_jsonl> <shard> <nshards>"""
import sys, json, gzip, time
sys.path.insert(0, sys.argv[1])
from rtlib19 import *
run, outp, shard, nsh = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
recs = [json.loads(l) for l in gzip.open(run + '/instances.jsonl.gz', 'rt')]
todo = [r for r in recs if r['arm'] in ('N-F219', 'N-AFF19', 'N-ELL19') and r['role'] == 'unsat']
todo.sort(key=lambda r: (r['arm'], r['index']))
todo = todo[shard::nsh]
M20_3 = Mono(20, 3); M20_4 = Mono(20, 4); M19_3 = Mono(19, 3); M19_4 = Mono(19, 4)
fo = open(outp, 'w')
for r in todo:
    t0 = time.time()
    P = decode_E_hex(r['E_hex'])
    res = {'key': r['key'], 'arm': r['arm'], 'family': r.get('family')}
    E3 = macaulay(P, M20_3, 3); E4 = macaulay(P, M20_4, 4)
    res['M_3'] = {'rank': E3.dim(), 'one': E3.has_one(), 'dims_by_deg': E3.dims_by_deg(M20_3)}
    res['M_4'] = {'rank': E4.dim(), 'one': E4.has_one(), 'dims_by_deg': E4.dims_by_deg(M20_4)}
    K = quad_kernel(P)
    res['kernel_dim'] = len(K)
    if r['arm'] == 'N-ELL19':
        f18 = P[18]
        res['row18_has_quadratic'] = any(bin(m).count('1') == 2 for m in f18)
        res['row18_masks'] = sorted(f18)
        res['e18_in_kernel'] = any(c == [0] * 18 + [1] for c in K) or (len(K) >= 1 and not res['row18_has_quadratic'])
        Ps, js, L, rel = substitute(P, set(f18))
        res['jstar'] = js
        R3 = macaulay(Ps, M19_3, 3); R4 = macaulay(Ps, M19_4, 4)
        res['R3'] = {'rank': R3.dim(), 'one': R3.has_one(), 'dims_by_deg': R3.dims_by_deg(M19_3)}
        res['R4'] = {'rank': R4.dim(), 'one': R4.has_one(), 'dims_by_deg': R4.dims_by_deg(M19_4)}
        res['T5_applicable'] = R4.dims_by_deg(M19_4)[3] == R3.dim()
    res['seconds'] = round(time.time() - t0, 2)
    fo.write(json.dumps(res) + '\n'); fo.flush()
