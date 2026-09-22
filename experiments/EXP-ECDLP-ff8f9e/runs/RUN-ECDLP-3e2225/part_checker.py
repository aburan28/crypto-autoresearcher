#!/usr/bin/env python3
"""RUN-ECDLP-3e2225 checker: independent spot re-derivations for the
partition profile (EXP-ECDLP-ff8f9e v1)."""

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

_drv = importlib.util.spec_from_file_location("pdrv", os.path.join(HERE, "part_driver.py"))
pd = importlib.util.module_from_spec(_drv)
_drv.loader.exec_module(pd)

REG = json.load(open(os.path.join(HERE, "part_registry.json")))
FITS = json.load(open(os.path.join(HERE, "part_fits.json")))
LADDER = FITS["ladder"]
results = {"checks": [], "all_passed": None}


def check(name, passed, detail):
    results["checks"].append({"check": name, "passed": bool(passed), "detail": detail})
    print(("PASS" if passed else "FAIL"), name, "--", detail)


def naive_norm(p, L, M, t_choice=None):
    x = np.arange(p)
    W = np.exp(-2j * np.pi * np.outer(x, x) / p)
    om = np.exp(2j * np.pi / M)
    best, best_t = 0.0, None
    ts = range(1, M) if t_choice is None else [t_choice]
    for t in ts:
        acc = np.zeros(p, dtype=np.complex128)
        for c in range(M):
            mask = (L == c)
            n = int(mask.sum())
            if n == 0:
                continue
            v = np.zeros(p)
            v[mask] = 1.0 / n
            acc += (om ** (t * c)) * (W @ v)
        l1 = float(np.abs(acc[1:]).sum())
        if l1 > best:
            best, best_t = l1, t
    return best, best_t


p_small = min(LADDER)
L, _ = pd.partition_levels("POP4", p_small)
n_norm, n_t = naive_norm(p_small, L, 4)
rec = REG[f"POP4:{p_small}"]
rel = abs(rec["l1_nontrivial"] - n_norm) / n_norm
check(f"naive_dft_POP4_{p_small}", rel <= 1e-9 and rec["argmax_t"] == n_t,
      f"rel diff {rel:.2e}, argmax t {rec['argmax_t']} vs {n_t}")

L2, _ = pd.partition_levels("RES4", p_small)
n_norm2, n_t2 = naive_norm(p_small, L2, 4)
rec2 = REG[f"RES4:{p_small}"]
rel2 = abs(rec2["l1_nontrivial"] - n_norm2) / n_norm2
check(f"naive_dft_RES4_{p_small}", rel2 <= 1e-9, f"rel diff {rel2:.2e}")


def chirpz2_norm(p, L, M, t_choice):
    inv2 = (p + 1) // 2
    Lfft = 1
    while Lfft < 3 * p:
        Lfft *= 2
    chirp = np.array([np.exp(-2j * np.pi * (((j * j) % p) * inv2 % p) / p)
                      for j in range(p)])
    b = np.conj(chirp)
    B = np.zeros(Lfft, dtype=np.complex128)
    for j in range(p):
        B[j] = b[j]
        if j > 0:
            B[Lfft - j] = b[p - j]
    FB = np.fft.fft(B)
    del B
    om = np.exp(2j * np.pi / M)
    acc = np.zeros(p, dtype=np.complex128)
    for c in range(M):
        mask = (L == c)
        n = int(mask.sum())
        if n == 0:
            continue
        v = np.zeros(p)
        v[mask] = 1.0 / n
        A = np.zeros(Lfft, dtype=np.complex128)
        A[:p] = v.astype(np.complex128) * chirp
        C = np.fft.ifft(np.fft.fft(A) * FB)
        acc += (om ** (t_choice * c)) * (C[:p] * chirp)
    return float(np.abs(acc[1:]).sum())


p_mid = min(q for q in LADDER if q > 2 ** 16)
L3, _ = pd.partition_levels("RES16", p_mid)
rec3 = REG[f"RES16:{p_mid}"]
c_norm = chirpz2_norm(p_mid, L3, 16, rec3["argmax_t"])
rel3 = abs(rec3["l1_nontrivial"] - c_norm) / c_norm
check(f"second_chirpz_RES16_{p_mid}_at_argmax_t", rel3 <= 1e-9,
      f"rel diff {rel3:.2e} at t={rec3['argmax_t']}")

ok = {c: r for c, r in REG.items() if r.get("status") == "ok"}
v0ok = all(r.get("vhat0_all_levels_ok", True) for r in ok.values()
           if "vhat0_all_levels_ok" in r)
check("vhat0_all_levels_all_ok_partition_cells", v0ok,
      f"{sum(1 for r in ok.values() if 'vhat0_all_levels_ok' in r)} partition cells")

fcp = FITS["fits"]["C02P16"]
same = True
for row in ["POP2", "POP4", "POP16", "POP64", "RES4", "RES16"]:
    f = FITS["fits"][row]
    v = FITS["verdicts"].get(row)
    if not f or v not in ("stable_above_random", "stable_flat", "unstable",
                         "stable_below_random", "unresolved_battery_not_measured"):
        continue
    delta = f["lambda"] - fcp["lambda"]
    se_d = math.sqrt((f["se"] or 1) ** 2 + (fcp["se"] or 1) ** 2)
    mrow = row + "M"
    fm = FITS["fits"].get(mrow)
    moeb = (abs(fm["lambda"] - f["lambda"]) > 2 * math.sqrt(
        (f["se"] or 1) ** 2 + (fm["se"] or 1) ** 2)) if fm else None
    mine = ("unstable" if moeb else
            "unresolved_battery_not_measured" if moeb is None else
            "stable_above_random" if delta > 2 * se_d else
            "stable_flat" if abs(delta) <= 2 * se_d else
            "stable_below_random")
    if mine != v:
        same = False
        check(f"independent_verdict_{row}", False,
              f"independent {mine} vs reported {v}")
if same:
    check("independent_verdict_recompute_all_rows", True,
          "all reported partition verdicts reproduce from the thresholds "
          "and battery flags")

results["all_passed"] = all(c["passed"] for c in results["checks"])
with open(os.path.join(HERE, "part_checker-report.json"), "w") as f:
    json.dump(results, f, indent=1)
print("ALL PASSED" if results["all_passed"] else "CHECKER FAILURES PRESENT")
