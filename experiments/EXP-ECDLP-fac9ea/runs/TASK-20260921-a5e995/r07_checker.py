#!/usr/bin/env python3
"""RUN-ECDLP-ccf8f0 checker: independent spot re-derivations for the R07
extension (amendment DEC-20260921-a796fe)."""

import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL_DIR = os.path.abspath(os.path.join(HERE, "..", "TASK-20260921-4888d4"))
sys.path.insert(0, IMPL_DIR)

_spec = importlib.util.spec_from_file_location("impl", os.path.join(IMPL_DIR, "implementation.py"))
impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(impl)

REG = json.load(open(os.path.join(HERE, "r07_registry.json")))
FITS = json.load(open(os.path.join(HERE, "r07_fits.json")))
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
    return float(np.abs(V[1:]).sum()), float(abs(V[0]))


p_small = min(LADDER)
v, _ = impl.build_row("R07", p_small)
l1n, v0n = naive_l1star(v, p_small)
rec = REG[f"R07:{p_small}"]
rel = abs(rec["l1_nontrivial"] - l1n) / l1n
check(f"naive_dft_R07_{p_small}", rel <= 1e-9 and abs(rec["abs_vhat0"] - v0n) / v0n <= 1e-9,
      f"rel L1* diff {rel:.2e}")

p_mid = min(q for q in LADDER if q > 2 ** 16)
v, _ = impl.build_row("R07", p_mid)
l1c, _ = chirpz2_l1star(v, p_mid)
rec = REG[f"R07:{p_mid}"]
rel2 = abs(rec["l1_nontrivial"] - l1c) / l1c
check(f"second_chirpz_R07_{p_mid}", rel2 <= 1e-9, f"rel L1* diff {rel2:.2e}")

ok = {c: r for c, r in REG.items() if r.get("status") == "ok"}
v0ok = all(r.get("vhat0_minus_1_abs", 1.0) <= 1e-9 for r in ok.values())
check("vhat0_equals_1_all_ok_cells", v0ok, f"{len(ok)} cells")

f_r07 = FITS["fits"]["R07"]
f_c02 = FITS["fits"]["C02A"]
d = f_r07["lambda"] - f_c02["lambda"]
s = math.sqrt((f_r07["se"] or 1) ** 2 + (f_c02["se"] or 1) ** 2)
independent_verdict = ("resolved_above_random" if d > 2 * s
                       else "at_random_level" if abs(d) <= 2 * s
                       else "unresolved_below_random")
same = independent_verdict == FITS["verdict"] or FITS["verdict"] in (
    "void_control_failure", "unresolved_artifactual_or_missing_moebius",
    "unresolved_insufficient_points")
check("independent_delta_verdict_recompute", same,
      f"independent delta verdict {independent_verdict} vs reported {FITS['verdict']} "
      f"(delta {d:.4f} +- {s:.4f})")

results["all_passed"] = all(c["passed"] for c in results["checks"])
with open(os.path.join(HERE, "r07_checker-report.json"), "w") as f:
    json.dump(results, f, indent=1)
print("ALL PASSED" if results["all_passed"] else "CHECKER FAILURES PRESENT")
