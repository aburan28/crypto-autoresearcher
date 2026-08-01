# EXP-INC-001 executor — candidate A2: output-sensitive finite-field incidence
# reporting for EC chord harvesting (m=3) vs exact enumeration.
#   enum    : exact enumerator baseline, Theta(B^2) pair tests (1 EC add + 1 x-hash lookup each)
#   r1      : dual range-searching reporter, grid-bucketing (g=ceil(sqrt(B)) x-interval buckets)
#   r2      : algebraic partition variant, cell key int(x^2-y) mod 9
#   r1_rand : NEGATIVE CONTROL — r1 on random non-EC point sets (determinant collinearity test)
# Positive control: r1/r2 triple multiset must equal enum exactly; witnesses verified by EC addition.
# Primary op unit: candidate pair test; setup/visit/hit ops counted separately (deterministic;
# wall time secondary). Frozen protocol: experiments/EXP-INC-001/specification.yaml.
import time, json, sys, math

SEEDS  = [20260717, 20260718, 20260719, 20260720, 20260721, 20260722]
PRIMES = [211, 1009, 4099]
FRACS  = [(1, 4), (1, 3), (2, 5)]     # B ~ n^(num/den)
B_MIN  = 8                            # target-family exclusion: tiny FB (B < 8)
T_MOD  = 9                            # algebraic partition modulus (r2)

def find_curve(p):
    # deterministic scan; first curve with prime #E(F_p) (prime order => ordinary, p>3)
    F = GF(p); cnt = 0
    while cnt < 20000:
        cnt += 1
        a = F(cnt % p); b = F((7*cnt + 3) % p)
        if 4*a**3 + 27*b**2 == 0: continue
        E = EllipticCurve(F, [a, b]); n = E.order()
        if is_prime(n): return E, int(n), [int(a), int(b)]
    raise RuntimeError("no prime-order curve found for p=%d" % p)

def make_fb(E, B, seed):
    F = E.base_field(); p = int(F.characteristic())
    set_random_seed(seed)
    pts = []; seen = set()
    while len(pts) < B:
        x = randint(0, p-1)
        if x in seen: continue
        try: P = E.lift_x(F(x))
        except Exception: continue
        if P.is_zero(): continue
        seen.add(x); pts.append(P)
    return pts

def make_rand_pts(p, B, seed):
    # negative-control point set: distinct uniform x, independent uniform y, NOT on any curve
    set_random_seed(seed)
    pts = []; seen = set()
    while len(pts) < B:
        x = randint(0, p-1)
        if x in seen: continue
        y = randint(0, p-1)
        seen.add(x); pts.append((int(x), int(y)))
    return pts

def _cells(P, p, mode):
    # returns (cell list [(key,[indices]),...], structure_pairs_scanned)
    B = len(P)
    if mode == "enum":
        return [(0, list(range(B)))], 1
    if mode == "r1":
        g = int(math.ceil(math.sqrt(B))); d = {}
        for i in range(B):
            b = (int(P[i].xy()[0]) * g) // p
            d.setdefault(b, []).append(i)
        return sorted(d.items()), g*(g+1)//2
    if mode == "r2":
        d = {}
        for i in range(B):
            x, y = P[i].xy()
            d.setdefault(int(x*x - y) % T_MOD, []).append(i)
        return sorted(d.items()), T_MOD*(T_MOD+1)//2
    raise ValueError(mode)

def run_ec(P, p, mode):
    # enum / r1 / r2 on EC points. Identical pair body: 1 EC add + 1 x-hash lookup.
    t0 = time.time()
    B = len(P)
    xidx = {}; setup = 0
    for i in range(B):
        xidx.setdefault(P[i].xy()[0], []).append(i); setup += 1     # x-index insert
    cells, visits = _cells(P, p, mode)
    setup += B if mode != "enum" else 0                             # bucketing inserts
    tests = 0; hits = 0; triples = set(); lines = {}
    nc = len(cells)
    for c1 in range(nc):
        L1 = cells[c1][1]
        for c2 in range(c1, nc):
            L2 = cells[c2][1]
            for i in L1:
                Pi = P[i]
                for j in L2:
                    if c1 == c2 and j <= i: continue
                    tests += 1
                    R = -(Pi + P[j])                                # pair test: EC add
                    if R.is_zero(): continue
                    ks = xidx.get(R.xy()[0])                        # x-hash lookup
                    if not ks: continue
                    for k in ks:
                        if k == i or k == j: continue
                        hits += 1
                        t = (i, j, k) if i < j else (j, i, k)
                        t = tuple(sorted(t))
                        if t in triples: continue
                        triples.add(t)
                        x1, y1 = P[t[0]].xy(); x2, y2 = P[t[1]].xy()
                        m = (y2 - y1)/(x2 - x1); c = y1 - m*x1      # line key (hit-only)
                        lines.setdefault((m, c), set()).update(t)
    wall = time.time() - t0
    # witness verification by exact EC addition
    verified = 0
    for (i, j, k) in triples:
        if (P[i] + P[j] + P[k]).is_zero(): verified += 1
    rich = [s for s in lines.values() if len(s) >= 3]
    return {"setup_ops": setup, "structure_pairs": visits, "candidate_tests": tests,
            "hit_ops": hits, "total_ops": setup + visits + tests + hits,
            "avoided_pairs": (B*(B-1))//2 - tests, "wall_s": wall,
            "triples": triples, "verified": verified,
            "rich_lines": len(rich), "incidences": sum(len(s) for s in rich),
            "max_richness": max((len(s) for s in rich), default=0)}

def run_rand(pts, p):
    # NEGATIVE CONTROL: r1-style bucketing on random non-EC points; per-pair test =
    # (B-2) determinant collinearity tests (no group-law third-point oracle exists).
    t0 = time.time()
    B = len(pts); g = int(math.ceil(math.sqrt(B))); d = {}
    setup = 0
    for i in range(B):
        b = (pts[i][0] * g) // p
        d.setdefault(b, []).append(i); setup += 1
    visits = g*(g+1)//2
    tests = 0; prim = 0; triples = set()
    keys = sorted(d); nc = len(keys)
    for c1 in range(nc):
        L1 = d[keys[c1]]
        for c2 in range(c1, nc):
            L2 = d[keys[c2]]
            for i in L1:
                x1, y1 = pts[i]
                for j in L2:
                    if c1 == c2 and j <= i: continue
                    tests += 1
                    x2, y2 = pts[j]; dx = x2 - x1; dy = y2 - y1
                    for k in range(B):
                        if k == i or k == j: continue
                        prim += 1
                        if (dy*(pts[k][0]-x1) - (pts[k][1]-y1)*dx) % p == 0:
                            triples.add(tuple(sorted((i, j, k))))
    wall = time.time() - t0
    return {"setup_ops": setup, "structure_pairs": visits, "candidate_tests": tests,
            "prim_tests": prim, "total_ops": setup + visits + tests + prim,
            "avoided_pairs": (B*(B-1))//2 - tests, "wall_s": wall,
            "n_triples": len(triples)}

def slope(xs, ys):
    n = len(xs)
    if n < 2: return None
    mx = sum(xs)/n; my = sum(ys)/n
    den = sum((x-mx)**2 for x in xs)
    if den == 0: return None
    return sum((x-mx)*(y-my) for x, y in zip(xs, ys))/den

def C3(B): return B*(B-1)*(B-2)//6

def main():
    t_start = time.time()
    out = {"experiment": "EXP-INC-001", "seeds": SEEDS, "primes": PRIMES,
           "B_min": B_MIN, "T_mod": T_MOD, "instances": [], "rows": []}
    pos_checked = 0; pos_mismatch = 0; neg_avoid_ec = 0; neg_avoid_rand = 0
    I_ec_tot = 0; I_rand_tot = 0; I_pred_tot = 0.0
    for p in PRIMES:
        E, n, ab = find_curve(p)
        grid = {}
        for (num, den) in FRACS:
            Bf = float(n) ** (num/den)
            B = int(math.floor(Bf + 0.5))
            grid["n^(%d/%d)" % (num, den)] = {"B_float": Bf, "B": B, "excluded": B < B_MIN}
        out["instances"].append({"p": p, "n": n, "curve_ab": ab, "B_grid": grid})
        print("p=%d n=%d E=[%d,%d] grid=%s" % (p, n, ab[0], ab[1],
              {k: (v["B"], "EXCLUDED" if v["excluded"] else "ok") for k, v in grid.items()}),
              file=sys.stderr, flush=True)
        for frac_name, ginfo in grid.items():
            if ginfo["excluded"]: continue
            B = ginfo["B"]
            for seed in SEEDS:
                FB = make_fb(E, B, seed)
                assert len(FB) == B
                r_enum = run_ec(FB, p, "enum")
                r_r1   = run_ec(FB, p, "r1")
                r_r2   = run_ec(FB, p, "r2")
                RP = make_rand_pts(p, B, seed)
                r_rand = run_rand(RP, p)
                # POSITIVE CONTROL: exact multiset equality + EC witness verification
                match = (r_enum["triples"] == r_r1["triples"] == r_r2["triples"])
                ver_ok = (r_enum["verified"] == len(r_enum["triples"]) ==
                          r_r1["verified"] == r_r2["verified"])
                pos_checked += 1
                if not (match and ver_ok): pos_mismatch += 1
                # NEGATIVE CONTROL tallies
                neg_avoid_ec   += r_r1["avoided_pairs"]
                neg_avoid_rand += r_rand["avoided_pairs"]
                I = len(r_enum["triples"])
                I_ec_tot += I; I_rand_tot += r_rand["n_triples"]
                I_pred = C3(B)/float(n); I_pred_tot += I_pred
                row = {"p": p, "n": n, "frac": frac_name, "B": B, "seed": seed, "I": I,
                       "I_pred": I_pred, "I_rand": r_rand["n_triples"],
                       "rich_lines": r_enum["rich_lines"],
                       "incidences": r_enum["incidences"],
                       "max_richness": r_enum["max_richness"],
                       "enum": {k: v for k, v in r_enum.items() if k != "triples"},
                       "r1":   {k: v for k, v in r_r1.items()   if k != "triples"},
                       "r2":   {k: v for k, v in r_r2.items()   if k != "triples"},
                       "rand": r_rand,
                       "control_match": bool(match and ver_ok)}
                out["rows"].append(row)
                print("  p=%d B=%d(%s) seed=%d I=%d (pred %.3f, rand %d) match=%s "
                      "tests e/r1/r2=%d/%d/%d" %
                      (p, B, frac_name, seed, I, I_pred, r_rand["n_triples"], match,
                       r_enum["candidate_tests"], r_r1["candidate_tests"],
                       r_r2["candidate_tests"]), file=sys.stderr, flush=True)
    # ---- aggregation: seed means per (p, frac, B) ----
    agg = {}
    for r in out["rows"]:
        agg.setdefault((r["p"], r["frac"], r["B"], r["n"]), []).append(r)
    means = []
    for (p, frac, B, n), rs in sorted(agg.items()):
        def m(path):
            vals = []
            for r in rs:
                v = r
                for k in path: v = v[k]
                vals.append(float(v))
            return sum(vals)/len(vals)
        means.append({"p": p, "n": n, "frac": frac, "B": B, "seeds": len(rs),
                      "I_mean": m(["I"]), "I_pred": m(["I_pred"]), "I_rand_mean": m(["I_rand"]),
                      "enum_total": m(["enum", "total_ops"]), "r1_total": m(["r1", "total_ops"]),
                      "r2_total": m(["r2", "total_ops"]),
                      "r1_setup": m(["r1", "setup_ops"]) + m(["r1", "structure_pairs"]),
                      "enum_tests": m(["enum", "candidate_tests"]),
                      "r1_tests": m(["r1", "candidate_tests"]),
                      "r1_nonsetup": m(["r1", "candidate_tests"]) + m(["r1", "hit_ops"]),
                      "enum_wall": m(["enum", "wall_s"]), "r1_wall": m(["r1", "wall_s"])})
    out["seed_means"] = means
    # ---- exponent fits (log2, least squares) ----
    def fit(key):
        xs = [math.log(r["B"], 2) for r in means]
        ys = [math.log(r[key], 2) for r in means]
        return slope(xs, ys)
    fits = {"alpha2_enum": fit("enum_total"), "alpha2_r1": fit("r1_total"),
            "alpha2_r2": fit("r2_total"), "output_vs_B": None}
    xsB = [math.log(r["B"], 2) for r in means if r["I_mean"] > 0]
    ysI = [math.log(r["I_mean"], 2) for r in means if r["I_mean"] > 0]
    fits["output_vs_B"] = slope(xsB, ysI)
    # complete-cost trend along each surviving grid row with >= 2 sizes
    trends = {}
    for frac in set(r["frac"] for r in means):
        rs = [r for r in means if r["frac"] == frac]
        if len(rs) < 2: continue
        xn = [math.log(r["n"], 2) for r in rs]
        trends[frac] = {"sizes": len(rs),
                        "trend_enum": slope(xn, [math.log(r["enum_total"], 2) for r in rs]),
                        "trend_r1": slope(xn, [math.log(r["r1_total"], 2) for r in rs])}
    fits["trends_by_row"] = trends
    out["fits"] = fits
    # ---- gate arithmetic ----
    gate = {"alpha2_threshold": 1.5, "alpha2_enum": fits["alpha2_enum"],
            "alpha2_r1": fits["alpha2_r1"], "alpha2_r2": fits["alpha2_r2"],
            "setup_ratio_r1_over_B2": [{"p": r["p"], "B": r["B"],
                                        "ratio": r["r1_setup"]/(r["B"]**2)} for r in means],
            "complete_cost_trends": trends, "trend_threshold": 0.49,
            "floor_2_3": 2/3, "charged_ratios": []}
    for r in means:
        gate["charged_ratios"].append(
            {"p": r["p"], "frac": r["frac"], "B": r["B"],
             "r1_total_over_0.886_sqrt_n": r["r1_total"]/(0.886*math.sqrt(r["n"])),
             "r1_total_over_n_pow_2_3": r["r1_total"]/(r["n"]**(2/3)),
             "enum_total_over_0.886_sqrt_n": r["enum_total"]/(0.886*math.sqrt(r["n"]))})
    out["gate_arithmetic"] = gate
    # ---- controls + validity ----
    neg_pass = (neg_avoid_rand <= neg_avoid_ec)
    out["controls"] = {
        "positive": {"instances_checked": pos_checked, "mismatches": pos_mismatch,
                     "pass": pos_mismatch == 0},
        "negative": {"avoided_pairs_ec_r1_total": neg_avoid_ec,
                     "avoided_pairs_rand_total": neg_avoid_rand,
                     "criterion": "avoided_pairs(rand) <= avoided_pairs(EC)",
                     "pass": bool(neg_pass),
                     "I_ec_total": I_ec_tot, "I_rand_total": I_rand_tot,
                     "I_pred_total": I_pred_tot}}
    valid = (pos_mismatch == 0) and neg_pass and len(out["rows"]) >= 3*len(SEEDS)
    out["validity"] = {"status": "valid" if valid else "invalid",
                       "reason": ("positive control exact on %d instances; negative control "
                                  "passes (random not reported more cheaply: %d <= %d avoided); "
                                  "%d rows" % (pos_checked, neg_avoid_rand, neg_avoid_ec,
                                               len(out["rows"]))) if valid else
                                 "control failure — see controls block"}
    out["wall_seconds_total"] = time.time() - t_start
    def _ser(o):
        try: return int(o)
        except Exception:
            try: return float(o)
            except Exception: return str(o)
    print(json.dumps(out, default=_ser))

main()
