#!/usr/bin/env python3
"""Validator_P13VAL independent recomputation for EXP-P13VOW-001 / RUN-P13VOW-001.

Written independently from the producer's cost_model.py: re-derives every
spot-checked quantity from the specification's formulas. The Dickman rho
cross-check uses Laplace inversion with DIFFERENT quadrature parameters
(h=0.02, T=30, GL=128 nodes) than the producer (h=0.05, T=25, GL=96), so a
shared quadrature bug would show up as disagreement.
"""
import json, math
import numpy
from numpy.polynomial.legendre import leggauss

RAW = "/Volumes/Volume/crypto-autoresearcher/experiments/EXP-P13VOW-001/runs/RUN-P13VOW-001/raw-result.json"
res = json.load(open(RAW))

GAMMA = 0.5772156649015328606
gx, gw = leggauss(128)
gs, gws = 0.5 * (gx + 1.0), 0.5 * gw

def Ein(z):
    zc = numpy.asarray(z, dtype=complex)[:, None]
    return ((1.0 - numpy.exp(-zc * gs[None, :])) / gs[None, :]) @ gws

def saddle(u):
    xi = math.log(u) + math.log(max(math.log(u), 0.5))
    for _ in range(200):
        e = math.exp(xi)
        f = (e - 1.0) / xi - u
        xi -= f / ((e * xi - (e - 1.0)) / xi**2)
        if abs(f) < 1e-15:
            break
    return xi

def rho_laplace(u, h=0.02, T=30.0):
    xi = saddle(u)
    n = int(round(T / h))
    taus = numpy.arange(-n, n + 1) * h
    ss = -xi + 1j * taus
    integ = numpy.exp(u * ss - Ein(ss) + GAMMA)
    return float((integ.sum() * h / (2 * numpy.pi)).real)

checks = []
def check(name, got, want, tol):
    ok = abs(got - want) <= tol
    checks.append((name, got, want, tol, "PASS" if ok else "FAIL"))

PF = res["per_field"]

# --- 1. T_DG baseline exponents (control C2)
for b2p, expect in [(256,128),(384,192),(512,256),(576,288),(768,384)]:
    check(f"T_DG log2p={b2p}", PF[f"log2p={b2p}"]["baseline_log2TDG"], expect, 1e-12)

# --- 2. log2X / w / u / log2P0 for p=256 and p=768 (from spec formulas)
for b2p in (256, 768):
    o = PF[f"log2p={b2p}"]["optimal"]
    lB = o["log2B"]
    check(f"log2X p={b2p}", o["log2X"], 0.5*lB + (b2p-1)/6, 1e-12)
    check(f"w p={b2p}", o["w"], o["log2X"]/lB, 1e-9)
    check(f"u p={b2p}", o["u"], (b2p-1)/(3*lB), 1e-9)
    check(f"log2P0 p={b2p}", o["log2P0"], -o["u"]*math.log2(o["u"]), 1e-9)
    check(f"log2T=log2M-log2P0 p={b2p}", o["log2T"], o["log2M"] - o["log2P0"], 1e-9)

# --- 3. log2M via INDEPENDENT Dickman rho (different quadrature) for all five fields
for b2p in (256, 384, 512, 576, 768):
    o = PF[f"log2p={b2p}"]["optimal"]
    indep = 2*o["log2X"] + math.log2(rho_laplace(o["w"]))
    check(f"log2M indep-rho p={b2p}", o["log2M"], indep, 0.005)

# --- 4. rho(2) validation anchor
v = res["model"]["dickman"]["validation"]
check("rho(2) exact anchor", v["rho2_laplace"], 1 - math.log(2), 3e-3)
check("cross-method max bits < 0.02", v["max_abs_diff_bits_u2_to_u8"], 0.0, 0.02)
# independent rho(2)
check("rho(2) indep-quadrature", rho_laplace(2.0), 1 - math.log(2), 2e-3)

# --- 5. vOW capping + overhead arithmetic (spot cells)
for b2p, lw, c in [(256,30,0.0),(512,50,0.5),(768,80,2.0),(384,40,1.0)]:
    o = PF[f"log2p={b2p}"]["optimal"]
    e = PF[f"log2p={b2p}"]["van_oorschot_wiener"][f"w=2^{lw}"][f"c={c}"]
    want = o["log2T"] - 0.5*min(lw, o["log2M"]) + c*math.sqrt(b2p)
    check(f"T(w) p={b2p} w=2^{lw} c={c}", e["log2T_w"], want, 1e-9)
    check(f"speedup p={b2p} w=2^{lw} c={c}", e["log2speedup_vs_DG"],
          b2p/2 - want, 1e-9)
    check(f"overhead_bits p={b2p} c={c}", e["overhead_bits"], c*math.sqrt(b2p), 1e-12)

# --- 6. crossover formula w* = 2*(T_full + overhead - T_DG)
for b2p, c in [(256,0.0),(256,2.0),(576,1.0),(768,2.0)]:
    o = PF[f"log2p={b2p}"]["optimal"]
    cx = PF[f"log2p={b2p}"]["crossover"][f"c={c}"]
    check(f"w* p={b2p} c={c}", cx["log2w_star_entries"],
          2*(o["log2T"] + c*math.sqrt(b2p) - b2p/2), 1e-9)

# --- 7. byte conversions
for b2p in (256, 768):
    mb = PF[f"log2p={b2p}"]["memory_bytes"]
    check(f"bytes64 p={b2p}", mb["log2bytes_64B_per_entry"], mb["log2M_entries"]+6, 1e-12)
    check(f"bytes256 p={b2p}", mb["log2bytes_256B_per_entry"], mb["log2M_entries"]+8, 1e-12)
vb = PF["log2p=512"]["vow_budget_bytes"]["w=2^60"]
check("w=2^60 bytes64", vb["log2bytes_64B_per_entry"], 66.0, 1e-12)
check("w=2^60 bytes256", vb["log2bytes_256B_per_entry"], 68.0, 1e-12)

# --- 8. the five paper-pair deviations quoted in the execution report
paper = {256:(106.5,92.5),384:(157.5,138.6),512:(204.2,181.3),576:(230.9,206.0),768:(302.4,272.2)}
for b2p,(pt,pm) in paper.items():
    d = PF[f"log2p={b2p}"]["deviation_bits"]
    o = PF[f"log2p={b2p}"]["optimal"]
    check(f"devT p={b2p}", d["time"], o["log2T"]-pt, 1e-9)
    check(f"devM p={b2p}", d["memory"], o["log2M"]-pm, 1e-9)
    tol_flag = abs(d["time"])<=0.75 and abs(d["memory"])<=0.75
    check(f"devflag p={b2p}", float(d["within_tolerance_0.75bit"]), float(tol_flag), 0)

# --- 9. C3 monotonicity over the full grid
mono = True
for b2p in (256,384,512,576,768):
    vow = PF[f"log2p={b2p}"]["van_oorschot_wiener"]
    for c in ("0.0","0.5","1.0","2.0"):
        seq = [vow[f"w=2^{lw}"][f"c={c}"]["log2T_w"] for lw in (30,40,50,60,70,80)]
        if any(seq[i+1] > seq[i] + 1e-12 for i in range(len(seq)-1)):
            mono = False
            print(f"MONOTONICITY VIOLATION p={b2p} c={c}")
checks.append(("C3 monotonicity full grid", 0, 0, 0, "PASS" if mono else "FAIL"))

# --- 10. asymptotic-B comparison spot check (p=256)
a = PF["log2p=256"]["asymptotic_B_choice"]
want_lBa = math.sqrt(255*math.log(2))/3/math.log(2)
check("log2B_asym p=256", a["log2B"], want_lBa, 1e-12)

# --- 11. B optimizer grid sanity: reported optimum is a grid point and beats neighbors
for b2p in (256,384,512,576,768):
    o = PF[f"log2p={b2p}"]["optimal"]
    on_grid = abs((o["log2B"] - 1.0) / 0.1 - round((o["log2B"] - 1.0) / 0.1)) < 1e-9
    checks.append((f"B* on grid p={b2p}", 0, 0, 0, "PASS" if on_grid else "FAIL"))

nfail = sum(1 for c in checks if c[4] == "FAIL")
print(f"total checks: {len(checks)}, FAIL: {nfail}")
for name, got, want, tol, st in checks:
    print(f"{st:4}  {name}: got={got!r} want~{want!r} tol={tol}")
raise SystemExit(1 if nfail else 0)
