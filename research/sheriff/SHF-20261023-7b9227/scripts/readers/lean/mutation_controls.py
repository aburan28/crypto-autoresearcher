#!/usr/bin/env python3
"""Proves-too-much controls: one-digit mutations of each DkCert field must
falsify DkCert.Holds (re-implemented); a one-monomial mutation of the Semaev
equations must break the S3 extensional identity and change the literal rows.
Usage: python3 -I mutation_controls.py <repo-root>"""
import re, json, sys, random
ROOT = sys.argv[1]
src = open(ROOT + "/formal/CryptoResearch/Endosweep/DkExactBatch4.lean").read()
def emod(a, b): return a % abs(b)
def holds(c):
    odd = c["small"] + c["large"]
    prod = 1
    for p, e in c["factors"]: prod *= p ** e
    P = 1
    for p in odd: P *= p
    D = c["DK"]
    mnd = (abs(D) + emod(D, 2)) // 4
    return all([
        c["q"] + 1 - c["t"] == c["h"] * c["n"],
        c["t"] ** 2 - 4 * c["q"] == D * c["f"] ** 2,
        4 * c["q"] - c["t"] ** 2 == prod,
        [p for p, e in c["factors"] if e % 2 == 1] == odd,
        len(set(odd)) == len(odd),
        (D == -P and emod(D, 4) == 1) or (D == -4 * P and emod(-P, 4) in (2, 3)),
        D < 0 and emod(D, 4) in (0, 1), mnd == c["deg"], P == c["s"],
        2 ** c["L"] <= abs(D) < 2 ** (c["L"] + 1), 2 ** (c["L"] - 2) <= c["deg"],
    ])
rng = random.Random(7)
res = {}
for name, body in re.findall(r"def (\w+) : DkCert where\n(.*?)\n\n", src, re.S):
    f = dict(l.strip().split(" := ", 1) for l in body.strip().split("\n"))
    c = dict(q=int(f["q"]), t=int(f["t"]), h=int(f["h"]), n=int(f["n"]), DK=int(f["DK"]), f=int(f["f"]),
             deg=int(f["deg"]), factors=[(int(a), int(b)) for a, b in re.findall(r"\((\d+), (\d+)\)", f["factors"])],
             small=[int(a) for a, _ in re.findall(r"\((\d+), (\d+)\)", f["smallPrimes"])],
             large=[int(x) for x in re.findall(r"\d+", f["largePrimes"])], s=int(f["s"]), L=int(f["L"]))
    base = holds(c)
    muts = {}
    for fld in ("q", "t", "n", "DK", "deg", "s"):
        d = dict(c); v = str(abs(c[fld])); i = rng.randrange(len(v))
        nv = v[:i] + str((int(v[i]) + 1) % 10) + v[i + 1:]
        d[fld] = int(nv) * (1 if c[fld] >= 0 else -1)
        muts[fld] = holds(d)
    d = dict(c); fac = list(c["factors"]); p, e = fac[-1]; fac[-1] = (p + 2, e); d["factors"] = fac
    d["large"] = [x if x != p else p + 2 for x in c["large"]]
    muts["largest_factor+2"] = holds(d)
    d = dict(c); d["L"] = c["L"] + 1; muts["L+1"] = holds(d)
    res[name] = dict(holds=base, mutated_holds=muts)
out = {"dk": res}
# Semaev: mutate one monomial of each equation
FORMAL = ROOT + "/formal/CryptoResearch/Semaev/"
s = open(FORMAL + "BooleanParityFiniteCertificate.lean").read()
eqs = json.loads(re.search(r"def equations : List \(List Nat\) :=\s*(\[\[.*?\]\])", s, re.S).group(1).replace("\n", ""))
MOD = 0b10011
def gm(a, b):
    r = 0
    for i in range(4):
        if (b >> i) & 1: r ^= a << i
    for i in (6, 5, 4):
        if (r >> i) & 1: r ^= MOD << (i - 4)
    return r
B = [9, 3, 2, 12]
def val(a, off):
    v = 0
    for i in range(4):
        if (a >> (off + i)) & 1: v ^= B[i]
    return v
def S3(x1, x2):
    e2 = gm(x1, x2) ^ x1 ^ x2
    return gm(e2, e2) ^ gm(x1, x2) ^ 1
def ok(E):
    return all(sum(((sum(1 for t in f if (t & a) == t) & 1) << b) for b, f in enumerate(E)) == S3(val(a, 0), val(a, 4)) for a in range(256))
sem = {"unmutated": ok(eqs)}
for k in range(4):
    E = [list(f) for f in eqs]; E[k] = E[k][:-1]
    sem[f"drop_last_monomial_eq{k}"] = ok(E)
out["semaev_equation_mutations_identity_holds"] = sem
print(json.dumps(out, indent=1))
