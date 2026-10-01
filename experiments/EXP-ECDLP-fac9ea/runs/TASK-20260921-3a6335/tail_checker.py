#!/usr/bin/env python3
"""RUN-ECDLP-0c5f65 checker: independent spot re-derivations for the
complex64 tail re-measure (amendment DEC-20260921-e7edc5)."""

import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL_DIR = os.path.abspath(os.path.join(HERE, "..", "TASK-20260921-4888d4"))
sys.path.insert(0, IMPL_DIR)

_spec = importlib.util.spec_from_file_location("impl", os.path.join(IMPL_DIR, "implementation.py"))
impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(impl)

_drv_spec = importlib.util.spec_from_file_location("taildrv", os.path.join(HERE, "tail_driver.py"))
taildrv = importlib.util.module_from_spec(_drv_spec)
_drv_spec.loader.exec_module(taildrv)

REG = json.load(open(os.path.join(HERE, "tail_registry.json")))
FITS = json.load(open(os.path.join(HERE, "tail_fits.json")))
results = {"checks": [], "all_passed": None}


def check(name, passed, detail):
    results["checks"].append({"check": name, "passed": bool(passed), "detail": detail})
    print(("PASS" if passed else "FAIL"), name, "--", detail)


def naive_l1star(v, p):
    x = np.arange(p)
    W = np.exp(-2j * np.pi * np.outer(x, x) / p)
    V = W @ v
    return float(np.abs(V[1:]).sum()), float(abs(V[0]))


p_small = 4111
v, _ = impl.build_row("R03", p_small)
l1n, v0n = naive_l1star(v, p_small)
cz64s = taildrv.ChirpZ64(p_small, os.path.join(HERE, "work"))
out64, _ = cz64s.transform(v)
rel = abs(out64[0] - l1n) / l1n
check(f"naive_dft_vs_complex64_R03_{p_small}", rel <= 1e-4,
      f"rel L1* diff {rel:.2e} (complex64 vs complex128 naive DFT)")


def chirpz2_64(v, p):
    L = 1
    while L < 3 * p:
        L *= 2
    inv2 = (p + 1) // 2
    chirp = np.array([np.exp(-2j * np.pi * (((j * j) % p) * inv2 % p) / p)
                      for j in range(p)], dtype=np.complex64)
    A = np.zeros(L, dtype=np.complex64)
    A[:p] = v.astype(np.complex64) * chirp
    b = np.conj(chirp)
    B = np.zeros(L, dtype=np.complex64)
    for j in range(p):
        B[j] = b[j]
        if j > 0:
            B[L - j] = b[p - j]
    C = np.fft.ifft(np.fft.fft(A) * np.fft.fft(B))
    V = C[:p] * chirp
    return float(np.abs(V[1:]).astype(np.float64).sum())


p_mid = 114161
v, _ = impl.build_row("R08", p_mid)
l1c = chirpz2_64(v, p_mid)
cz64m = taildrv.ChirpZ64(p_mid, os.path.join(HERE, "work"))
outm, _ = cz64m.transform(v)
rel2 = abs(outm[0] - l1c) / l1c
check(f"second_chirpz_complex64_R08_{p_mid}", rel2 <= 1e-4,
      f"rel L1* diff {rel2:.2e}")

ok = {c: r for c, r in REG.items() if r.get("status") == "ok" and c != "XCHECK:R03:4818013"}
v0ok = all(r.get("vhat0_minus_1_rel", 1.0) <= 1e-4 for r in ok.values())
check("vhat0_within_1e-4_all_ok_cells", v0ok, f"{len(ok)} cells")

xc = REG["XCHECK:R03:4818013"]
check("dual_precision_crosscheck", xc["relative_difference"] <= 1e-4,
      f"rel diff {xc['relative_difference']:.2e}")

bres = FITS.get("breach_vs_incap_comparison", {})
real = {c: d for c, d in bres.items() if d["breach_measurement_preserved"] > 1e-3}
worst = max((d["relative_difference"] for d in real.values()), default=0.0)
check("breach_values_consistent_within_precision", worst <= 1e-3,
      f"worst per-cell breach-vs-in-cap relative difference over signal rows {worst:.2e} "
      f"(complex64 precision bound plus FFT roundoff; the breach "
      f"measurements were not corrupted, only out of cap)")

results["all_passed"] = all(c["passed"] for c in results["checks"])
with open(os.path.join(HERE, "tail_checker-report.json"), "w") as f:
    json.dump(results, f, indent=1)
print("ALL PASSED" if results["all_passed"] else "CHECKER FAILURES PRESENT")
