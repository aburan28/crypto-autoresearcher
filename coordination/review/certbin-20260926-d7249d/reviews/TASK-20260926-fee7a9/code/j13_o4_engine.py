"""J13 O4: pinned engine (unchanged) on the kept N-PERT19 systems: M_3, M_4, W_4; rc_b
(my substitution v_{j*} := ell + v_{j*}; R''_3 / R''_4 by the pinned engine) where the
quadratic left kernel is 1-dimensional. Then my own literal W_4 on every kept system."""
import sys, json, time
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[2])
from crypto_autoresearcher.gf2 import closure, _native
from rtlib19 import decode_E_hex, quad_kernel, combo, substitute, Mono, macaulay, literal_W
inp, outp, own = sys.argv[3], sys.argv[4], ('--own' in sys.argv)
C3 = closure.Closure(20, 3, 19); C4 = closure.Closure(20, 4, 19)
R3 = closure.Closure(19, 3, 19); R4 = closure.Closure(19, 4, 19)
M20_4 = Mono(20, 4)
fo = open(outp, 'w')
for line in open(inp):
    r = json.loads(line)
    P = decode_E_hex(r['E_hex'])
    eqs = [sorted(s) for s in P]
    t0 = time.time()
    m3, _ = C3.macaulay_closure(eqs, want_cert=False)
    m4, _ = C4.macaulay_closure(eqs, want_cert=False)
    w4, _ = C4.w_closure(eqs, want_cert=False)
    rec = {'key': r['key'], 'family': r['family'], 'k': r['k'], 'pair': r['pair'], 'c_k_trace': r['c_k_trace'],
           'kernel_dim': r['kernel_dim'], 'ell_survives': r['ell_survives_by_rule'], 'M_3': m3, 'M_4': m4, 'W_4': w4,
           'backend': _native.build_info.get('backend')}
    K = quad_kernel(P)
    if len(K) == 1:
        ell = combo(P, K[0])
        lin = [i for i in range(20) if (1 << i) in ell]
        rec['ell_linear_support'] = lin
        rec['ell_const'] = 1 if 0 in ell else 0
        if lin:
            Ps, js, L, rel = substitute(P, ell)
            e19 = [sorted(s) for s in Ps]
            r3, _ = R3.macaulay_closure(e19, want_cert=False)
            r4, _ = R4.macaulay_closure(e19, want_cert=False)
            rec['rc_b'] = {'jstar': js, 'R3': r3, 'R4': r4, 'sigma': r4['dims_by_deg'][3] - 360}
    rec['engine_seconds'] = round(time.time() - t0, 2)
    if own:
        t1 = time.time()
        E4 = macaulay(P, M20_4, 4)
        ow, _ = literal_W(P, M20_4, 4, start=E4)
        rec['own_W_4'] = {k: ow[k] for k in ('dims', 'iterations_to_fixpoint', 'final_dim', 'one', 'one_first_iteration', 'dims_by_deg')}
        rec['own_M_4'] = {'rank': E4.dim(), 'one': E4.has_one(), 'dims_by_deg': E4.dims_by_deg(M20_4)}
        rec['own_agrees_with_engine'] = all(rec['own_W_4'][k] == w4[k] for k in rec['own_W_4']) and rec['own_M_4'] == {k: m4[k] for k in ('rank', 'one', 'dims_by_deg')}
        rec['own_seconds'] = round(time.time() - t1, 2)
    fo.write(json.dumps(rec) + '\n'); fo.flush()
    print(rec['key'], 'ker', rec['kernel_dim'], 'ell', rec['ell_survives'], 'M4', m4['one'], m4['dims_by_deg'], 'W4', w4['one'], w4['dims'], w4['one_first_iteration'], 'R4', rec.get('rc_b', {}).get('R4', {}).get('dims_by_deg'), 'own', rec.get('own_agrees_with_engine'), flush=True)
