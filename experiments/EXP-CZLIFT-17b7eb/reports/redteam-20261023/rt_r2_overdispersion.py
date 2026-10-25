"""R2: per-lift exact rate of a deterministic section vs the random-function collision model.
Success pairs = #{k != +-m : w(k) = w(m)}, w = u/k; for random w this is ~ (p-1) with sd ~ sqrt(11 (p-1))."""
import json, math, statistics
d = json.load(open('rt_r2_exact_output.json'))['exact_rates']
z = []
for k, v in d.items():
    D, p, sec = k.split('|'); p = int(p)
    if p < 100:
        continue
    r = v['canonical']['rate_all_mean'] * (p - 3)
    z.append((r - 1) / math.sqrt(11 / (p - 1)))
out = {"canonical_lifts_p>=100_both_deterministic_sections": len(z),
       "standardized_deviation_mean": round(statistics.mean(z), 3),
       "standardized_deviation_sd": round(statistics.pstdev(z), 3),
       "max_abs": round(max(abs(x) for x in z), 3),
       "model": "per-lift rate*(p-3) - 1 scaled by sqrt(11/(p-1)) (Poisson(1) collision count of w = u/k); sd ~ 1 means the model fits"}
print(json.dumps(out, indent=1))
json.dump(out, open("rt_r2_overdispersion_output.json", "w"), indent=1)
