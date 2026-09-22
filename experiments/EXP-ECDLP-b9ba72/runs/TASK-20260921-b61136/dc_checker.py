#!/usr/bin/env python3
"""RUN-ECDLP-ee15df checker: independent spot re-derivations for the
digit-character profile (EXP-ECDLP-b9ba72 v1)."""

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

_drv = importlib.util.spec_from_file_location("dcdrv", os.path.join(HERE, "dc_driver.py"))
dc = importlib.util.module_from_spec(_drv)
_drv.loader.exec_module(dc)

REG = json.load(open(os.path.join(HERE, "dc_registry.json")))
FITS = json.load(open(os.path.join(HERE, "dc_fits.json")))
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
v, _ = dc.build_row("VT", p_small)
l1n, v0n = naive_l1star(v, p_small)
rec = REG[f"VT:{p_small}"]
rel = abs(rec["l1_nontrivial"] - l1n) / l1n
check(f"naive_dft_VT_{p_small}",
      rel <= 1e-9 and abs(rec["abs_vhat0"] - v0n) / v0n <= 1e-9,
      f"rel L1* diff {rel:.2e}")

v, _ = dc.build_row("VR", p_small)
l1n2, _ = naive_l1star(v, p_small)
rec2 = REG[f"VR:{p_small}"]
rel2 = abs(rec2["l1_nontrivial"] - l1n2) / l1n2
check(f"naive_dft_VR_{p_small}", rel2 <= 1e-9, f"rel L1* diff {rel2:.2e}")

p_mid = min(q for q in LADDER if q > 2 ** 16)
v, _ = dc.build_row("VT", p_mid)
l1c = chirpz2_l1star(v, p_mid)
rec3 = REG[f"VT:{p_mid}"]
rel3 = abs(rec3["l1_nontrivial"] - l1c) / l1c
check(f"second_chirpz_VT_{p_mid}", rel3 <= 1e-9, f"rel L1* diff {rel3:.2e}")

ident = REG["IDENTITY:VT:4099"]
check("identity_l1_levelset_equals_character_norm_over_2A",
      ident["relative_difference"] <= 1e-9,
      f"rel diff {ident['relative_difference']:.2e} "
      f"(corrected identity: l1*(VT) = ||that||_1^*/(2|A_t|))")

ok = {c: r for c, r in REG.items()
      if r.get("status") == "ok" and not c.startswith("IDENTITY")}
v0ok = all(r.get("vhat0_minus_1_abs", 1.0) <= 1e-9 for r in ok.values())
check("vhat0_equals_1_all_ok_cells", v0ok, f"{len(ok)} cells")

for ch, base, mrow in (("Thue-Morse", "VT", "VTM"), ("Rudin-Shapiro", "VR", "VRM")):
    f, fm = FITS["fits"][base], FITS["fits"][mrow]
    fa = FITS["fits"]["C02A"]
    moeb = abs(fm["lambda"] - f["lambda"]) > 2 * math.sqrt(
        (f["se"] or 1) ** 2 + (fm["se"] or 1) ** 2)
    delta = f["lambda"] - fa["lambda"]
    se_d = math.sqrt((f["se"] or 1) ** 2 + (fa["se"] or 1) ** 2)
    mine = ("unstable" if moeb else
            "stable_above_random" if delta > 2 * se_d else
            "stable_flat" if abs(delta) <= 2 * se_d else "unresolved")
    check(f"independent_verdict_{base}", mine == FITS["verdicts"][ch],
          f"independent {mine} vs reported {FITS['verdicts'][ch]} "
          f"(delta {delta:.4f} +- {se_d:.4f})")

results["all_passed"] = all(c["passed"] for c in results["checks"])
with open(os.path.join(HERE, "dc_checker-report.json"), "w") as f:
    json.dump(results, f, indent=1)
print("ALL PASSED" if results["all_passed"] else "CHECKER FAILURES PRESENT")
