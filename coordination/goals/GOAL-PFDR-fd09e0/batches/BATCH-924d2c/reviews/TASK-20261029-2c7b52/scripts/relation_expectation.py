# Descriptive check (not part of the reading): expected number of curves per r >= 2 cell whose
# base points satisfy a nonzero relation v.P = O with v in the difference box [-2T, 2T]^r, under the
# statement's model of independent uniform P_i on a prime-order group of order N (P[v.P = O] = 1/N),
# against the observed number of records with duplicate_skips > 0 or infinity_skips > 0.
# Also: Monte Carlo of the duplicate count produced by ONE uniform random relation v in the box
# (pairs c, c' of the half-box H with c - c' = +-v or c + c' = +-v, any multiple of v ignored).
import json, sys, os, itertools, random, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
recs = [json.loads(l) for l in open(os.path.join(ROOT, "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl"))]
by = {}
for r in recs:
    by.setdefault(r["cell"], []).append(r)
rows = []
tot_e = tot_o = 0.0
for cell, rs in sorted(by.items()):
    r = rs[0]["r"]
    if r == 1:
        continue
    T = rs[0]["gap_meta"]["T"]
    nvec = ((4 * T + 1) ** r - 1) / 2
    exp = sum(nvec / x["N"] for x in rs)
    obs = sum(1 for x in rs if x["gap_meta"]["duplicate_skips"] or x["gap_meta"]["infinity_skips"])
    tot_e += exp
    tot_o += obs
    rows.append({"cell": cell, "T": T, "expected_curves_with_relation": round(exp, 4), "observed_records_with_skips": obs})
# duplicate count distribution for one random relation in the r=3, T=10 box
rng = random.Random(20261029)
T = 10
H = [v for v in itertools.product(range(-T, T + 1), repeat=3) if next((x for x in v if x), 0) > 0]
Hs = set(H)
def dups(v):
    cnt = 0
    for c in H:
        for w in (v, tuple(-x for x in v)):
            d = tuple(ci + wi for ci, wi in zip(c, w))
            if d in Hs:
                cnt += 1
            s = tuple(-ci + wi for ci, wi in zip(c, w))  # c + c' = w  ->  c' = w - c
            if s in Hs and s != c:
                cnt += 1
    return cnt / 2.0  # each unordered colliding pair counted twice
samples = []
for _ in range(400):
    while True:
        v = tuple(rng.randint(-2 * T, 2 * T) for _ in range(3))
        if any(v):
            break
    samples.append(dups(v))
samples.sort()
frac_degen = sum(1 for s in samples if s > len(H) - 4096) / len(samples)
out = {"model": "independent uniform P_i, P[v.P = O] = 1/N per nonzero v up to sign",
       "per_cell": rows, "total_expected_r_ge_2": round(tot_e, 3), "total_observed_r_ge_2": tot_o,
       "b20_r3_n4096_single_relation_pair_count_quantiles": {q: samples[int(q * (len(samples) - 1))] for q in (0.1, 0.25, 0.5, 0.75, 0.9)},
       "b20_r3_n4096_fraction_of_single_relations_exceeding_slack_534": frac_degen,
       "note": "pair counts are an approximation of duplicate_skips (first-occurrence order, multiples of v and the stopping point are ignored)"}
json.dump(out, open(os.path.join(ROOT, "out/outputs/relation-expectation.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in out if k != "per_cell"}, indent=1))
for r in rows:
    if r["expected_curves_with_relation"] > 0.05 or r["observed_records_with_skips"]:
        print(r)
