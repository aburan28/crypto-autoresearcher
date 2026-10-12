"""AFTER THE SEAL -- independent re-verification of harvested-row certificates and of the
j0 formal flags.

Lineage: the base-construction CONVENTIONS (index order, min-y lift, seed labels) were
read from factor_base.py/curve.py after the seal; every computation here is my own code
(modular sqrt, affine point arithmetic, scalar multiplication, orbit/formal-span test).
No engine module is imported.

  * every retained TT and TB harvested row (kcoef = rhs = 0) of every arm except
    known_log (already checked in the exponent domain) must satisfy sum_i c_i F_i = O on
    my reconstruction of the arm's base (random-arm seeds c, c+1000, ... c+5000 as in the
    CLI; j0 random seeds c, c+1000, c+2000);
  * j0 panel (every arm): the formal flag of every TT/TB row is recomputed from my own
    automorphism basis (omega = primitive_root(p)^((p-1)/3), lambda the root of
    l^2 + l + 1 = 0 mod N with [lambda]F = (omega x_F, y_F) checked on a base point,
    eps from the y's), and pairs_formal / pairs_nonformal of TT and TB are recounted."""
import collections, glob, gzip, json, os, sys, random
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
RUNS = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs")
SEED_OFF = {"random_sub_r0": 0, "random_sub_r1": 1000, "random_sub_r2": 2000, "random_dick_r0": 3000,
            "random_dick_r1": 4000, "random_dick_r2": 5000, "j0_random_r0": 0, "j0_random_r1": 1000,
            "j0_random_r2": 2000}


def sqrtm(n, p):
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    # Cipolla (own choice of algorithm)
    a = 0
    while pow((a * a - n) % p, (p - 1) // 2, p) != p - 1:
        a += 1
    w = (a * a - n) % p

    def mul(x, y):
        return ((x[0] * y[0] + x[1] * y[1] % p * w) % p, (x[0] * y[1] + x[1] * y[0]) % p)
    r, b, e = (1, 0), (a, 1), (p + 1) // 2
    while e:
        if e & 1:
            r = mul(r, b)
        b = mul(b, b)
        e >>= 1
    return r[0]


def lift(x, a, b, p):
    y = sqrtm((x * x * x + a * x + b) % p, p)
    if y is None or y == 0:
        return None
    return (x, min(y, p - y))


def add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        l = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        l = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (l * l - x1 - x2) % p
    return (x3, (l * (x1 - x3) - y1) % p)


def mul(k, P, a, p):
    if k < 0:
        k, P = -k, (None if P is None else (P[0], (-P[1]) % p))
    R = None
    while k:
        if k & 1:
            R = add(R, P, a, p)
        P = add(P, P, a, p)
        k >>= 1
    return R


def factor(n):
    f, d = set(), 2
    while d * d <= n:
        while n % d == 0:
            f.add(d)
            n //= d
        d += 1
    if n > 1:
        f.add(n)
    return f


def prim_root(p):
    qs = factor(p - 1)
    g = 2
    while any(pow(g, (p - 1) // q, p) == 1 for q in qs):
        g += 1
    return g


def build_base(r):
    p, a, b = r["p"], r["a"], r["b"]
    arm, size, fp, c = r["arm"], r["fb_size"], r.get("fb_params") or {}, r["curve"]
    pts = []
    if arm == "small_x":
        x = 0
        while len(pts) < size and x < p:
            P = lift(x, a, b, p)
            if P is not None:
                pts.append(P)
            x += 1
    elif arm in ("subgroup", "j0_coset"):
        d, g = fp["d"], fp["coset"]
        zeta = pow(prim_root(p), (p - 1) // d, p)
        z = g
        for _ in range(d):
            P = lift(z, a, b, p)
            if P is not None:
                pts.append(P)
            z = z * zeta % p
    elif arm == "dickson":
        d, g, cc = fp["d"], fp["coset"], fp["c"]
        zeta = pow(prim_root(p), (p - 1) // d, p)
        u = g
        for _ in range(d):
            P = lift((u + cc * pow(u, -1, p)) % p, a, b, p)
            if P is not None:
                pts.append(P)
            u = u * zeta % p
    elif arm in SEED_OFF:
        rng = random.Random(f"fb-random|{p}|{a}|{b}|{size}|{c + SEED_OFF[arm]}")
        seen = set()
        while len(pts) < size:
            x = rng.randrange(p)
            if x in seen:
                continue
            seen.add(x)
            P = lift(x, a, b, p)
            if P is not None:
                pts.append(P)
    else:
        return None
    return pts


def j0_structure(pts, p, N, a):
    """(mu, comp): F_i = mu_i * F_root(i) over the formal relations; lambda from own check."""
    omega = pow(prim_root(p), (p - 1) // 3, p)
    # lambda: roots of l^2 + l + 1 mod N (N prime, N = 1 mod 3)
    s = sqrtm(N - 3, N)
    inv2 = pow(2, -1, N)
    roots = [((-1 + s) * inv2) % N, ((-1 - s) * inv2) % N]
    F0 = pts[0]
    target = ((omega * F0[0]) % p, F0[1])
    lam = [l for l in roots if mul(l, F0, a, p) == target]
    if len(lam) != 1:
        return None, None, "lambda check failed"
    lam = lam[0]
    xi = {P[0]: i for i, P in enumerate(pts)}
    parent = list(range(len(pts)))
    mu = [1] * len(pts)  # F_i = mu_i * F_parent-root

    def find(i):
        # returns (root, multiplier m with F_i = m F_root)
        m = 1
        while parent[i] != i:
            m = m * mu[i] % N
            i = parent[i]
        return i, m
    for ia, P in enumerate(pts):
        xb = omega * P[0] % p
        if xb in xi:
            ib = xi[xb]
            eps = 1 if pts[ib][1] == P[1] else -1
            # F_b = eps*lam*F_a
            ra, ma = find(ia)
            rb, mb = find(ib)
            if ra != rb:
                # F_b = mb F_rb and F_b = eps lam F_a = eps lam ma F_ra -> F_rb = eps lam ma / mb F_ra
                parent[rb] = ra
                mu[rb] = eps * lam * ma * pow(mb, -1, N) % N
    comp = [find(i) for i in range(len(pts))]
    return comp, lam, None


def residual(coeffs, comp, N):
    r = collections.defaultdict(int)
    for i, c in coeffs:
        root, m = comp[i]
        r[root] = (r[root] + c * m) % N
    return tuple(sorted((k, v) for k, v in r.items() if v))


def sources():
    out = [("R10", os.path.join(RUNS, "RUN-PFDR-1b78f7-census-m3", "rows.jsonl.gz"),
            [os.path.join(RUNS, "RUN-PFDR-1b78f7-census-m3", "harvest-rows.jsonl.gz")])]
    out.append(("R11a1", os.path.join(RUNS, "RUN-PFDR-1b78f7-census-m4", "rows.jsonl.gz"),
                [os.path.join(RUNS, "RUN-PFDR-1b78f7-census-m4", "harvest-rows.jsonl.gz")]))
    for lab, rd, att in [("R11a2", "RUN-PFDR-1b78f7-census-m4", "attempt-2"), ("R12", "RUN-PFDR-1b78f7-census-m5", "attempt-1"),
                         ("R14", "RUN-PFDR-1b78f7-j0", "attempt-1"), ("R16", "RUN-PFDR-1b78f7-stage-r", "attempt-1")]:
        for jd in sorted(glob.glob(os.path.join(RUNS, rd, att, "jobs", "*"))):
            out.append((lab, os.path.join(jd, "rows.jsonl.gz"), [os.path.join(jd, "harvest-rows.jsonl.gz")]))
    return out


def main():
    tally = collections.Counter()
    fails, j0_flag_mism = [], []
    j0_counts = {}
    bases_checked = 0
    for lab, rows_p, hps in sources():
        inst = {}
        for l in gzip.open(rows_p, "rt"):
            r = json.loads(l)
            if r.get("method") == "rho" or r.get("status") != "completed_valid" or not r.get("arm"):
                continue
            m = r.get("m") or (int(r["method"][4:]) if str(r.get("method", "")).startswith("ic_m") else None)
            inst[(r["bits"], r["curve"], m, r["arm"], r["mode"])] = r
        cache = {}
        for hp in hps:
            with gzip.open(hp, "rt") as f:
                for l in f:
                    h = json.loads(l)
                    if h["class"] not in ("TT", "TB") or h["arm"] == "known_log":
                        continue
                    k = (h["bits"], h["curve"], h["m"], h["arm"], h["mode"])
                    r = inst.get(k)
                    if r is None:
                        tally["row_without_instance"] += 1
                        continue
                    bk = (h["bits"], h["curve"], h["m"], h["arm"])
                    if bk not in cache:
                        pts = build_base(r)
                        comp = lam = None
                        if pts is not None and len(pts) != r["fb_size"]:
                            tally["base_size_mismatch"] += 1
                        if r.get("panel") == "j0" and pts:
                            comp, lam, err = j0_structure(pts, r["p"], r["N"], r["a"])
                            if err:
                                tally["j0_lambda_fail"] += 1
                        cache[bk] = (pts, comp)
                        bases_checked += 1
                    pts, comp = cache[bk]
                    if pts is None:
                        tally["no_base"] += 1
                        continue
                    S = None
                    for i, c in h["coeffs"]:
                        S = add(S, mul(c, pts[i], r["a"], r["p"]), r["a"], r["p"])
                    ok = S is None and h["kcoef"] == 0 and h["rhs"] == 0
                    tally[f"{h['class']}|{'ok' if ok else 'FAIL'}"] += 1
                    if not ok and len(fails) < 20:
                        fails.append([lab, k, h["class"]])
                    if comp is not None:
                        res = residual(h["coeffs"], comp, r["N"])
                        rf = (len(res) == 0)
                        if rf != bool(h["formal"]):
                            j0_flag_mism.append([lab, k, h["class"]])
                        jc = j0_counts.setdefault(k, {"TT_groups": collections.defaultdict(list), "TB_rows": 0, "TB_formal": 0})
                        if h["class"] == "TB":
                            jc["TB_rows"] += 1
                            jc["TB_formal"] += rf
                        else:
                            jc["TT_groups"][json.dumps(h["elements"][0], sort_keys=True)].append(res)
        rl.log(rows_p, f"cert_bases: rows + harvest rows of this source read ({lab})")
    # j0 recount of pairs_formal / pairs_nonformal vs recorded
    rows14 = {}
    for l in gzip.open(os.path.join(RUNS, "RUN-PFDR-1b78f7-j0", "rows.jsonl.gz"), "rt"):
        r = json.loads(l)
        if r.get("method") != "rho":
            rows14[(r["bits"], r["curve"], 3, r["arm"], r["mode"])] = r
    j0_cmp = collections.Counter()
    j0_diff = []
    for k, jc in j0_counts.items():
        r = rows14[k]
        st = r["harvest"]
        tb_nf = jc["TB_rows"] - jc["TB_formal"]
        ok_tb = (jc["TB_formal"] == st["TB"]["at_stop"]["pairs_formal"] and tb_nf == st["TB"]["at_stop"]["pairs_nonformal"])
        tt_formal = 0
        for g, reslist in jc["TT_groups"].items():
            cl = collections.Counter([()] + reslist)
            tt_formal += sum(v * (v - 1) // 2 for v in cl.values())
        ok_tt = tt_formal == st["TT"]["at_stop"]["pairs_formal"]
        j0_cmp[f"TB_formal_nonformal_{'ok' if ok_tb else 'DIFF'}"] += 1
        j0_cmp[f"TT_pairs_formal_{'ok' if ok_tt else 'DIFF'}"] += 1
        if not (ok_tb and ok_tt) and len(j0_diff) < 20:
            j0_diff.append([list(k), jc["TB_formal"], st["TB"]["at_stop"]["pairs_formal"], tt_formal, st["TT"]["at_stop"]["pairs_formal"]])
    out = {"row_certificates": dict(tally), "failures_first": fails, "bases_reconstructed": bases_checked,
           "j0_formal_flag_mismatches": len(j0_flag_mism), "j0_flag_mismatch_first": j0_flag_mism[:20],
           "j0_pair_recount": dict(j0_cmp), "j0_pair_recount_diffs": j0_diff}
    json.dump(out, open(os.path.join(W, "checks/out/cert-bases.json"), "w"), indent=1, default=str)
    print(json.dumps(out, default=str)[:3000])


if __name__ == "__main__":
    main()
