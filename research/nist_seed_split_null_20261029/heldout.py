"""Frozen held-out test (PROTOCOL.md). Usage:
python3 heldout.py <raw19.json> <acceptance analysis.json> <certificates.jsonl> <out.json>"""
import json, sys
import numpy as np
from analysis_lib import primes, probs, chi, load_rows

RAW, ACC, CERT, OUT = sys.argv[1:5]
B = 691; NMC = 200_000; SEED = 20261029
ELLS = primes(3, B)
rows19 = load_rows(RAW)
acc = json.load(open(ACC))["rows"]
certs = [json.loads(l) for l in open(CERT) if '"record": "certificate"' in l]

def split(p, D): return sum(chi(D, l) == 1 for l in ELLS)
def midpct(p, S):
    f = np.zeros(len(ELLS) + 2); f[0] = 1.0
    for l in ELLS:
        q = probs(p, l)[0]; f[1:] = f[1:] * (1 - q) + f[:-1] * q; f[0] *= 1 - q
    return 100 * (f[:S].sum() + f[S] / 2)

def cert_rows(stream, index):
    rs = [c for c in certs if c["index"] == index and (c.get("target") == stream or c["name"].startswith(stream + ":"))]
    return rs

FIELD_OF_STREAM = {}
held = []
for r in acc:
    if r["label"] not in ("order_too_wide_only", "opposite_root_only") and not (r["stream"] == "P-384" and r["label"] == "published"):
        continue
    cs = cert_rows(r["stream"], r["index"])
    assert cs, ("missing certificate", r["stream"], r["index"])
    Ds = set()
    for c in cs:
        assert c["order_certified"] and c["n_prime_pari"], c["name"]
        p = int(c["p"]); n = int(c["n"]); t = p + 1 - n; Ds.add((p, t * t - 4 * p))
    assert len(Ds) == 1, ("branches disagree", r)
    (p, D), = Ds
    S = split(p, D)
    held.append(dict(stream=r["stream"], index=r["index"], label=("published" if r["label"] == "published" else "heldout"),
                     kind=r["label"], bits=p.bit_length(), branches=len(cs), split=S, mid_pct=midpct(p, S), _D=D))

named = [dict(stream=None, index=None, name=r["name"], label=r["label"], bits=r["bits"], split=split(r["p"], r["D"]),
              mid_pct=midpct(r["p"], split(r["p"], r["D"])), _D=r["D"]) for r in rows19]
# field bit length of the 19-curve record (239-bit field is 239 bits; others match)
for h in held: assert h["bits"] in (192, 224, 239, 256, 384), h

def pair_frac(hi, lo):
    num = den = 0
    for a in hi:
        for b in lo:
            if a["bits"] != b["bits"]: continue
            den += 1; num += 1.0 if a["split"] > b["split"] else 0.5 if a["split"] == b["split"] else 0.0
    return num / den if den else float("nan"), den

def perm_p(hi, lo, rng, nmc=NMC):
    obs, den = pair_frac(hi, lo)
    fields = sorted({x["bits"] for x in lo})
    pools = {f: np.array([x["split"] for x in hi + lo if x["bits"] == f]) for f in fields}
    nlo = {f: sum(x["bits"] == f for x in lo) for f in fields}
    ge = 0
    for _ in range(nmc // 1000):
        num = np.zeros(1000)
        for f in fields:
            v = pools[f]; perm = np.argsort(rng.random((1000, len(v))), axis=1)
            L = v[perm[:, :nlo[f]]]; H = v[perm[:, nlo[f]:]]
            d = H[:, :, None] - L[:, None, :]
            num += (d > 0).sum(axis=(1, 2)) + 0.5 * (d == 0).sum(axis=(1, 2))
        ge += int((num / den >= obs - 1e-12).sum())
    return obs, den, (ge + 1) / (nmc + 1)

rng = np.random.default_rng(SEED)
pub4 = [x for x in named if x["label"] == "published"]
om11 = [x for x in named if x["label"] == "omitted"]
ho4 = [x for x in held if x["label"] == "heldout" and x["bits"] != 384]
obs, den, p = perm_p(ho4, pub4, rng)
primary = dict(statistic="fraction of within-field (heldout, published) pairs with heldout split > published (ties 1/2)",
               pairs=den, observed=obs, perm_p_one_sided=p, nmc=NMC, seed=SEED, replicates=p <= 0.05)
# secondary
u = sorted(x["mid_pct"] / 100 for x in ho4); n = len(u)
ks = max(max((i + 1) / n - v, v - i / n) for i, v in enumerate(u))
o2, d2, p2 = perm_p(om11, ho4, np.random.default_rng(SEED + 1))
p384 = [x for x in held if x["bits"] == 384]
p384_rank = sorted(p384, key=lambda x: x["split"])
sens = []
for Bs in (101, 251, 397, 997, 2003, 5003):
    E = primes(3, Bs)
    cnt = lambda x: dict(bits=x["bits"], split=sum(chi(x["_D"], l) == 1 for l in E))
    f, d = pair_frac([cnt(x) for x in ho4], [cnt(x) for x in pub4])
    sens.append(dict(B=Bs, pairs=d, heldout_over_published=f))
for x in held + named: x.pop("_D")
out = dict(protocol="PROTOCOL.md", cutoff=B, n_odd_primes=len(ELLS), heldout=held, named19=named, primary=primary,
           secondary=dict(heldout_ks_vs_uniform=dict(n=n, D=ks, crit_5pct=1.36 / n ** 0.5),
                          named_vs_heldout=dict(statistic="fraction of within-field (named omitted, heldout) pairs with named split > heldout",
                                                pairs=d2, observed=o2, perm_p_one_sided=p2),
                          sensitivity_other_cutoffs=sens,
                          p384=[dict(label=x["label"], index=x["index"], split=x["split"], mid_pct=x["mid_pct"]) for x in p384_rank]))
json.dump(out, open(OUT, "w"), indent=1, default=float)
print(json.dumps(dict(primary=primary, secondary=out["secondary"]), indent=1, default=float))
for f in (192, 224, 239, 256):
    print(f, "published", sorted(x["split"] for x in pub4 if x["bits"] == f), "named", sorted(x["split"] for x in om11 if x["bits"] == f),
          "heldout", sorted(x["split"] for x in ho4 if x["bits"] == f))
