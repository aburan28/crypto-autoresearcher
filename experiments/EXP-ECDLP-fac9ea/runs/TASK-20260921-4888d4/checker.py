#!/usr/bin/env python3
"""EXP-ECDLP-fac9ea v2/v3 checker: independent re-derivations for
RUN-ECDLP-8e13c2 (TASK-20260921-4888d4).

1. Naive O(p^2) DFT spot check at the smallest ladder prime for two rows.
2. A second, independently structured chirp-z (different padding-length
   policy and placement arithmetic) at a mid ladder prime for one row.
3. Blind re-derivation of the gate algebra from the two cited records'
   own claim text (IDEA-20260904-f68c7f (D)/(E), IDEA-20260920-b6ad24
   (A1)-(A3)), never reading implementation.py's fit or verdict code, and
   an independent verdict recompute for every registry row.
4. Independent recomputation of the control outcomes from registry.json.
"""

import importlib.util
import json
import math
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REG = json.load(open(os.path.join(HERE, "registry.json")))
FITS = json.load(open(os.path.join(HERE, "fits.json")))

spec = importlib.util.spec_from_file_location("impl", os.path.join(HERE, "implementation.py"))
impl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(impl)

results = {"checks": [], "all_passed": None}


def check(name, passed, detail):
    results["checks"].append({"check": name, "passed": bool(passed), "detail": detail})
    print(("PASS" if passed else "FAIL"), name, "--", detail)


def naive_dft_l1star(v, p):
    x = np.arange(p)
    W = np.exp(-2j * np.pi * np.outer(x, x) / p)
    V = W @ v
    return float(np.abs(V[1:]).sum()), float(abs(V[0]))


def chirpz2_l1star(v, p):
    """Second independent chirp-z: length = next power of two >= 3p, chirp
    built by an explicit per-index loop over the exponent-space form
    e_j = (j^2 mod p) * inv2 mod p (the p-periodic form the Bluestein
    identity requires for odd p), placement by explicit per-index loop."""
    L = 1
    while L < 3 * p:
        L *= 2
    inv2 = (p + 1) // 2
    chirp = np.array([np.exp(-2j * np.pi * (((j * j) % p) * inv2 % p) / p)
                      for j in range(p)])
    a = v.astype(np.complex128) * chirp
    A = np.zeros(L, dtype=np.complex128)
    A[:p] = a
    b = np.conj(chirp)
    B = np.zeros(L, dtype=np.complex128)
    for j in range(p):
        B[j] = b[j]
        if j > 0:
            B[L - j] = b[p - j]
    F = np.fft.fft(A) * np.fft.fft(B)
    C = np.fft.ifft(F)
    V = C[:p] * chirp
    return float(np.abs(V[1:]).sum()), float(abs(V[0]))


primes = sorted(FITS["ladders"]["primary"] + FITS["ladders"]["secondary"])
p_small = min(primes)
p_mid = min(q for q in primes if q > 2 ** 16)

for row in ["R01", "R03"]:
    v, _ = impl.build_row(row, p_small)
    l1_naive, v0_naive = naive_dft_l1star(v, p_small)
    rec = REG[f"{row}:{p_small}"]
    rel = abs(rec["l1_nontrivial"] - l1_naive) / l1_naive
    v0d = abs(rec["abs_vhat0"] - v0_naive) / v0_naive
    check(f"naive_dft_{row}_{p_small}", rel <= 1e-9 and v0d <= 1e-9,
          f"rel L1* diff {rel:.2e}, vhat0 diff {v0d:.2e}")

row_mid = "R08"
v, _ = impl.build_row(row_mid, p_mid)
l1_2, v0_2 = chirpz2_l1star(v, p_mid)
rec = REG[f"{row_mid}:{p_mid}"]
rel2 = abs(rec["l1_nontrivial"] - l1_2) / l1_2
check(f"second_chirpz_{row_mid}_{p_mid}", rel2 <= 1e-9,
      f"rel L1* diff {rel2:.2e} (impl {rec['l1_nontrivial']:.6f} vs indep {l1_2:.6f})")

f68 = open(os.path.join(HERE, "../../../../ledger/proposals/IDEA-20260904-f68c7f.yaml")).read()
b62 = open(os.path.join(HERE, "../../../../ledger/proposals/IDEA-20260920-b6ad24.yaml")).read()
has_14 = re.search(r"n\^\{1/4", f68) is not None
has_eps_bound = re.search(r"\|\|vhat\|\|_1.{0,12}n\^\{-1/2", f68) is not None
has_16 = re.search(r"lambda >= 1/6", b62) is not None
has_floor = re.search(r"n\^\{\(4-2\*lambda\)/11\}", b62) is not None
check("gate_algebra_thresholds_present_in_cited_records",
      has_14 and has_eps_bound and has_16 and has_floor,
      f"1/4 in f68c7f: {has_14}; eps bound: {has_eps_bound}; "
      f"1/6 in b6ad24: {has_16}; floor form: {has_floor}")


def independent_verdict(lam, moebius_delta):
    if moebius_delta is True:
        return "artifactual"
    if lam is None:
        return "unresolved"
    if lam > 0.25:
        return "corner_open_and_learning_open"
    if lam >= 1 / 6:
        return "corner_open_learning_blocked"
    return "floor_blocked"


verdict_ok = True
detail = []
for row in impl.GATE_ROWS:
    fam = FITS["families"].get(row, {})
    fit = fam.get("fit")
    if not fit:
        continue
    mine = independent_verdict(fit["lambda"], fam.get("moebius_delta_beyond_2se"))
    theirs = fam.get("verdict")
    if mine != theirs:
        verdict_ok = False
        detail.append(f"{row}: independent {mine} vs reported {theirs}")
check("independent_verdict_recompute_all_rows", verdict_ok,
      "; ".join(detail) if detail else "all reported verdicts reproduce from the "
      "thresholds 1/4 and 1/6 plus the moebius flag, re-derived independently")

ok_cells = {cid: r for cid, r in REG.items() if r.get("status") == "ok"}
v0ok = all(r.get("vhat0_minus_1_abs", 1.0) <= 1e-9 for r in ok_cells.values())
c01ok = all(r["l1_nontrivial"] <= 1e-9 * max(r["abs_vhat0"], 1e-30)
            for cid, r in ok_cells.items() if cid.startswith("C01:"))
check("vhat0_equals_1_all_ok_cells", v0ok,
      f"{sum(1 for r in ok_cells.values() if r.get('vhat0_minus_1_abs', 1) <= 1e-9)}"
      f"/{len(ok_cells)} cells within 1e-9")
check("C01_numerically_zero", c01ok, "all C01 cells at numerical zero")

fa = FITS["families"]["C02A"]["fit"]
fb = FITS["families"]["C02B"]["fit"]
c02_band = abs(fa["lambda"] - 0.5) <= 2 * (fa["se"] or 1) + 0.02
seed_agree = abs(fa["lambda"] - fb["lambda"]) <= 2 * math.sqrt(
    (fa["se"] or 1) ** 2 + (fb["se"] or 1) ** 2)
check("C02_parseval_band_and_seed_agreement", c02_band and seed_agree,
      f"C02A lambda {fa['lambda']:.4f} (band {c02_band}), seed agreement {seed_agree}")

r03 = FITS["families"]["R03"]["fit"]
r03_pass = 0.36 <= r03["lambda"] <= 0.42
check("R03_reproduction_band", r03_pass,
      f"R03 fitted lambda {r03['lambda']:.4f} (point-estimate semantics per the "
      f"frozen text) in [0.36, 0.42]: {r03_pass}; SE {r03['se']:.4f}, "
      f"+-2SE [{r03['lambda']-2*r03['se']:.4f}, {r03['lambda']+2*r03['se']:.4f}] "
      f"-- reproduction is marginal at the band edge")

r03b = FITS["families"]["R03B"]["fit"]
same = (r03b["lambda"] == r03["lambda"] and
        sorted(r03b["primes"]) == sorted(r03["primes"]))
check("R03B_deterministic_replication", same,
      f"R03B lambda {r03b['lambda']:.4f} identical to R03: {same}")

results["all_passed"] = all(c["passed"] for c in results["checks"])
with open(os.path.join(HERE, "checker-report.json"), "w") as f:
    json.dump(results, f, indent=1)
print("ALL PASSED" if results["all_passed"] else "CHECKER FAILURES PRESENT")
