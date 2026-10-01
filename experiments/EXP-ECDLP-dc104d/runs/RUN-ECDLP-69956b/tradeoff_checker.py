#!/usr/bin/env python3
"""RUN-ECDLP-69956b checker: independent spot re-derivations, including
the O4 identity (the inversion-image transform as the character sum over
the inverted set) and the R08I equality case."""

import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL_DIR = os.path.abspath(os.path.join(
    HERE, "..", "..", "..", "EXP-ECDLP-fac9ea", "runs", "TASK-20260921-4888d4"))
sys.path.insert(0, IMPL_DIR)

_spec = importlib.util.spec_from_file_location("impl", os.path.join(IMPL_DIR, "implementation.py"))
impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(impl)

_drv = importlib.util.spec_from_file_location("tdrv", os.path.join(HERE, "tradeoff_driver.py"))
td = importlib.util.module_from_spec(_drv)
_drv.loader.exec_module(td)

REG = json.load(open(os.path.join(HERE, "tradeoff_registry.json")))
FITS = json.load(open(os.path.join(HERE, "tradeoff_fits.json")))
LADDER = FITS["ladder"]
results = {"checks": [], "all_passed": None}


def check(name, passed, detail):
    results["checks"].append({"check": name, "passed": bool(passed), "detail": detail})
    print(("PASS" if passed else "FAIL"), name, "--", detail)


p_small = min(LADDER)
inv = impl.inv_table(p_small)
x = np.arange(p_small)
W = np.exp(-2j * np.pi * np.outer(x, x) / p_small)

v, _ = td.build_row("IVQI", p_small, inv)
Vn = W @ v
rec = REG[f"IVQI:{p_small}"]
rel = abs(rec["l1_nontrivial"] - float(np.abs(Vn[1:]).sum())) / float(np.abs(Vn[1:]).sum())
check(f"naive_dft_IVQI_{p_small}", rel <= 1e-9, f"rel diff {rel:.2e}")

A_mask = np.zeros(p_small, dtype=bool)
qr = impl.power_set_mask(p_small, 2)
L = p_small // 8
A_mask[:L] = qr[:L]
A = np.nonzero(A_mask)[0]
K = x[1:16]
# CORRECTED (checker-side bug, disclosed): the O4 identity's direct side
# is the character sum over the INVERSES of A's elements,
# (1/|A|) sum_{a in A} eta^{k * a^{-1}}; the first draft omitted the
# inversion (eta^{a*k}), which of course disagrees -- the driver's
# computation and the naive DFT already agreed at 2.4e-14, so the
# identity itself was never in doubt; only this verification was wrong.
what_direct = np.array([sum(np.exp(-2j * np.pi * (int(inv[a]) * int(k) % p_small) / p_small)
                            for a in A) for k in K]) / len(A)
v_ivq, _ = td.build_row("IVQ", p_small, inv)
w = v_ivq[inv]
what_via_inv = np.array([sum(w[int(xx)] * np.exp(-2j * np.pi * int(xx) * int(k) / p_small)
                            for xx in range(p_small)) for k in K])
o4 = float(np.max(np.abs(what_direct - what_via_inv)))
check("O4_identity_character_sum_vs_transformed_indicator", o4 <= 1e-9,
      f"max coefficient difference {o4:.2e} (the inversion-image transform "
      f"equals the character sum over the inverted set)")

eq = FITS["equality_worst_rel_diff"]
check("R08I_equals_R08_equality_case", eq <= 1e-12,
      f"worst relative difference {eq:.2e}")

ok = {c: r for c, r in REG.items() if r.get("status") == "ok"}
v0ok = all(r.get("vhat0_minus_1_abs", 1.0) <= 1e-9 for r in ok.values())
check("vhat0_equals_1_all_ok_cells", v0ok, f"{len(ok)} cells")


def chirpz2_l1star(v, p):
    Lf = 1
    while Lf < 3 * p:
        Lf *= 2
    inv2 = (p + 1) // 2
    chirp = np.array([np.exp(-2j * np.pi * (((j * j) % p) * inv2 % p) / p)
                      for j in range(p)])
    A = np.zeros(Lf, dtype=np.complex128)
    A[:p] = v.astype(np.complex128) * chirp
    b = np.conj(chirp)
    B = np.zeros(Lf, dtype=np.complex128)
    for j in range(p):
        B[j] = b[j]
        if j > 0:
            B[Lf - j] = b[p - j]
    C = np.fft.ifft(np.fft.fft(A) * np.fft.fft(B))
    V = C[:p] * chirp
    return float(np.abs(V[1:]).sum())


p_mid = min(q for q in LADDER if q > 2 ** 16)
inv_mid = impl.inv_table(p_mid)
v, _ = td.build_row("R01I", p_mid, inv_mid)
l1c = chirpz2_l1star(v, p_mid)
rec2 = REG[f"R01I:{p_mid}"]
rel2 = abs(rec2["l1_nontrivial"] - l1c) / l1c
check(f"second_chirpz_R01I_{p_mid}", rel2 <= 1e-9, f"rel diff {rel2:.2e}")

f_r01, f_r01i = FITS["fits"]["R01"], FITS["fits"]["R01I"]
f_ivq, f_ivqi = FITS["fits"]["IVQ"], FITS["fits"]["IVQI"]
r01i_flat = abs(f_r01i["lambda"] - 0.5) <= 2 * (f_r01i["se"] or 1) + 0.02
ivq_structured = abs(f_ivq["lambda"] - 0.5) > 2 * (f_ivq["se"] or 1)
d_ivq = f_ivq["lambda"] - f_ivqi["lambda"]
s_ivq = math.sqrt((f_ivq["se"] or 1) ** 2 + (f_ivqi["se"] or 1) ** 2)
ivqi_flat = abs(f_ivqi["lambda"] - 0.5) <= 2 * (f_ivqi["se"] or 1) + 0.02
mine_ivq = ("COUNTEREXAMPLE_TO_MECHANISM" if ivq_structured and abs(d_ivq) <= 2 * s_ivq and not ivqi_flat
            else "inversion_collapse_confirmed" if ivq_structured and ivqi_flat
            else "no_structure_to_collapse")
check("independent_IVQ_verdict", mine_ivq == FITS["verdicts"]["IVQ"],
      f"independent {mine_ivq} vs reported {FITS['verdicts']['IVQ']}")

r01_structured = abs(f_r01["lambda"] - 0.5) > 2 * (f_r01["se"] or 1)
mine_r01 = ("inversion_collapse_confirmed" if r01_structured and r01i_flat
            else "not_confirmed")
check("independent_R01_verdict", mine_r01 == FITS["verdicts"]["R01_inversion_collapse"],
      f"independent {mine_r01} vs reported {FITS['verdicts']['R01_inversion_collapse']} "
      f"(R01I lambda {f_r01i['lambda']:.4f} at flat: {r01i_flat})")

results["all_passed"] = all(c["passed"] for c in results["checks"])
with open(os.path.join(HERE, "tradeoff_checker-report.json"), "w") as f:
    json.dump(results, f, indent=1)
print("ALL PASSED" if results["all_passed"] else "CHECKER FAILURES PRESENT")
