"""Red team TASK-20261023-20d7d9, joint R2: the homomorphism-rate null and the success-test null.

Independent arithmetic only (no producer module is imported). Reads the two archived
raw-result.json files by key. Re-derives:
  (a) the naive and Hensel homomorphism-rate nulls, with the exact x, y domain run.py uses
      (x = g^e, e in [1, p-2], so x ranges over F_p^* minus {1});
  (b) a replay of the (x, y) draws (shares only run.py's RNG call order) to confirm that
      naive hom == (x*y < p) row by row;
  (c) the exact naive success criterion success <=> q_p(g) != 0 and g^d mod p^2 < p, checked
      against the recorded success bit and against an own precision-4 p-adic-log ratio;
  (d) a three-way split of every naive row: sub-p (g^d < p), band (p <= g^d < p^2), rest;
  (e) the exact conditional expectation of each class given the drawn primes and generators
      (d uniform in [2, p-3]) and the exact Poisson-binomial tail of the observed rest count.
Usage: python3 -B r2_nulls.py  (from the repository root)
"""
from __future__ import annotations

import json
import math
import random

RUNS = {
    20261009: "experiments/EXP-CZLIFT-bdae69/runs/RUN-CZLIFT-0cefcd/raw-result.json",
    20261010: "experiments/EXP-CZLIFT-bdae69/runs/RUN-CZLIFT-a5c1da/raw-result.json",
}
K = 4


def vp(n: int, p: int, cap: int) -> int:
    if n == 0:
        return cap
    v = 0
    while n % p == 0 and v < cap:
        n //= p
        v += 1
    return v


def plog_1unit(u: int, p: int, k: int) -> int:
    """log_p(u) mod p^k for u == 1 mod p (p > k + 2 so no m in the sum is divisible by p)."""
    M = p ** k
    t = (u - 1) % M
    assert t % p == 0
    out, tm = 0, 1
    for m in range(1, k + 1):
        tm = tm * t % M
        out = (out + (1 if m % 2 else -1) * tm * pow(m, -1, M)) % M
    return out


def functional(u: int, p: int, k: int = K) -> int:
    M = p ** k
    return plog_1unit(pow(u, p - 1, M), p, k)


def padic_ratio_success(p: int, g: int, d: int) -> bool:
    """The run.py ratio rule (first nonzero digit), re-implemented, on the naive section."""
    fg, fgd = functional(g, p), functional(pow(g, d, p), p)
    vg, vgd = vp(fg, p, K), vp(fgd, p, K)
    if vg >= K or vgd < vg:
        return False
    if vgd > vg:
        return False  # ratio 0, never equal to d in [2, p-3]
    ratio = (fgd // p ** vgd) * pow((fg // p ** vg) % p, -1, p) % p
    return ratio == d % p


def fermat_q(a: int, p: int) -> int:
    return ((pow(a, p - 1, p * p) - 1) // p) % p


def exact_success(p: int, g: int, d: int) -> bool:
    return fermat_q(g, p) != 0 and pow(g, d, p * p) < p


def klass(p: int, g: int, d: int) -> str:
    lg = d * math.log(g)
    if lg < math.log(p) - 1e-12:
        return "subp"
    if lg < 2 * math.log(p) - 1e-12:
        return "band"
    return "rest"


def success_sets(p: int, g: int) -> dict:
    """Exact success counts per class over all d in [2, p-3]."""
    out = {"subp": [0, 0], "band": [0, 0], "rest": [0, 0]}  # [size of class, successes]
    for d in range(2, p - 2):
        c = klass(p, g, d)
        out[c][0] += 1
        out[c][1] += exact_success(p, g, d)
    return out


def poisson_binomial_tail(probs_counts: list[tuple[float, int]], obs: int) -> float:
    """P(S >= obs) for S = sum of Binomial(n_i, q_i), exact convolution."""
    dist = [1.0]
    for q, n in probs_counts:
        for _ in range(n):
            new = [0.0] * (len(dist) + 1)
            for s, pr in enumerate(dist):
                new[s] += pr * (1 - q)
                new[s + 1] += pr * q
            dist = new
    return sum(dist[obs:])


def hom_null(p: int) -> tuple[float, float]:
    """P(x*y < p) for x, y independent uniform on F_p^* minus {1} (run.py), and on all of F_p^*."""
    n_excl = sum(max(0, (p - 1) // x - 1) for x in range(2, p))  # y in [2, (p-1)//x]
    n_all = sum((p - 1) // x for x in range(1, p))
    return n_excl / (p - 2) ** 2, n_all / (p - 1) ** 2


def replay_xy(seed: int, p: int, g: int, samples: int):
    """Reproduce only the (d, x, y) draws of run.py measure_prime (RNG call order)."""
    rng = random.Random(seed * 65_537 + p)
    M = p ** K
    out = []
    for _ in range(samples):
        d = rng.randrange(2, p - 2)
        x = pow(g, rng.randrange(1, p - 1), p)
        y = pow(g, rng.randrange(1, p - 1), p)
        out.append((d, x, y))
        for _ in range(5):  # hensel draws s_g, s_gd, s_x, s_y, s_xy (teichmuller, naive draw nothing)
            rng.randrange(M // p)
    return out


def main() -> None:
    report = {}
    for seed, path in RUNS.items():
        raw = json.load(open(path))
        primes = raw["raw"]["primes"]
        rec_metrics = raw["metrics"]["sections"]
        hom_exp_excl = hom_exp_all = hom_exp_invp = hens_hom_exp = 0.0
        replay_hom_mismatch = replay_d_mismatch = 0
        hens_hom_obs = naive_hom_obs = 0
        succ_mismatch_exact = succ_mismatch_padic = 0
        cls_obs = {"subp": [0, 0], "band": [0, 0], "rest": [0, 0]}  # [rows, successes]
        cls_lambda_invp = {"subp": 0.0, "band": 0.0, "rest": 0.0}
        cond_exp = {"subp": 0.0, "band": 0.0, "rest": 0.0}
        rest_pb = []
        per_prime = []
        for pr in primes:
            p, g, rows = pr["p"], pr["generator"], pr["rows"]
            n = len(rows)
            he, ha = hom_null(p)
            hom_exp_excl += n * he
            hom_exp_all += n * ha
            hom_exp_invp += n / p
            hens_hom_exp += n / p ** 3
            rep = replay_xy(seed, p, g, n)
            for r, (d, x, y) in zip(rows, rep):
                replay_d_mismatch += r["d"] != d
                replay_hom_mismatch += r["sections"]["naive"]["hom"] != (x * y < p)
            naive_hom_obs += sum(r["sections"]["naive"]["hom"] for r in rows)
            hens_hom_obs += sum(r["sections"]["hensel"]["hom"] for r in rows)
            S = success_sets(p, g)
            ndom = p - 4
            for c in S:
                cond_exp[c] += n * S[c][1] / ndom
            rest_pb.append((S["rest"][1] / ndom, n))
            ps = {"p": p, "g": g, "L": int(math.floor(math.log(p - 1) / math.log(g) + 1e-12)),
                  "subp_set_size": S["subp"][0], "band_set_size": S["band"][0], "band_successes": S["band"][1],
                  "rest_set_size": S["rest"][0], "rest_successes_exact": S["rest"][1],
                  "rest_expected_at_inv_p": round(S["rest"][0] / p, 4), "obs": {"subp": 0, "band": 0, "rest": 0}}
            for r in rows:
                d = r["d"]
                rec = r["sections"]["naive"]["success"]
                ex = exact_success(p, g, d)
                pa = padic_ratio_success(p, g, d)
                succ_mismatch_exact += rec != ex
                succ_mismatch_padic += rec != pa
                c = klass(p, g, d)
                cls_obs[c][0] += 1
                cls_obs[c][1] += rec
                cls_lambda_invp[c] += 1 / p
                ps["obs"][c] += rec
            per_prime.append(ps)
        rest_obs = cls_obs["rest"][1]
        rest_tail_exact = poisson_binomial_tail(rest_pb, rest_obs)
        lam_invp_rest = cls_lambda_invp["rest"]
        lam_invp_rest_plus_band = cls_lambda_invp["rest"] + cls_lambda_invp["band"]

        def ptail(lam, k):
            return 1 - sum(math.exp(-lam) * lam ** j / math.factorial(j) for j in range(k))

        report[str(seed)] = {
            "recorded": {"naive_hom_rate": rec_metrics["naive"]["homomorphism_rate"],
                         "hensel_hom_rate": rec_metrics["hensel"]["homomorphism_rate"],
                         "naive_success_rate": rec_metrics["naive"]["success_rate"],
                         "reference_inv_p": rec_metrics["naive"]["reference_inv_p"]},
            "replay": {"d_mismatch": replay_d_mismatch, "naive_hom_vs_xy_lt_p_mismatch": replay_hom_mismatch},
            "hom_null": {
                "naive_observed": naive_hom_obs,
                "naive_expected_exact_domain_Fp_minus_1": round(hom_exp_excl, 3),
                "naive_expected_domain_all_Fp_star": round(hom_exp_all, 3),
                "naive_expected_at_inv_p_as_stated": round(hom_exp_invp, 3),
                "naive_P_ge_obs_under_inv_p": ptail(hom_exp_invp, naive_hom_obs),
                "hensel_observed": hens_hom_obs,
                "hensel_expected_exact_inv_p_cubed": hens_hom_exp,
                "hensel_P_eq_0_under_inv_p": math.exp(-hom_exp_invp),
            },
            "success_bit_checks": {"recorded_vs_exact_criterion_mismatch": succ_mismatch_exact,
                                   "recorded_vs_own_padic_ratio_mismatch": succ_mismatch_padic, "rows": 40 * len(primes)},
            "naive_split": {c: {"rows": cls_obs[c][0], "successes": cls_obs[c][1],
                                "expected_at_inv_p": round(cls_lambda_invp[c], 3),
                                "expected_exact_conditional_on_primes": round(cond_exp[c], 3)} for c in cls_obs},
            "rest_residual": {
                "observed": rest_obs,
                "lambda_inv_p_rest_only": round(lam_invp_rest, 3),
                "P_ge_obs_rest_only": ptail(lam_invp_rest, rest_obs),
                "lambda_inv_p_rest_plus_band(validator_model)": round(lam_invp_rest_plus_band, 3),
                "P_ge_obs_rest_plus_band": ptail(lam_invp_rest_plus_band, rest_obs),
                "exact_conditional_expectation": round(cond_exp["rest"], 3),
                "exact_conditional_P_ge_obs": rest_tail_exact,
            },
            "total_exact_conditional_expectation": round(sum(cond_exp.values()), 3),
            "primes_with_rest_successes": [
                {k: ps[k] for k in ("p", "g", "L", "rest_set_size", "rest_successes_exact", "rest_expected_at_inv_p", "obs")}
                for ps in per_prime if ps["obs"]["rest"] or ps["rest_successes_exact"] >= 3],
            "band_successes_any_prime": sum(ps["band_successes"] for ps in per_prime),
        }
    out = "experiments/EXP-CZLIFT-bdae69/reports/redteam-20261023/r2_nulls_output.json"
    json.dump(report, open(out, "w"), indent=1)
    for s, rep in report.items():
        print("seed", s)
        for k in ("replay", "hom_null", "success_bit_checks", "naive_split", "rest_residual"):
            print(" ", k, json.dumps(rep[k]))
        print("  total_exact_conditional_expectation", rep["total_exact_conditional_expectation"],
              "band_successes_any_prime", rep["band_successes_any_prime"])


if __name__ == "__main__":
    main()
