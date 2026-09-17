"""Exercise the branch itself with a stub closure, since no real instance in this
contract both has degree-5 generators and returns sufficient. This is a test of
the recording logic, not a measurement of anything."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/code")
import run_cert, closure_cert, boolsys

class A: pass
a = A()
a.__dict__.update(dict(wall_cap=60.0, mem_cap=2.0, closure_mem_cap=1.0, threads=1, d_max=6,
                       standard_cap=200000, single_max_cols=200000, closure_max_cols=10**9,
                       single_d3=False, no_closure=False, no_single=True, skip_f4=True,
                       skip_f4_reason="verification", count_reference=False, resume=False))
out = Path(tempfile.mkdtemp()); logf = open(out/"log.txt", "w")

# a system whose generators are degree 5, so the degree-4 block is empty
sysd5 = {"family": "stub_degree5", "N": 6, "var_names": [f"v{i}" for i in range(6)],
         "equations": [[0b011111, 0]], "n": None, "m": None, "t": None, "k": None}

def stub(N, eqs, D, mem_cap, s_known=None, standard_cap=100000, **kw):
    """Pretend the closure decides at D = 5 -- above 4."""
    return {"D": D, "instrument": "closure", "status": "completed",
            "verdict": "sufficient" if D >= 5 else "insufficient",
            "verdict_basis": "stub", "rank": 1, "ncols": 10, "standard_monomials": 2,
            "iterations": [], "contains_one": False, "wall_s": 0.0}

real = closure_cert.closure_certificate
closure_cert.closure_certificate = stub
try:
    recs, _ = run_cert.measure(sysd5, "verify_stub_d5", out, a, logf)
finally:
    closure_cert.closure_certificate = real
cl = [r for r in recs if r["instrument"] == "closure_certificate"][0]
print("max generator degree:", cl["max_generator_degree"], "(degree-4 block is empty)")
print("closure_D (deciding degree):", cl["closure_D"])
print("degree4_sufficiency_verdict:", repr(cl["degree4_sufficiency_verdict"]))
print("degree4_verdict_source:", repr(cl["degree4_verdict_source"]))
ok = cl["degree4_sufficiency_verdict"] != "sufficient"
print("PASS -- a degree-5 decision is NOT recorded as degree-4 sufficiency" if ok else "FAIL")
