"""Red team TASK-20261023-20d7d9: PTM-1 and the generator-dependence of the naive excess (joint R1).

Independent arithmetic (no producer module). For every prime 50 < p < 2000 it enumerates the
EXACT naive-section success set S(p, g) = {d in [2, p-3] : run.py ratio rule returns d}, using
the closed form success <=> q_p(g) != 0 and g^d mod p^2 < p (Wieferich bases, q_p(g) = 0, are
evaluated with an own precision-4 p-adic-log ratio instead), under four generator rules:
  A  smallest primitive root (the frozen run.py choice, sympy.primitive_root);
  B  primitive root uniform at random (PTM-1 object; R_B roots sampled per prime);
  C  smallest primitive root > sqrt(p) (sub-p chain empty: g^2 > p);
  D  rule A, but d restricted to the rest region g^d >= p^2 (sub-p chain and band removed).
Then it simulates the frozen protocol (40 primes sampled without replacement from the 288,
40 d's uniform per prime, run.py's z formula) NREP times per rule and reports the z
distribution. Population quantities have no sampling error in d (exhaustive).
Usage: python3 -B ptm1_generator_controls.py   (repository root; ~1 core, under a minute)
"""
from __future__ import annotations

import json
import math
import random
import statistics

PMIN, PMAX, NPR, NS, K = 50, 2000, 40, 40, 4
R_B = 32
NREP = 4000
SEED = 20261023


def primes_between(a: int, b: int) -> list[int]:
    sieve = bytearray([1]) * b
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(b ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(a + 1, b) if sieve[i]]


def factor_set(n: int) -> list[int]:
    out, q = [], 2
    while q * q <= n:
        if n % q == 0:
            out.append(q)
            while n % q == 0:
                n //= q
        q += 1
    if n > 1:
        out.append(n)
    return out


def is_primroot(g: int, p: int, fs: list[int]) -> bool:
    return all(pow(g, (p - 1) // q, p) != 1 for q in fs)


def vp(n: int, p: int, cap: int) -> int:
    if n == 0:
        return cap
    v = 0
    while n % p == 0 and v < cap:
        n //= p
        v += 1
    return v


def functional(u: int, p: int, k: int = K) -> int:
    M = p ** k
    t = (pow(u, p - 1, M) - 1) % M
    out, tm = 0, 1
    for m in range(1, k + 1):
        tm = tm * t % M
        out = (out + (1 if m % 2 else -1) * tm * pow(m, -1, M)) % M
    return out


def padic_success(p: int, g: int, d: int) -> bool:
    fg, fgd = functional(g, p), functional(pow(g, d, p), p)
    vg, vgd = vp(fg, p, K), vp(fgd, p, K)
    if vg >= K or vgd != vg:
        return False
    return (fgd // p ** vgd) * pow((fg // p ** vg) % p, -1, p) % p == d % p


def success_set(p: int, g: int, region: str = "all") -> tuple[list[int], int]:
    """Exact success set and the size of the d-domain for the region."""
    p2 = p * p
    wieferich = (pow(g, p - 1, p2) == 1)
    lp = math.log(p)
    S, dom = [], 0
    cur = g * g % p2
    for d in range(2, p - 2):
        if region == "rest" and d * math.log(g) < 2 * lp - 1e-12:
            cur = cur * g % p2
            continue
        dom += 1
        ok = padic_success(p, g, d) if wieferich else (cur < p)
        if ok:
            S.append(d)
        cur = cur * g % p2
    return S, dom


def main() -> None:
    rng = random.Random(SEED)
    P = primes_between(PMIN, PMAX)
    table = {}
    wief = []
    pop = {r: {"succ": 0.0, "null": 0.0, "rows": 0} for r in ("A", "B", "C", "D")}
    bins = {"50-500": [0, 0.0, 0, 0.0], "500-1000": [0, 0.0, 0, 0.0], "1000-2000": [0, 0.0, 0, 0.0]}
    rest_sizes = []
    for p in P:
        fs = factor_set(p - 1)
        roots = [g for g in range(2, p) if is_primroot(g, p, fs)]
        gA = roots[0]
        gC = next(g for g in roots if g * g > p)
        gB = rng.sample(roots, min(R_B, len(roots)))
        for g in set([gA, gC] + gB):
            if pow(g, p - 1, p * p) == 1:
                wief.append((p, g))
        SA, domA = success_set(p, gA)
        SC, domC = success_set(p, gC)
        SD, domD = success_set(p, gA, "rest")
        SB = [success_set(p, g) for g in gB]
        L = int(math.floor(math.log(p - 1) / math.log(gA) + 1e-12))
        table[p] = {"gA": gA, "L": L, "A": (len(SA), domA), "C": (len(SC), domC), "D": (len(SD), domD),
                    "B": [(len(s), dom) for s, dom in SB], "gB": gB}
        pop["A"]["succ"] += len(SA) / domA; pop["A"]["null"] += 1 / p
        pop["C"]["succ"] += len(SC) / domC; pop["C"]["null"] += 1 / p
        pop["D"]["succ"] += len(SD) / domD; pop["D"]["null"] += 1 / p
        pop["B"]["succ"] += statistics.fmean(len(s) / dom for s, dom in SB); pop["B"]["null"] += 1 / p
        rest_sizes.append((p, len(SD), domD / p))
        b = "50-500" if p < 500 else ("500-1000" if p < 1000 else "1000-2000")
        bins[b][0] += len(SD); bins[b][1] += domD / p; bins[b][2] += len(SA) - len(SD); bins[b][3] += (domA - domD) / p
    n_pr = len(P)
    pop_summary = {r: {"mean_success_rate_per_pair": pop[r]["succ"] / n_pr, "mean_inv_p": pop[r]["null"] / n_pr,
                       "ratio_to_inv_p": pop[r]["succ"] / pop[r]["null"]} for r in pop}
    # overdispersion of the rest-set size under rule A versus its 1/p expectation
    obs = [s for _, s, _ in rest_sizes]
    lam = [m for _, _, m in rest_sizes]
    chi = sum((o - m) ** 2 / m for o, m in zip(obs, lam)) / len(obs)
    rest_summary = {"sum_rest_successes": sum(obs), "sum_expected_at_inv_p": round(sum(lam), 3),
                    "ratio": sum(obs) / sum(lam), "dispersion_index_(1=Poisson)": round(chi, 3),
                    "max_prime": max(rest_sizes, key=lambda t: t[1] - t[2])[:2],
                    "bins_rest(obs,exp_inv_p)_and_nonrest(obs,exp_inv_p)": {k: [v[0], round(v[1], 3), v[2], round(v[3], 3)] for k, v in bins.items()}}

    # protocol simulation (run.py z formula)
    def z_of(succ: int, invp_sum: float, n: int) -> float:
        ref = invp_sum / n
        return (succ / n - ref) / math.sqrt(ref * (1 - ref) / n)

    sims = {}
    for rule in ("A", "B", "C", "D"):
        zs = []
        for _ in range(NREP):
            ps = rng.sample(P, NPR)
            succ, inv, n = 0, 0.0, 0
            for p in ps:
                t = table[p]
                if rule == "B":
                    j = rng.randrange(len(t["B"]))
                    size, dom = t["B"][j]
                else:
                    size, dom = t[rule]
                q = size / dom
                for _ in range(NS):
                    succ += rng.random() < q
                inv += NS / p
                n += NS
            zs.append(z_of(succ, inv, n))
        zs.sort()
        sims[rule] = {"mean_z": statistics.fmean(zs), "sd_z": statistics.pstdev(zs),
                      "q05": zs[int(0.05 * NREP)], "q50": zs[NREP // 2], "q95": zs[int(0.95 * NREP)],
                      "P_z_gt_4": sum(z > 4 for z in zs) / NREP, "P_z_lt_-4": sum(z < -4 for z in zs) / NREP}
    out = {"primes": n_pr, "R_B_roots_per_prime": R_B, "nrep": NREP, "seed": SEED,
           "wieferich_pairs_found_(p,g)": wief, "population_exact": pop_summary,
           "rule_A_rest_region": rest_summary, "protocol_z_distribution": sims,
           "rule_A_L_histogram": {str(L): sum(1 for t in table.values() if t["L"] == L) for L in sorted({t["L"] for t in table.values()})}}
    json.dump(out, open("experiments/EXP-CZLIFT-bdae69/reports/redteam-20261023/ptm1_generator_controls_output.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
