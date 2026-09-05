"""R2: what the sweep could have shown, and the two controls it did not run.

(a) ONE INTEGER instance (A, B, x_R) reduced modulo a ladder of primes -- the
    experiment the specialization claim actually describes.  The sweep instead
    redraws (A, B, x_R) in F_p at each prime, so no instance exists at two primes.
(b) the one invariant in the table that is NOT forced: the support-matched
    null's top_rank at D = 5 (a genuine 6 x 6 determinant in the 9 top
    coefficients).  Its drop locus is exhibited at small primes.
(c) bookkeeping checks on the raw records used by R2/R4.
"""
import json, os, random, sys
from itertools import combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_digit import N, stilde_values, poly_from_values, profile, echelon_ranks

REPO = "/home/user/crypto-autoresearcher"
out = {}
P64 = (1 << 64) - 59
P256 = 2**256 - 2**224 + 2**192 + 2**96 - 1


def primes_upto(n):
    s = [True] * (n + 1); s[0] = s[1] = False
    for i in range(2, int(n ** .5) + 1):
        if s[i]:
            for j in range(i * i, n + 1, i): s[j] = False
    return [i for i in range(n + 1) if s[i]]


# ---- (a) one integer instance down a prime ladder --------------------------
A0, B0, XR0 = 941, 428, 3690          # the frozen fixture instance, as integers
ladder = {}
for p in primes_upto(200) + [4099, P64, P256]:
    v = stilde_values(A0, B0, XR0, p)
    pr = profile(poly_from_values(v, p), p)
    ladder[str(p)] = {"zeros": sum(1 for t in v if t % p == 0),
                      "full_top": [list(x[:2]) for x in pr]}
out["one_integer_instance_across_primes"] = ladder
out["one_integer_instance_first_prime_at_reference"] = next(
    (q for q in sorted(int(k) for k in ladder)
     if ladder[str(q)]["full_top"] == [[0, 0], [1, 1], [6, 2], [15, 1]]), None)
out["one_integer_instance_deviating_primes"] = [
    q for q in sorted(int(k) for k in ladder)
    if ladder[str(q)]["full_top"] != [[0, 0], [1, 1], [6, 2], [15, 1]]]

# ---- (b) the support-matched null's top rank at D = 5 ----------------------
support = set(poly_from_values(stilde_values(A0, B0, XR0, P64), P64))
top_support = sorted(m for m in support if bin(m).count("1") == 4)


def null_top_rank_D5(p, rng):
    poly = {m: rng.randrange(1, p) for m in support}
    top4 = {m: c for m, c in poly.items() if bin(m).count("1") == 4}
    tgt = {m: k for k, m in enumerate(sum(1 << i for i in c) for c in combinations(range(N), 5))}
    rows = []
    for i in range(N):
        mu = 1 << i
        row = {}
        for m, c in top4.items():
            if m & mu: continue
            row[tgt[m | mu]] = (row.get(tgt[m | mu], 0) + c) % p
        rows.append({k: v for k, v in row.items() if v})
    return echelon_ranks(rows, p, 10 ** 9)[0]


nulls = {}
for p in (5, 7, 11, 13, 101, 4099):
    rng = random.Random(999 + p)
    ranks = [null_top_rank_D5(p, rng) for _ in range(2000)]
    nulls[str(p)] = {"draws": 2000, "rank_histogram": {str(k): ranks.count(k) for k in sorted(set(ranks))},
                     "drop_rate_below_6": round(sum(1 for r in ranks if r < 6) / len(ranks), 5)}
out["null_top_rank_D5_drop_rate"] = nulls
out["null_support_top_monomials"] = len(top_support)

# ---- (c) raw-record bookkeeping -------------------------------------------
book = {}
for run, tag in (("RUN-PFDR-fd901a-sweep-p4099", "p4099"), ("RUN-PFDR-fd901a-sweep-p64", "p64"),
                 ("RUN-PFDR-fd901a-sweep-p256", "p256")):
    with open(os.path.join(REPO, "experiments/EXP-PFDR-fd901a/runs", run, "raw-result.json")) as fh:
        raw = json.load(fh)["raw"]
    curves = {c["seed"]: (c["a"], c["b"]) for c in raw["curves"]}
    terms = {}
    seeds = {}
    for d in raw["draws"]:
        if d["arm"] == "semaev":
            terms[str(d["generator_term_counts"])] = terms.get(str(d["generator_term_counts"]), 0) + 1
        if d["arm"] == "null_support":
            seeds[d["rng_seed_mixed"]] = seeds.get(d["rng_seed_mixed"], 0) + 1
    book[tag] = {"curve_1101": curves.get(1101), "semaev_term_counts": terms,
                 "null_draws": sum(seeds.values()), "distinct_null_mixed_seeds": len(seeds),
                 "null_seed_collisions": sum(1 for v in seeds.values() if v > 1)}
out["bookkeeping"] = book

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out",
                       "r2_forced_profile.json"), "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
print(json.dumps({k: v for k, v in out.items() if k != "one_integer_instance_across_primes"},
                 indent=1, sort_keys=True))
print("LADDER (p: zeros, profile):")
for k in sorted(out["one_integer_instance_across_primes"], key=lambda x: int(x)):
    e = out["one_integer_instance_across_primes"][k]
    print(f"  p={k}: zeros={e['zeros']} profile={e['full_top']}")
