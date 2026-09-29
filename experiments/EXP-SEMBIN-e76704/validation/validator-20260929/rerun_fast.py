# Validator re-execution of C1, T1, C2, T3, T4 from the committed src/ (imported, not copied).
import sys, json, time, random
SRC = "/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src"
sys.dont_write_bytecode = True
sys.path.insert(0, SRC)
import run_separation as R
from ffd_semaev import build_system, a_real_xR, popcount
from recomb_search import ffd as slow_ffd, new_falls_at as slow_nf, _tables, recombine
from fastfall import Kernel
out = {"tests": {}, "controls": {}}
t0 = time.time()
reg = []
for n, npr in R.REGRESSION_CELLS:
    rng = random.Random(n*100+npr); xR = a_real_xR(n,1,1,rng)
    basis = ([1]+[1<<j for j in range(1,npr)])[:npr]
    eqs = build_system(n,npr,1,xR,basis); N = 2*npr
    s = slow_ffd(eqs,N,tabs=_tables(N)); f = Kernel(eqs,N).ffd([1<<j for j in range(len(eqs))],{})
    reg.append(dict(cell=[n,npr],original=s,fast=f,match=(s==f)))
out["controls"]["C1_kernel_regression"] = dict(cells=reg, all_match=all(r["match"] for r in reg))
sem63,_,xR63 = R.cell_systems(6,3); N=6
req = recombine(sem63,[1,2,4,8,26]); tabs=_tables(N)
out["tests"]["T1_witness"] = dict(D_ff_identity=slow_ffd(sem63,N,tabs=tabs), D_ff_M=slow_ffd(req,N,tabs=tabs),
    new_falls_identity=[slow_nf(sem63,N,D,tabs) for D in (1,2,3)],
    new_falls_M=[slow_nf(req,N,D,tabs) for D in (1,2,3)],
    degrees_identity=[max(popcount(m) for m in f) for f in sem63],
    degrees_M=[max(popcount(m) for m in f) for f in req])
out["controls"]["C2_span_invariant"] = (len(R.indep(sem63))==len(R.indep(req))==len(sem63))
sem42, null42, xR42 = R.cell_systems(4,2)
for key, gs, NN in (("T3_semaev_4_2", sem42, 4), ("T4_null_4_2", null42, 4)):
    ts=time.time(); r = R.exhaustive(gs, NN); r["seconds"]=round(time.time()-ts,1); out["tests"][key]=r
out["xR"] = {"(6,3)": xR63, "(4,2)": xR42}
out["elapsed"] = round(time.time()-t0,1)
json.dump(out, open("/tmp/claude-0/validator/rerun_fast.json","w"), indent=1)
print(json.dumps(out))
