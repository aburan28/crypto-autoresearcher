"""Frozen L-value study (PROTOCOL.md). Usage:
python3 lvalue.py <raw19.json> <acceptance analysis.json> <certificates.jsonl> <census_dir> <out_dir>"""
import glob, json, math, os, sys, time
from multiprocessing import Pool
import numpy as np
import cypari2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nist_seed_split_null_20261029"))
from analysis_lib import primes, probs, chi, load_rows  # noqa: E402

RAW, ACC, CERT, CENSUS, OUT = sys.argv[1:6]
X = 10 ** 8; MC_LMAX = 10 ** 5; NMC = 200_000; SEEDS = (20261030, 20261031)
CUTS = (101, 251, 397, 691, 997, 2003, 5003); CHECKPOINTS = (10 ** 6, 10 ** 7, 10 ** 8)
pari = cypari2.Pari(); pari.allocatemem(2 * 10 ** 9)
HERE = os.path.dirname(os.path.abspath(__file__))


def sieve(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False; s[4::2] = False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if s[i]: s[i * i::2 * i] = False
    return np.nonzero(s)[0].astype(np.int64)


ELL = sieve(X); ODD = ELL[1:]


def legendre_vec(D, ells):
    """(D/l) for odd primes l < 2^27, vectorized: residue by 16-bit Horner, then Euler's criterion."""
    a = abs(D); limbs = []
    while a: limbs.append(a & 0xFFFF); a >>= 16
    r = np.zeros_like(ells)
    for limb in reversed(limbs): r = (r * 65536 + limb) % ells
    if D < 0: r = (ells - r) % ells
    res = np.ones_like(ells); base = r.copy(); e = (ells - 1) // 2
    while e.any():
        odd = (e & 1).astype(bool)
        res = np.where(odd, res * base % ells, res); base = base * base % ells; e >>= 1
    out = np.where(res == 1, 1, -1); out[r == 0] = 0
    return out.astype(np.int8)


def kron2(D):
    m = D % 8
    return 0 if m % 2 == 0 else (1 if m in (1, 7) else -1)


def log_euler(D):
    """Cumulative -sum log(1 - chi(l)/l) at each checkpoint, l = 2 included via the Kronecker symbol."""
    c = legendre_vec(D, ODD).astype(np.float64)
    terms = -np.log1p(-c / ODD); cum = np.cumsum(terms)
    two = -math.log1p(-kron2(D) / 2)
    return {x: float(two + cum[np.searchsorted(ODD, x, side="right") - 1]) for x in CHECKPOINTS}, c


# ---- law of chi_Delta(l) under the prime-order null, closed form ----
def law(p, l):
    """(P+1, P0, P-1). Counts u in F_l by chi(u^2-4d): N0 = 1+chi(d), N+ - N- = -1; drop u = 1+d (disc (d-1)^2)."""
    d = p % l; n0 = 1 + chi(d, l); npl = (l - n0 - 1) // 2; nmi = (l - n0 + 1) // 2
    if d == 1 % l: n0 -= 1
    else: npl -= 1
    w = (npl * (l * l + l), n0 * l * l, nmi * (l * l - l)); s = sum(w)
    return tuple(x / s for x in w)


def null_draws(p, seed):
    """Per draw: E(B) at each cut (odd l <= B) and the odd l <= MC_LMAX log-Euler sum."""
    rng = np.random.default_rng(seed); acc = np.zeros(NMC); snaps = {}
    for l in primes(3, MC_LMAX):
        q1, q0, _ = law(p, l); u = rng.random(NMC)
        x = np.where(u < q1, 1.0, np.where(u < q1 + q0, 0.0, -1.0))
        acc -= np.log1p(-x / l)
        if l in LASTP: snaps[LASTP[l]] = acc.copy()
    snaps["L"] = acc
    return snaps


LASTP = {max(primes(3, B)): B for B in CUTS}


def midpct(null, x):
    return float(100 * ((null < x - 1e-12).mean() + 0.5 * (np.abs(null - x) <= 1e-12).mean()))


# ---- curves ----
def load_curves():
    rows19 = load_rows(RAW); acc = json.load(open(ACC))["rows"]
    certs = [json.loads(l) for l in open(CERT) if '"record": "certificate"' in l]
    cur = [dict(name=r["name"], label=r["label"], bits=r["bits"], uid=r["uid"], p=r["p"], D=r["D"]) for r in rows19]
    for r in acc:
        if r["label"] not in ("order_too_wide_only", "opposite_root_only"): continue
        cs = [c for c in certs if c["index"] == r["index"] and (c.get("target") == r["stream"] or c["name"].startswith(r["stream"] + ":"))]
        Ds = set()
        for c in cs:
            assert c["order_certified"] and c["n_prime_pari"]
            p = int(c["p"]); t = p + 1 - int(c["n"]); Ds.add((p, t * t - 4 * p))
        assert len(Ds) == 1; (p, D), = Ds
        if p.bit_length() == 384: continue
        cur.append(dict(name=f"heldout_{r['stream']}_{r['index']}", label="heldout", bits=p.bit_length(), uid=None, p=p, D=D))
    assert len(cur) == 61, len(cur)
    return cur


def census_dk():
    out = {}
    for f in glob.glob(os.path.join(CENSUS, "**", "results.json"), recursive=True):
        for e in json.load(open(f)):
            v = e.get("value") or {}
            if isinstance(v, str): v = eval(v)  # census stores a repr'd dict
            if e.get("curve_uid") not in (None, "None") and "D_K" in v: out[e["curve_uid"]] = (int(v["D_K"]), int(v["f_pi"]))
    return out


def per_curve(c):
    t0 = time.time(); D = c["D"]
    DK = int(pari.coredisc(D)); f = math.isqrt(D // DK); assert f * f * DK == D
    logs, _ = log_euler(DK)
    # E(B) and S from chi_Delta (python pow, independent of the vectorized path)
    E = {}; S691 = 0; acc = 0.0
    for l in primes(3, max(CUTS)):
        x = chi(D, l); acc -= math.log1p(-x / l)
        if l <= 691 and x == 1: S691 += 1
        if l in LASTP: E[LASTP[l]] = acc
    # truncated log L over odd l <= MC_LMAX with chi_{D_K}, for the null comparison
    cK = legendre_vec(DK, ODD[ODD <= MC_LMAX]).astype(np.float64)
    l1e5 = float(-np.log1p(-cK / ODD[ODD <= MC_LMAX]).sum())
    return dict(c, D=str(D), D_K=str(DK), f_pi=f, log2_absDK=math.log2(-DK), logL=logs, L_hat=math.exp(logs[X]),
                E=E, S691=S691, logL_odd_le_1e5=l1e5, secs=time.time() - t0)


def controls(curves, results):
    ctl = {}
    # positive (estimator): random fundamental discriminants with exact h
    rng = np.random.default_rng(SEEDS[0]); est = []
    for bits in (80, 90, 100, 110):
        k = 0
        while k < 5:
            n = int(rng.integers(0, 2 ** 62)) << (bits - 62) | int(rng.integers(0, 2 ** 62)) % (1 << (bits - 62))
            n |= 1 << (bits - 1); D = -n
            if D % 4 != 1 or not pari.isfundamental(D): continue
            t = time.time(); h = int(pari.qfbclassno(D) if bits == 80 else pari.quadclassunit(D)[0])
            L = math.pi * h / math.sqrt(n); lg, _ = log_euler(D)
            est.append(dict(bits=bits, D=str(D), h=h, logL_exact=math.log(L), logL_hat=lg[X], err=lg[X] - math.log(L),
                            err_1e6=lg[10 ** 6] - math.log(L), err_1e7=lg[10 ** 7] - math.log(L), secs=time.time() - t)); k += 1
            print("estimator control", bits, est[-1]["err"], flush=True)
    ctl["estimator"] = dict(rows=est, max_abs_err=max(abs(r["err"]) for r in est), pass_=all(abs(r["err"]) <= 0.01 for r in est))
    # positive (chi): S at 691 against the committed held-out run
    prev = json.load(open(os.path.join(HERE, "..", "nist_seed_split_null_20261029", "runs", "heldout.json")))
    pn = {x["name"]: x["split"] for x in prev["named19"]}
    ph = {f"heldout_{x['stream']}_{x['index']}": x["split"] for x in prev["heldout"]}
    mism = [r["name"] for r in results if (pn.get(r["name"], ph.get(r["name"])) != r["S691"])]
    vec = {}
    for r in results:
        if r["name"] in pn:
            c = legendre_vec(int(r["D"]), ODD[ODD <= 691]); vec[r["name"]] = int((c == 1).sum()) == pn[r["name"]]
    ctl["chi_S691"] = dict(python_mismatches=mism, vectorized_match_named=vec, pass_=not mism and all(vec.values()))
    # A/A implementation
    aa = {}
    pick = [r for r in results if r["name"] == "prime239v1"] + [r for r in results if r["name"] != "prime239v1"][:2]
    small = ODD[ODD <= 10 ** 6]
    for r in pick:
        for key in ("D", "D_K"):
            Dv = int(r[key]); v = legendre_vec(Dv, small)
            py = np.array([chi(Dv, int(l)) for l in small], dtype=np.int8)
            aa[f"{r['name']}:{key}"] = int((v != py).sum())
    ctl["aa_impl"] = dict(mismatches=aa, pass_=not any(aa.values()))
    # census cross-check
    cen = census_dk(); cc = {}
    for r in results:
        if r["uid"] in cen: cc[r["name"]] = (cen[r["uid"]][0] == int(r["D_K"]) and cen[r["uid"]][1] == r["f_pi"])
    ctl["census_DK"] = dict(checked=len(cc), mismatches=[k for k, v in cc.items() if not v], pass_=all(cc.values()))
    return ctl


def main():
    os.makedirs(OUT, exist_ok=True)
    curves = load_curves()
    for p in sorted({c["p"] for c in curves}):  # closed-form law equals analysis_lib.probs
        for l in primes(3, 400):
            a = law(p, l); b = probs(p, l)
            assert abs(a[0] - b[0]) < 1e-12 and abs(a[1] - b[1]) < 1e-12, (p, l, a, b)
    print("law matches probs for l < 400", flush=True)
    with Pool(4) as pool: results = pool.map(per_curve, curves)
    print("curves done", flush=True)
    fields = sorted({(r["bits"], r["p"]) for r in results})
    null = {}
    for bits, p in fields:
        null[bits] = {s: null_draws(p, s) for s in SEEDS}; print("null", bits, flush=True)
    for r in results:
        nd = null[r["bits"]][SEEDS[0]]; nd2 = null[r["bits"]][SEEDS[1]]
        r["pct_logL"] = midpct(nd["L"], r["logL_odd_le_1e5"]); r["pct_logL_seed2"] = midpct(nd2["L"], r["logL_odd_le_1e5"])
        r["pct_E"] = {B: midpct(nd[B], r["E"][B]) for B in CUTS}; r["pct_E_seed2"] = {B: midpct(nd2[B], r["E"][B]) for B in CUTS}
        r["p"] = str(r["p"])
    ctl = controls(curves, results)
    v = next(r for r in results if r["name"] == "prime239v1")
    se = lambda q: 100 * math.sqrt(max(q / 100 * (1 - q / 100), 1 / NMC) / NMC)
    ctl["aa_mc"] = dict(logL=(v["pct_logL"], v["pct_logL_seed2"]), E691=(v["pct_E"][691], v["pct_E_seed2"][691]),
                        pass_=abs(v["pct_logL"] - v["pct_logL_seed2"]) <= 3 * math.sqrt(2) * se(v["pct_logL"])
                        and abs(v["pct_E"][691] - v["pct_E_seed2"][691]) <= 3 * math.sqrt(2) * se(v["pct_E"][691]))
    ho = sorted(r["pct_logL"] / 100 for r in results if r["label"] == "heldout"); n = len(ho)
    ks = max(max((i + 1) / n - u, u - i / n) for i, u in enumerate(ho))
    ctl["null_calibration"] = dict(n=n, ks_D=ks, ks_crit_5pct=1.358 / math.sqrt(n))
    q = v["pct_logL"]; decision = "ordinary" if 2.5 <= q <= 97.5 else ("low" if q < 1 else "high" if q > 99 else "borderline")
    rank = sorted(r["logL"][X] for r in results).index(v["logL"][X]) + 1
    summary = dict(prime239v1=dict(logL_hat=v["logL"][X], L_hat=v["L_hat"], pct_logL=q, pct_E=v["pct_E"],
                                   rank_logL_among_61=rank, decomposition=dict(
                                       l2=-math.log1p(-kron2(int(v["D_K"])) / 2), l3_691=v["E"][691],
                                       gt691=v["logL"][X] + math.log1p(-kron2(int(v["D_K"])) / 2) - v["E"][691])),
                   decision_Q1=decision, controls_pass={k: c.get("pass_") for k, c in ctl.items()})
    json.dump(dict(protocol="PROTOCOL.md", x=X, seeds=SEEDS, nmc=NMC, rows=results, summary=summary),
              open(os.path.join(OUT, "lvalues.json"), "w"), indent=1, default=str)
    json.dump(ctl, open(os.path.join(OUT, "controls.json"), "w"), indent=1, default=str)
    with open(os.path.join(OUT, "rows.jsonl"), "w") as fh:
        for r in results:
            fh.write(json.dumps(dict(instance_id=r["name"], arm=r["label"], field_bits=r["bits"], log_L_hat=r["logL"][X],
                                     pct_logL=r["pct_logL"], E691=r["E"][691], pct_E691=r["pct_E"][691],
                                     status="succeeded")) + "\n")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
