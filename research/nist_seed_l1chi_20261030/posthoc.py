"""Post-hoc, descriptive (NOT preregistered) checks on runs/results.json:
null percentile of prime239v1's tail terms (5003 < l <= 10^6 = the decisive scope;
1000 < l <= 10^6), implied class number from the fundamental discriminant recorded by
research/nist_seed_genus_rank_20261023, and the minimum-of-69 null tail."""
import json, math
from analyze import primes_upto, kron, term, null_probs
r = json.load(open("runs/results.json")); t = next(x for x in r["rows"] if x["name"] == "prime239v1")
p, D = int(t["p"]), int(t["D"]); P = primes_upto(10**6); out = {}
for lo in (5003, 1000):
    o = sum(term(kron(D, l), l) for l in P if l > lo); mu = var = 0.0
    for l in P:
        if l > lo:
            pp, pm, _ = null_probs(p, l); a, b = term(1, l), term(-1, l); m = pp * a + pm * b; mu += m; var += pp * a * a + pm * b * b - m * m
    z = (o - mu) / math.sqrt(var)
    out[f"tail_gt_{lo}"] = dict(observed=o, null_mean=mu, null_sd=math.sqrt(var), z=z, pct=50 * (1 + math.erf(z / math.sqrt(2))))
g = json.load(open("../nist_seed_genus_rank_20261023/analysis.json"))
row = next(x for x in g["rows"] if "prime239v1" in json.dumps(x)[:400])
DK = int(row["fundamental_discriminant"]); L = math.exp(t["logP_DK"])
out["class_number"] = dict(D_K_bits=abs(DK).bit_length(), conductor_squared=D // DK, L_est=L,
                           log2_h_est=math.log2(math.sqrt(abs(DK)) * L / math.pi), log2_h_at_L1=math.log2(math.sqrt(abs(DK)) / math.pi))
out["min_of_69_tail"] = 1 - (1 - t["pct_delta"] / 100) ** 69
json.dump(out, open("runs/posthoc.json", "w"), indent=1); print(json.dumps(out, indent=1))
