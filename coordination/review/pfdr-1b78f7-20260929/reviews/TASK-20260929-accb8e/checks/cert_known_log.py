"""Disjoint certificate check (own code, exponent domain): every harvested row of the
known_log arm (R10, m = 3, bits <= 24; census and on) must satisfy
  sum_i c_i*(i+1) + kcoef*k == rhs (mod N),
since F_i = (i+1)P (1-based logs, G6) and Q = kP with k from the C-5 / main-panel rule
k = random.Random(f"target|{bits}|{c}|0").randrange(1, N). TT/TB rows (kcoef = rhs = 0)
and SS rows (two-target rows) are all checked. Shares no code with harvest.py."""
import gzip, json, os, random, sys, collections
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks")); import rl
R = os.path.join(rl.WT, "experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-census-m3")
N = {}
for l in gzip.open(rl.opened(os.path.join(R, "rows.jsonl.gz"), "cert check: R10 rows (N per curve)"), "rt"):
    r = json.loads(l); N[(r["bits"], r["curve"])] = r["N"]
tally = collections.Counter(); bad = []
p = os.path.join(R, "harvest-rows.jsonl.gz"); rl.opened(p, "cert check: R10 harvest rows streamed (known_log rows only)")
kcache = {}
with gzip.open(p, "rt") as f:
    for l in f:
        if '"known_log"' not in l: continue
        r = json.loads(l)
        if r["arm"] != "known_log": continue
        key = (r["bits"], r["curve"]); n = N[key]
        if key not in kcache: kcache[key] = random.Random(f"target|{r['bits']}|{r['curve']}|0").randrange(1, n)
        k = kcache[key]
        lhs = (sum(c * (i + 1) for i, c in r["coeffs"]) + r["kcoef"] * k - r["rhs"]) % n
        ok = lhs == 0
        tally[(r["class"], r["mode"], ok)] += 1
        if not ok and len(bad) < 10: bad.append([r["bits"], r["curve"], r["mode"], r["class"]])
res = {"tally": {f"{a}|{b}|{c}": v for (a, b, c), v in sorted(tally.items())}, "failures_first": bad,
       "instances": len(kcache), "all_ok": not any(not c for (_, _, c) in tally)}
json.dump(res, open(os.path.join(W, "checks/out/cert-known-log.json"), "w"), indent=1)
print(res)
