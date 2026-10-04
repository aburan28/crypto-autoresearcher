"""Cross-check of RUN-SEMBIN-5ed13e n=45 draw 0 (D=4 insufficient, rank 166705,
std 13681, |V|=2): same instance file, a different elimination routine
(mzd_echelonize, method 0) and a different batching (cap given), with the
evaluation check at a verified common zero on every elimination."""
import sys, json, time, ctypes
sys.path.insert(0, '.'); sys.path.insert(0, '/home/user/crypto-autoresearcher/harness/macaulay_fp/fixtures')
import closure_cert, soundness_probe
INST = sys.argv[3]
method, cap = int(sys.argv[1]), float(sys.argv[2])
d = json.load(open(INST)); inst = {**d['meta'], **d['system']}
assign, nf = soundness_probe.solution_assignment(inst)
bad = sum(1 for e in inst['equations'] if soundness_probe.evaluate(e, assign))
print(f"instance N={inst['N']} sha={d['system_sha256'][:16]} solutions listed={nf}; witness violates {bad} generators (must be 0)", flush=True)
L = closure_cert._lib
L.closure_set_witness.argtypes = [ctypes.c_uint64]; L.closure_set_witness(assign)
L.closure_set_method.argtypes = [ctypes.c_int]; L.closure_set_method(method)
print('elimination', ['mzd_echelonize','mzd_echelonize_pluq','mzd_echelonize_m4ri'][method], 'cap', cap, 'm4ri', closure_cert.M4RI_LIBRARY, flush=True)
t = time.time()
c = closure_cert.closure_certificate(inst['N'], inst['equations'], 4, cap, s_known=int(sys.argv[4]), standard_cap=200000)
print(f"DONE {time.time()-t:.0f}s status={c.get('status')} rank={c.get('rank')}/{c.get('ncols')} contains_one={c.get('contains_one')} "
      f"std={c.get('standard_monomials')} verdict={c.get('verdict')} lm_sha={c.get('basis_lm_sha256')} faults={c.get('elimination_faults')} "
      f"iters={[(x['rows'], x['rank_after'], x['new_pivots']) for x in c['iterations']]}", flush=True)
