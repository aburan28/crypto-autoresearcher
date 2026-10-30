"""Prime-order Chebotarev null and cutoff sweep for small-prime split counts.

Input: the archived 19-curve record of the 1997 seed-selection extension
(research/nist_seed_1997_selection_extension_20261023/sea_signature/runs/
scan-20261023T1840Z/raw.json). Output: results.json. Exact rational
probabilities are evaluated in floating point; no sampling.
"""
import hashlib, json, math, sys

RAW = sys.argv[1]
OUT = sys.argv[2]
CUTOFFS = [101, 251, 397, 691, 997, 2003, 5003]
HEADLINE = 691


def primes(lo, hi):
    s = bytearray([1]) * (hi + 1); s[0:2] = b"\0\0"
    for i in range(2, int(hi ** 0.5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(lo, hi + 1) if s[i]]


def chi(x, l):
    x %= l
    if x == 0: return 0
    return 1 if pow(x, (l - 1) // 2, l) == 1 else -1


_cache = {}
def probs(p, l, prime_order=True):
    """P(split), P(ramified) for Frob uniform in GL2(F_l) with det p,
    excluding eigenvalue 1 when prime_order. #{A: tr=u, det=d} = l^2 + l*chi(u^2-4d)."""
    key = (p % l, l, prime_order)
    if key in _cache: return _cache[key]
    d = p % l; w = {1: 0, -1: 0, 0: 0}
    for u in range(l):
        if prime_order and (1 - u + d) % l == 0: continue
        c = chi(u * u - 4 * d, l); w[c] += l * l + l * c
    s = sum(w.values()); _cache[key] = (w[1] / s, w[0] / s); return _cache[key]


def pmf(qs):
    f = [1.0]
    for q in qs:
        g = [0.0] * (len(f) + 1)
        for k, v in enumerate(f): g[k] += v * (1 - q); g[k + 1] += v * q
        f = g
    return f


raw_bytes = open(RAW, "rb").read(); raw = json.loads(raw_bytes)
rows = []
for r in raw["rows"]:
    p = int(r["p_hex"], 16); n = int(r["n_hex"], 16); t = p + 1 - n
    rows.append(dict(name=r["name"], label=r["label"], bits=r["field_bits"], uid=r["curve_uid"],
                     p=p, n=n, t=t, D=t * t - 4 * p, twist=p + 1 + t))

res = {"input": RAW, "input_sha256": hashlib.sha256(raw_bytes).hexdigest(),
       "model": "Frobenius mod l uniform on GL2(F_l) with det p; prime_order excludes eigenvalue 1; independent across l",
       "fields": {}, "curves": {}, "sweep": []}

for bits in sorted({r["bits"] for r in rows}):
    p = next(r["p"] for r in rows if r["bits"] == bits)
    ells = primes(3, HEADLINE)
    entry = {"n_odd_primes": len(ells)}
    for po in (False, True):
        qs = [probs(p, l, po)[0] for l in ells]
        entry["prime_order" if po else "unconditional"] = {
            "mean": sum(qs), "sd": math.sqrt(sum(q * (1 - q) for q in qs))}
    res["fields"][str(bits)] = entry

for B in CUTOFFS:
    ells = primes(3, B)
    for var in ("split", "split+ram", "split-twist"):
        pct = {}
        for r in rows:
            qs, k = [], 0
            for l in ells:
                s, z = probs(r["p"], l); c = chi(r["D"], l)
                if var == "split": qs.append(s); k += c == 1
                elif var == "split+ram": qs.append(s + z); k += c >= 0
                else:
                    if r["twist"] % l == 0: continue
                    qs.append(s); k += c == 1
            f = pmf(qs); below = sum(f[:k])
            pct[r["name"]] = dict(count=k, cdf_le=below + f[k], mid_pct=100 * (below + f[k] / 2))
            if B == HEADLINE and var == "split":
                res["curves"][r["name"]] = dict(label=r["label"], bits=r["bits"], uid=r["uid"], split=k,
                    ramified=sum(chi(r["D"], l) == 0 for l in ells),
                    n_small_factors=[l for l in ells if r["n"] % l == 0],
                    twist_small_factors=[l for l in ells if r["twist"] % l == 0],
                    cdf_le=pct[r["name"]]["cdf_le"], mid_pct=pct[r["name"]]["mid_pct"])
        lab = {r["name"]: (r["label"], r["bits"]) for r in rows}
        pairs = [(a, b) for a in pct for b in pct if lab[a][0] == "omitted" and lab[b][0] == "published" and lab[a][1] == lab[b][1]]
        med = lambda xs: (sorted(xs)[len(xs) // 2] if len(xs) % 2 else sum(sorted(xs)[len(xs) // 2 - 1:len(xs) // 2 + 1]) / 2)
        res["sweep"].append(dict(B=B, variant=var, n_odd_primes=len(ells),
            pairs_omitted_higher=sum(pct[a]["mid_pct"] > pct[b]["mid_pct"] for a, b in pairs),
            pairs_omitted_higher_raw_count=sum(pct[a]["count"] > pct[b]["count"] for a, b in pairs),
            pairs_total=len(pairs),
            published_median_pct=med([v["mid_pct"] for k2, v in pct.items() if lab[k2][0] == "published"]),
            omitted_median_pct=med([v["mid_pct"] for k2, v in pct.items() if lab[k2][0] == "omitted"]),
            per_curve=pct))
        print(B, var, res["sweep"][-1]["pairs_omitted_higher"], res["sweep"][-1]["pairs_omitted_higher_raw_count"],
              round(pct["prime239v1"]["mid_pct"], 3), flush=True)

json.dump(res, open(OUT, "w"), indent=1, sort_keys=True)
