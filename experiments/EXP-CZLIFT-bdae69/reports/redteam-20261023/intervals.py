"""Red team TASK-20261023-20d7d9: exact Poisson 95% intervals and Clopper-Pearson bounds quoted in the report.
Inputs are the counts printed by r2_nulls.py, ptm1_generator_controls.py and r1_elliptic_analogue.py."""
import math, json


def pcdf(k, lam):
    return sum(math.exp(-lam) * lam ** j / math.factorial(j) for j in range(k + 1))


def pois_ci(k, a=0.05):
    def solve(f, lo, hi):
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else solve(lambda m: (1 - pcdf(k - 1, m)) < a / 2 and 1 or -1, 0, 10 * k + 10)
    hi = solve(lambda m: pcdf(k, m) > a / 2 and 1 or -1, 0, 10 * k + 20)
    return lo, hi


def r(x):
    return round(x, 3)


out = {}
lam_h = 2.052 + 3.334
out["hensel_success_pooled"] = {"obs": 3, "exp_inv_p": lam_h, "ratio": r(3 / lam_h), "ratio_95ci": [r(x / lam_h) for x in pois_ci(3)]}
lam_rest = 2.004 + 3.110
lam_rest_exact = 2.479 + 4.106
out["naive_rest_pooled_vs_inv_p"] = {"obs": 9, "exp": lam_rest, "ratio": r(9 / lam_rest), "ratio_95ci": [r(x / lam_rest) for x in pois_ci(9)]}
out["naive_rest_pooled_vs_exact_conditional"] = {"obs": 9, "exp": lam_rest_exact, "ratio": r(9 / lam_rest_exact), "ratio_95ci": [r(x / lam_rest_exact) for x in pois_ci(9)]}
out["naive_total_pooled_vs_inv_p"] = {"obs": 33, "exp": lam_h, "ratio": r(33 / lam_h), "ratio_95ci": [r(x / lam_h) for x in pois_ci(33)]}
out["naive_total_pooled_vs_exact_conditional"] = {"obs": 33, "exp": 11.549 + 17.643, "ratio": r(33 / (11.549 + 17.643)), "ratio_95ci": [r(x / (11.549 + 17.643)) for x in pois_ci(33)]}
out["clopper_pearson_lower_k_eq_n"] = {"teich_3200": r(0.025 ** (1 / 3200) * 1e5) / 1e5, "subp_24": r(0.025 ** (1 / 24)), "e37a1_balanced_Dint_1420": r(0.025 ** (1 / 1420) * 1e4) / 1e4, "e37a1_naive_Dint_pos_1136": r(0.025 ** (1 / 1136) * 1e4) / 1e4, "j0_balanced_d2_287": r(0.025 ** (1 / 287) * 1e4) / 1e4}
e = 1420 * 23.881 / 11333
out["e37a1_hensel_at_Dint"] = {"obs": 2, "exp_inv_p": r(e), "ratio_95ci": [r(x / e) for x in pois_ci(2)]}
for name, k, lam in (("e37a1_rest_naive", 21, 21.725), ("e37a1_rest_balanced", 22, 21.725), ("e37a1_rest_hensel", 25, 21.725),
                     ("j0_rest_naive", 25, 24.086), ("j0_rest_balanced", 22, 24.086), ("j0_rest_hensel", 16, 24.086)):
    out[name] = {"obs": k, "exp_inv_p": lam, "ratio": r(k / lam), "ratio_95ci": [r(x / lam) for x in pois_ci(k)]}
out["P_z_gt_4_on_both_seeds"] = {"rule_A_smallest_root": r(0.9375 ** 2), "rule_B_random_root": 0.00575 ** 2}
json.dump(out, open("experiments/EXP-CZLIFT-bdae69/reports/redteam-20261023/intervals_output.json", "w"), indent=1)
print(json.dumps(out, indent=1))
