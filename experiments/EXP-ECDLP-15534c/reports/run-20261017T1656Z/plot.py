"""Draw the recorded uniformity statistics of EXP-ECDLP-15534c (RUN-ECDLP-b927d1).

Values are copied from the run's raw-result.json into data.json; nothing is recomputed
beyond placing recorded points on axes."""
import json, pathlib
import matplotlib; matplotlib.use("svg")
import matplotlib.pyplot as plt
here = pathlib.Path(__file__).parent
d = json.loads((here / "data.json").read_text())
tests = d["tests"]; alpha = d["summary"]["bonferroni_alpha"]
rules = ["L1_integer_hensel", "L2_teichmuller_hensel", "L3_random_hensel"]
arms = ["special", "random"]; col = {"special": "#4a7bb7", "random": "#999999"}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))
for i, rule in enumerate(rules):
    for j, arm in enumerate(arms):
        ps = [max(t["chi_p"], 1e-12) for t in tests if t["rule"] == rule and t["arm"] == arm]
        ks = [t["ks"] for t in tests if t["rule"] == rule and t["arm"] == arm]
        x = i + (-0.17 if arm == "special" else 0.17)
        a1.scatter([x] * len(ps), ps, s=9, color=col[arm], alpha=0.7, label=arm if i == 0 else None)
        a2.scatter([x] * len(ks), ks, s=9, color=col[arm], alpha=0.7, label=arm if i == 0 else None)
a1.set_yscale("log"); a1.axhline(alpha, ls="--", color="k", lw=1, label=f"Bonferroni alpha {alpha:.2e}")
a1.set_xticks(range(3)); a1.set_xticklabels(["L1 integer", "L2 Teichmuller", "L3 random"], fontsize=8)
a1.set_ylabel("recorded chi-square p-value (20 bins, n=400)"); a1.set_title("chi-square p per test (432 tests)", fontsize=9); a1.legend(fontsize=7)
thr = tests[0]["ks_threshold"]
a2.axhline(thr, ls="--", color="k", lw=1, label=f"recorded KS threshold {thr:.4f} (alpha 0.001)")
a2.set_xticks(range(3)); a2.set_xticklabels(["L1 integer", "L2 Teichmuller", "L3 random"], fontsize=8)
a2.set_ylabel("recorded KS distance to uniform on Z/p"); a2.set_title("KS distance per test", fontsize=9); a2.legend(fontsize=7)
fig.suptitle("RUN-ECDLP-b927d1: formal-group defect uniformity, 14-bit primes, d in {2,3}, 6 curves x 2 primes x 3 seeds per arm", fontsize=9)
fig.tight_layout(); fig.savefig(here / "uniformity.svg")
