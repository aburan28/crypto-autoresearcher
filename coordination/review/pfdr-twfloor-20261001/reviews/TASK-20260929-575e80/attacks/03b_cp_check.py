"""03b -- check of the exact compound-Poisson tail used by NULL-P (MC-2 follow-up).

On the instance with the largest |z| in 03's 200-seed cross-check, (main,22,c4,m4,small_x,on):
(a) brute-force Poisson mixture of convolution powers, (b) the FFT of numlib.cp_pmf, (c) an
independent 2,000,000-draw Monte Carlo (seed 12345). Writes out/03b_cp_check.json.
"""
import importlib.util, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump
from numlib import cp_pmf
spec = importlib.util.spec_from_file_location("n3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "03_f6_nulls.py"))
n3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(n3)
laws = n3.jump_laws()
xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
x = [x for x in xs if x["bits"] == 22 and x["curve"] == 4 and x["m"] == 4 and x["arm"] == "small_x" and x["mode"] == "on"][0]
u = 4 * x["S"] ** 2 / x["N"]; need = u / 0.81 - x["relations"]; k = int(math.floor(need))
def cp_brute(lam, pmf, nmax):
    out = np.zeros(nmax); cur = np.zeros(nmax); cur[0] = 1.0; pk = math.exp(-lam); out += pk * cur
    for kk in range(1, 400):
        cur = np.convolve(cur, pmf)[:nmax]; pk *= lam / kk; out += pk * cur
        if pk < 1e-18 and kk > lam: break
    return out
tot = np.zeros(6000); tot[0] = 1
for c in ("TT", "TB", "SS"):
    if x["mu_" + c] > 0:
        L = laws[(4, c)]; tot = np.convolve(tot, cp_brute(x["mu_" + c] / L["EJ"], L["pmf"], 6000))[:6000]
lam = sum(x["mu_" + c] / laws[(4, c)]["EJ"] for c in ("TT", "TB", "SS") if x["mu_" + c] > 0)
mix = np.zeros(max(len(laws[(4, c)]["pmf"]) for c in ("TT", "TB", "SS")))
for c in ("TT", "TB", "SS"):
    if x["mu_" + c] > 0:
        p = laws[(4, c)]["pmf"]; mix[:len(p)] += (x["mu_" + c] / laws[(4, c)]["EJ"] / lam) * p
f = cp_pmf(lam, mix)
rng = np.random.default_rng(12345); n = 2_000_000; chunk = 100_000; hits = 0
for _ in range(n // chunk):  # chunked so the sampler stays far below the 1.5e9-byte stop (RF-5)
    tm = np.zeros(chunk)
    for c in ("TT", "TB", "SS"):
        if x["mu_" + c] > 0:
            L = laws[(4, c)]; K = rng.poisson(x["mu_" + c] / L["EJ"], chunk)
            tm += np.bincount(np.repeat(np.arange(chunk), K), weights=rng.choice(len(L["pmf"]), size=int(K.sum()), p=L["pmf"]), minlength=chunk)
    hits += int(np.sum(tm > need))
pm = hits / n
dump("03b_cp_check.json", {"instance": ["main", 22, 4, 4, "small_x", "on"], "brute_force_tail": float(tot[k + 1:].sum()),
     "fft_tail": float(f[k + 1:].sum()), "mc_2e6_tail": pm, "mc_se": math.sqrt(pm * (1 - pm) / n),
     "z_mc_vs_exact": (pm - float(f[k + 1:].sum())) / math.sqrt(pm * (1 - pm) / n),
     "note": "03's 200-seed cross-check reused seeds 0..199 for every instance, so its 21 z-values are correlated; this independent run is the calibration."})
print(open(os.path.join(OUT, "03b_cp_check.json")).read())
