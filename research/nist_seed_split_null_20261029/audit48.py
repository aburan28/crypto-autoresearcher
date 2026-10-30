"""Audit of runs/validation48_rows.jsonl(.gz) from the rows alone: recompute every split
count from (p, t), the KS distances and means against the model, check N = p + 1 - t and
N prime for all rows, and re-count 100 randomly sampled curves with PARI ellcard
(sample seed from the rows file's sha256, drawn after the run)."""
import gzip, hashlib, json, math, random, sys
import cypari2
from sympy import primerange
from analysis_lib import probs, pmf

path, out = sys.argv[1:3]
raw = (gzip.open if path.endswith(".gz") else open)(path, "rb").read()
rows = [json.loads(s) for s in raw.splitlines()]
P = cypari2.Pari(); P.allocatemem(10**9)
ells = list(primerange(3, 692)); res = dict(rows=len(rows), rows_sha256=hashlib.sha256(raw).hexdigest(), fields=[])
for trial in (0, 1):
    R = [r for r in rows if r["trial"] == trial]; p = R[0]["p"]
    assert all(r["p"] == p and r["N"] == p + 1 - r["t"] and P.isprime(r["N"]) for r in R)
    ks = []
    for r in R:
        D = r["t"] ** 2 - 4 * p; k = sum(1 for l in ells if D % l and pow(D % l, (l - 1) // 2, l) == 1)
        assert k == r["split"]; ks.append(k)
    f = pmf([probs(p, l, True)[0] for l in ells]); cdf = [sum(f[:k + 1]) for k in range(len(f))]
    em = sum(ks) / len(ks); ksd = max(abs(sum(1 for x in ks if x <= k) / len(ks) - cdf[k]) for k in range(len(f)))
    res["fields"].append(dict(p=p, n=len(R), emp_mean=em, ks_D=ksd))
rng = random.Random(int(res["rows_sha256"], 16)); sample = rng.sample(rows, 100)
res["pari_recount"] = dict(n=100, seed="int(rows_sha256, 16)",
                          mismatches=sum(int(P.ellcard(P.ellinit([-3, r["b"]], r["p"]))) != r["N"] for r in sample))
json.dump(res, open(out, "w"), indent=1); print(json.dumps(res, indent=1))
