"""Rerun of validate48.py that keeps one row per sampled prime-order curve (clears D2).

    python3 validate48_rows.py runs/validation48_rows.jsonl runs/validation48_summary.json

Identical RNG seed (20261029), RNG call order and PARI calls as validate48.py, so the
two 48-bit fields, all 3,000 curves and the printed aggregates must reproduce exactly.
Each row: trial, p, b, N (curve order), t, split count (odd l <= 691). Every non-prime
draw is counted (attempts) but not stored.
"""
import hashlib, json, math, random, sys
import cypari2
from sympy import primerange
from analysis_lib import probs, pmf as dist

rows_path, summary_path = sys.argv[1:3]
P = cypari2.Pari(); P.allocatemem(10**9)
ells = list(primerange(3, 692)); rng = random.Random(20261029)
summary = dict(seed=20261029, curves_per_field=1500, ells="odd primes 3..691", pari=str(P("version()")),
               python=sys.version.split()[0], fields=[])
with open(rows_path, "w") as out:
    for trial in range(2):
        p = int(P.nextprime(rng.getrandbits(48) | (1 << 47)))
        ks = []; attempts = 0
        while len(ks) < 1500:
            b = rng.randrange(1, p); N = int(P.ellcard(P.ellinit([-3, b], p))); attempts += 1
            if not P.isprime(N): continue
            t = p + 1 - N; D = t * t - 4 * p
            k = sum(1 for l in ells if D % l and pow(D % l, (l - 1) // 2, l) == 1)
            ks.append(k)
            out.write(json.dumps(dict(trial=trial, p=p, b=b, N=N, t=t, split=k), separators=(",", ":")) + "\n")
        ps = [probs(p, l, True)[0] for l in ells]; f = dist(ps)
        mu = sum(ps); sd = math.sqrt(sum(q * (1 - q) for q in ps))
        em = sum(ks) / len(ks); es = math.sqrt(sum((k - em) ** 2 for k in ks) / (len(ks) - 1))
        cdf = [sum(f[:k + 1]) for k in range(len(f))]
        ks_stat = max(abs(sum(1 for x in ks if x <= k) / len(ks) - cdf[k]) for k in range(len(f)))
        lo = sum(1 for x in ks if x <= 42) / len(ks)
        line = (f"p={p}: model mean {mu:.2f} sd {sd:.2f} | empirical(n=1500) mean {em:.2f} sd {es:.2f} | "
                f"KS D={ks_stat:.4f} (5% crit {1.36/math.sqrt(len(ks)):.4f}) | emp P(X<=42)={lo:.4f} model {cdf[42]:.4f}")
        print(line, flush=True)
        summary["fields"].append(dict(p=p, attempts=attempts, model_mean=mu, model_sd=sd, emp_mean=em, emp_sd=es,
                                      ks_D=ks_stat, ks_crit_5pct=1.36 / math.sqrt(len(ks)), emp_le_42=lo, model_le_42=cdf[42],
                                      printed=line))
summary["rows_sha256"] = hashlib.sha256(open(rows_path, "rb").read()).hexdigest()
json.dump(summary, open(summary_path, "w"), indent=1)
