"""Truncated L(1, chi) Euler products for the 69 draft-eligible NIST/ANSI seed curves.

Frozen with PROTOCOL.md / protocol.json before any target curve is evaluated.

    python3 analyze.py RAW19 ACCEPTANCE CERTIFICATES CALIBRATION OUT

For each eligible seed position (one Delta = t^2 - 4p per position):
  logP_delta = sum_{l <= X} -log(1 - chi_Delta(l)/l)   decisive statistic
  logP_DK    = same with chi_{D_K}, the l-part of the conductor stripped
               (descriptive; approximates log L(1, chi_{D_K}))
Null for logP_delta: Frobenius mod l uniform on GL2(F_l) with det p and no
eigenvalue 1 (prime order), independent over l. Monte Carlo over odd l <= L0,
an exact-moment Gaussian for L0 < l <= X; the l = 2 term is the constant
chi(2) = -1 (t odd for prime n, so Delta = 5 mod 8).
"""
import hashlib, json, math, sys
import numpy as np

X = 10**6          # Euler-product cutoff
L0 = 1000          # Monte Carlo below, Gaussian above
NMC = 10**6        # null Monte Carlo draws per field
NPERM = 200_000    # permutation draws (descriptive comparison)
SEED = 20261030
TARGET = ("prime239v3", 2185)   # prime239v1
THRESHOLD_PCT = 1.0


def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0:2] = b"\0\0"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


def kron(D, l):
    """Kronecker symbol (D / l) for a prime l and a discriminant D (D = 0, 1 mod 4)."""
    if l == 2:
        if D % 2 == 0: return 0
        return 1 if D % 8 in (1, 7) else -1
    r = D % l
    if r == 0: return 0
    return 1 if pow(r, (l - 1) // 2, l) == 1 else -1


def strip_conductor(D, l):
    """Remove the l-part of the conductor: largest l^(2e) with D / l^(2e) still a discriminant."""
    if l == 2:
        while D % 4 == 0 and (D // 4) % 4 in (0, 1): D //= 4
    else:
        l2 = l * l
        while D % l2 == 0: D //= l2
    return D


def chi_dk(D, l):
    return kron(strip_conductor(D, l), l)


def null_probs(p, l):
    """(P(+1), P(-1), P(0)) for chi_Delta(l), l odd, under the prime-order GL2(F_l) model.
    Closed form: with d = p mod l, N0 = 1 + (d/l) traces give u^2 - 4d = 0,
    N+ = (l - 2 - (d/l)) / 2 give a nonzero square; the excluded trace u = 1 + d has
    u^2 - 4d = (1 - d)^2 (zero iff d = 1). #{A : tr u, det d} = l^2 + l chi(u^2 - 4d)."""
    d = p % l
    cd = 1 if pow(d, (l - 1) // 2, l) == 1 else -1
    n0 = 1 + cd; npl = (l - 2 - cd) // 2; nmi = l - npl - n0
    if d == 1 % l: n0 -= 1
    else: npl -= 1
    wp, wm, w0 = (l * l + l) * npl, (l * l - l) * nmi, l * l * n0
    s = wp + wm + w0
    return wp / s, wm / s, w0 / s


def null_probs_brute(p, l):
    d = p % l; w = {1: 0, -1: 0, 0: 0}
    for u in range(l):
        if (1 - u + d) % l == 0: continue
        c = kron(u * u - 4 * d, l); w[c] += l * l + l * c
    s = sum(w.values()); return w[1] / s, w[-1] / s, w[0] / s


def term(c, l):
    return -math.log(1.0 - c / l)


def self_test():
    """Instrument checks run on every invocation; no target data involved."""
    for p in (2**127 - 1, 2**192 - 2**64 - 1, 10**18 + 9, 1000003):
        for l in primes_upto(200)[1:]:
            if p % l == 0: continue
            a, b = null_probs(p, l), null_probs_brute(p, l)
            assert max(abs(x - y) for x, y in zip(a, b)) < 1e-12, (p, l, a, b)
    assert kron(5, 2) == -1 and kron(1, 2) == 1 and kron(-3, 3) == 0 and kron(-3, 7) == 1
    assert strip_conductor(-3 * 49, 7) == -3 and strip_conductor(-4 * 4, 2) == -4 and strip_conductor(-3 * 4, 2) == -3
    return True


def null_field(p, small, large, rng):
    """Monte Carlo sums over odd l <= L0 and exact Gaussian moments for L0 < l <= X."""
    S = np.full(NMC, term(-1, 2))
    for l in small[1:]:
        pp, pm, _ = null_probs(p, l)
        u = rng.random(NMC)
        S += np.where(u < pp, term(1, l), np.where(u < pp + pm, term(-1, l), 0.0))
    mu = var = 0.0
    for l in large:
        pp, pm, p0 = null_probs(p, l)
        a, b = term(1, l), term(-1, l)
        m = pp * a + pm * b; mu += m; var += pp * a * a + pm * b * b - m * m
    return S, mu, math.sqrt(var)


def pct(x, S, mu, sd):
    z = (x - S - mu) / sd
    return 100.0 * float(np.mean(0.5 * (1.0 + np.vectorize(math.erf)(z / math.sqrt(2.0)))))


def main():
    raw19, acc, cert, calib, out = sys.argv[1:6]
    self_test()
    cal = json.load(open(calib))
    tau = cal["tolerance_abs_log"]
    primes = primes_upto(X); small = [l for l in primes if l <= L0]; large = [l for l in primes if l > L0]

    # positive control: secp256k1, D_K = -3, L(1, chi_-3) = pi / (3 sqrt 3)
    p_k1 = 2**256 - 2**32 - 977
    n_k1 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    t = p_k1 + 1 - n_k1; D = t * t - 4 * p_k1
    lp = sum(term(chi_dk(D, l), l) for l in primes)
    pos = dict(curve="secp256k1", logP_DK=lp, log_L_exact=math.log(math.pi / (3 * math.sqrt(3))), tolerance=tau)
    pos["passes"] = abs(lp - pos["log_L_exact"]) <= tau

    accrows = json.load(open(acc))["rows"]
    certs = [json.loads(s) for s in open(cert) if '"record": "certificate"' in s]
    names = {}
    for r in json.load(open(raw19))["rows"]:
        if r["label"] == "published": names[int(r["n_hex"], 16)] = r["name"]
    rows = []
    for r in accrows:
        cs = [c for c in certs if c["target"] == r["stream"] and c["index"] == r["index"]]
        assert cs and all(c["order_certified"] and c["n_prime_pari"] for c in cs), r
        Ds = {(int(c["p"]), (int(c["p"]) + 1 - int(c["n"])) ** 2 - 4 * int(c["p"])) for c in cs}
        assert len(Ds) == 1, ("branches disagree", r)
        (p, D), = Ds
        assert D % 8 == 5, ("t odd expected for prime order", r)
        nm = next((names[int(c["n"])] for c in cs if int(c["n"]) in names), None)
        rows.append(dict(stream=r["stream"], index=r["index"], label=r["label"], name=nm, field_bits=p.bit_length(), p=p, D=D))

    rng = np.random.default_rng(SEED)
    nulls = {}
    for p in sorted({x["p"] for x in rows}):
        nulls[p] = null_field(p, small, large, rng)
    for x in rows:
        x["logP_delta"] = sum(term(kron(x["D"], l), l) for l in primes)
        x["logP_DK"] = sum(term(chi_dk(x["D"], l), l) for l in primes)
        x["pct_delta"] = pct(x["logP_delta"], *nulls[x["p"]])
    tgt = next(x for x in rows if (x["stream"], x["index"]) == TARGET)
    assert tgt["name"] == "prime239v1"

    # descriptive: within-field published vs unpublished (fields with both)
    pub = [x for x in rows if x["label"] == "published"]; unp = [x for x in rows if x["label"] != "published"]
    fields = sorted({x["field_bits"] for x in pub} & {x["field_bits"] for x in unp})
    def frac(P, U):
        num = den = 0
        for f in fields:
            for a in U:
                for b in P:
                    if a["field_bits"] == f == b["field_bits"]:
                        den += 1; num += (a["logP_delta"] > b["logP_delta"]) + 0.5 * (a["logP_delta"] == b["logP_delta"])
        return num / den, den
    obs, den = frac(pub, unp)
    rng2 = np.random.default_rng(SEED + 1); ge = 0
    pools = {f: [x for x in rows if x["field_bits"] == f] for f in fields}
    npub = {f: sum(x["label"] == "published" for x in pools[f]) for f in fields}
    for _ in range(NPERM):
        P, U = [], []
        for f in fields:
            idx = rng2.permutation(len(pools[f]))
            P += [pools[f][i] for i in idx[:npub[f]]]; U += [pools[f][i] for i in idx[npub[f]:]]
        ge += frac(P, U)[0] >= obs - 1e-12
    for x in rows: x["p"] = str(x["p"]); x["D"] = str(x["D"])
    unp_pct = sorted(x["pct_delta"] / 100 for x in unp); n = len(unp_pct)
    ks = max(max((i + 1) / n - v, v - i / n) for i, v in enumerate(unp_pct))
    res = dict(protocol="PROTOCOL.md", X=X, L0=L0, nmc=NMC, seed=SEED, self_test="passed",
               positive_control=pos, instrument_valid=bool(pos["passes"]),
               decisive=dict(target="prime239v1", pct_delta=tgt["pct_delta"], threshold_pct=THRESHOLD_PCT,
                             verdict=("invalid_measurement" if not pos["passes"] else
                                      "extreme_persists" if tgt["pct_delta"] < THRESHOLD_PCT else "not_extreme")),
               descriptive=dict(unpublished_over_published=obs, pairs=den, perm_p_one_sided=(ge + 1) / (NPERM + 1),
                                unpublished_ks_vs_uniform=dict(n=n, D=ks, crit_5pct=1.36 / math.sqrt(n))),
               rows=rows)
    with open(out, "w") as fh: json.dump(res, fh, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
