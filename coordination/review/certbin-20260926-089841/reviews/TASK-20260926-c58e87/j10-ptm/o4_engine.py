"""O4 engine runs (TASK-20260926-c58e87). Runs the PINNED engine UNCHANGED on every kept O4
system and on the 20 S_3 descents over V' (after o4-declaration.yaml was written and hashed):
  Closure(18, 4, 17).macaulay_closure(eqs, want_cert=True)
  Closure(18, 4, 17).w_closure(eqs, want_cert=True)
Every returned certificate is checked with own code (rtlib.flat_cert_ok: sum mu*f_k == 1).
Environment set by the caller: CRYPTO_AR_GF2_BACKEND=native, CRYPTO_AR_GF2_CACHE=<scratch>,
CRYPTO_AR_GF2_THREADS=1, PYTHONDONTWRITEBYTECODE=1.
Usage: python3 o4_engine.py <worktree> <j10-ptm dir>
"""
import json
import os
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rtlib as R  # noqa: E402

wt, d = sys.argv[1], sys.argv[2]
sys.path.insert(0, f"{wt}/src")
from crypto_autoresearcher.gf2 import closure, kernels  # noqa: E402  (object under test)

t0 = time.time()
C = closure.Closure(18, 4, 17)
S = json.load(open(f"{d}/o4-systems.json"))
items = [(k["key"], k["role"], k["s"], k["E_hex"]) for k in S["kept"] if "EXHAUSTED" not in k]
items += [(f"S3-VR:{dd['slot']}", "unsat" if dd["s"] == 0 else "sat", dd["s"], dd["E_hex"]) for dd in S["descents"]]
recs = []
certchecks = []
for key, role, s, eh in items:
    E = R.hex_to_E(eh)
    eqs = R.E_eqs_masks(E)
    ta = time.time()
    m4, c4 = C.macaulay_closure(eqs, want_cert=True)
    tb = time.time()
    w4, cw = C.w_closure(eqs, want_cert=True)
    tc = time.time()
    dbd = m4["dims_by_deg"]
    rec = {"key": key, "role": role, "s": s,
           "M4": {"rank": int(m4["rank"]), "one": bool(m4["one"]), "dims_by_deg": [int(x) for x in dbd],
                  "P": int(m4["rank"]) - int(dbd[3]), "fallen": int(dbd[3]),
                  "linear_forms": int(dbd[1]) - int(dbd[0]), "seconds": round(tb - ta, 3)},
           "W4": {k: (v if not hasattr(v, "tolist") else v.tolist()) for k, v in w4.items()},
           "W4_seconds": round(tc - tb, 3),
           "codim_W4": 4048 - int(w4["final_dim"])}
    for name, cert in (("M4", c4), ("W4", cw)):
        if cert is not None:
            ok, maxmu = R.flat_cert_ok(cert, E)
            certchecks.append({"key": key, "closure": name, "format": "flat (engine)", "pairs": len(cert),
                               "max_mu": maxmu, "own_sum_check": ok,
                               "counts_as": ("M_4 / W_4 (max|mu| <= 2)" if maxmu is not None and maxmu <= 2
                                             else "unsatisfiability and 1 in M_{2+max|mu|} only")})
            rec[name + "_cert"] = {"pairs": len(cert), "max_mu": maxmu, "own_sum_check": ok}
        else:
            rec[name + "_cert"] = None
    recs.append(rec)
    print(key, role, s, rec["M4"]["rank"], rec["M4"]["one"], rec["M4"]["dims_by_deg"],
          "W4", w4["one"], w4["one_first_iteration"], w4["final_dim"], w4["dims"], flush=True)
from crypto_autoresearcher.gf2 import _native  # noqa: E402
env = {k: os.environ.get(k) for k in ("CRYPTO_AR_GF2_BACKEND", "CRYPTO_AR_GF2_CACHE", "CRYPTO_AR_GF2_THREADS",
                                      "PYTHONDONTWRITEBYTECODE")}
out = {"engine_backend": kernels.backend(), "build_info": dict(_native.build_info), "env": env,
       "seconds": round(time.time() - t0, 1), "records": recs}
json.dump(out, open(f"{d}/o4-engine-records.json", "w"), indent=1)
json.dump(certchecks, open(f"{d}/o4-certificate-checks.json", "w"), indent=1)
print("backend", kernels.backend(), _native.build_info.get("source_sha256"), "seconds", out["seconds"])
