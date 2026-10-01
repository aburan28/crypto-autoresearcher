#!/usr/bin/env python3
"""RUN-ECDLP-4dfb36 checker: independent spot re-derivations for the
cross-ratio family profile (EXP-ECDLP-4ce0a2 v1)."""

import importlib.util
import json
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

_drv = importlib.util.spec_from_file_location("crdrv", os.path.join(HERE, "cr_driver.py"))
cr = importlib.util.module_from_spec(_drv)
_drv.loader.exec_module(cr)

REG = json.load(open(os.path.join(HERE, "cr_registry.json")))
FITS = json.load(open(os.path.join(HERE, "cr_fits.json")))
LADDER = FITS["ladder"]
results = {"checks": [], "all_passed": None}


def check(name, passed, detail):
    results["checks"].append({"check": name, "passed": bool(passed), "detail": detail})
    print(("PASS" if passed else "FAIL"), name, "--", detail)


def naive_l1star(v, p):
    x = np.arange(p)
    W = np.exp(-2j * np.pi * np.outer(x, x) / p)
    V = W @ v
    return float(np.abs(V[1:]).sum()), float(abs(V[0]))


def chirpz2_l1star(v, p):
    L = 1
    while L < 3 * p:
        L *= 2
    inv2 = (p + 1) // 2
    chirp = np.array([np.exp(-2j * np.pi * (((j * j) % p) * inv2 % p) / p)
                      for j in range(p)])
    A = np.zeros(L, dtype=np.complex128)
    A[:p] = v.astype(np.complex128) * chirp
    b = np.conj(chirp)
    B = np.zeros(L, dtype=np.complex128)
    for j in range(p):
        B[j] = b[j]
        if j > 0:
            B[L - j] = b[p - j]
    C = np.fft.ifft(np.fft.fft(A) * np.fft.fft(B))
    V = C[:p] * chirp
    return float(np.abs(V[1:]).sum())


p_small = min(LADDER)
ctx = {"qr": impl.power_set_mask(p_small, 2), "inv": impl.inv_table(p_small)}
v, _ = cr.build_row("CR", p_small, ctx)
l1n, v0n = naive_l1star(v, p_small)
rec = REG[f"CR:{p_small}"]
rel = abs(rec["l1_nontrivial"] - l1n) / l1n
check(f"naive_dft_CR_{p_small}",
      rel <= 1e-9 and abs(rec["abs_vhat0"] - v0n) / v0n <= 1e-9,
      f"rel L1* diff {rel:.2e}")

p_mid = min(q for q in LADDER if q > 2 ** 16)
ctx2 = {"qr": impl.power_set_mask(p_mid, 2), "inv": impl.inv_table(p_mid)}
v, _ = cr.build_row("CR", p_mid, ctx2)
l1c = chirpz2_l1star(v, p_mid)
rec2 = REG[f"CR:{p_mid}"]
rel2 = abs(rec2["l1_nontrivial"] - l1c) / l1c
check(f"second_chirpz_CR_{p_mid}", rel2 <= 1e-9, f"rel L1* diff {rel2:.2e}")

v2, _ = cr.build_row("R08", p_small, ctx)
l1n2, _ = naive_l1star(v2, p_small)
rec3 = REG[f"R08:{p_small}"]
rel3 = abs(rec3["l1_nontrivial"] - l1n2) / l1n2
check(f"naive_dft_R08_{p_small}", rel3 <= 1e-9, f"rel L1* diff {rel3:.2e}")

ok = {c: r for c, r in REG.items() if r.get("status") == "ok"}
v0ok = all(r.get("vhat0_minus_1_abs", 1.0) <= 1e-9 for r in ok.values())
check("vhat0_equals_1_all_ok_cells", v0ok, f"{len(ok)} cells")

anchor_ok = True
detail = []
for row in cr.SWEEP:
    for p in LADDER:
        r = REG.get(f"{row}:{p}", {})
        if r.get("status") == "ok" and "anchors" not in (r.get("note") or ""):
            anchor_ok = False
            detail.append(f"{row}:{p} missing anchor record")
check("all_sweep_cells_record_their_anchor_triples", anchor_ok,
      "; ".join(detail) if detail else "all sweep cells carry their anchors")

spread_ok = FITS["spread_within_2se"]
mine = ("family_level_varying" if not spread_ok else
        "stable_above_random" if (FITS["delta_vs_C02A"] is not None and
                                  FITS["delta_vs_C02A"] > 0 and
                                  FITS["delta_vs_R08"] > 0) else "stable_flat")
if FITS["verdict"] == "void_control_failure" or FITS["verdict"] == "unresolved":
    same = True
else:
    same = mine == FITS["verdict"]
check("independent_verdict_recompute", same,
      f"independent {mine} vs reported {FITS['verdict']} "
      f"(spread {FITS['anchor_spread']}, deltas {FITS['delta_vs_C02A']}/"
      f"{FITS['delta_vs_R08']})")

results["all_passed"] = all(c["passed"] for c in results["checks"])
with open(os.path.join(HERE, "cr_checker-report.json"), "w") as f:
    json.dump(results, f, indent=1)
print("ALL PASSED" if results["all_passed"] else "CHECKER FAILURES PRESENT")
