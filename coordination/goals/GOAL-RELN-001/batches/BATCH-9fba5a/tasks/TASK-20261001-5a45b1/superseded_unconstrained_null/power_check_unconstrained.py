"""NON-PROTOCOL power and proves-too-much check for EXP-RELN-dc761f.

Label: NON-PROTOCOL. Synthetic graphs only, numpy PCG64 seeded from the string
'TASK-20261001-5a45b1|non-protocol|power-check'. No curve arithmetic, no
attempt, no SHA256 protocol label, and no draw from the honest generator's
law: the H0 graphs come from an independent-edge surrogate whose parameters
(n_lp, 1-LP share, edge counts) are fixture counts and the already-committed
RUN-RELN-a695fe outcome counts.

What it checks, for the contract's primary test (rule S-1..S-5):
  * statistic C34 = C3 + C4: multiplicity-weighted count of cycles of length
    3 and 4 on distinct vertices (loops excluded), via trace formulas,
    unit-checked against brute force;
  * null: pure configuration-model rewire of the stub list (R replicates);
  * pooled one-sided Monte Carlo test over the 18 primary cells
    (9 fixtures x kappa in {1, 2}) and the ENRICHED / NULL-MATCHED rule;
  * conditions: H0 surrogate (false-positive rate), CM pseudo-treatment,
    spanning forest (known false), degree-preserving planted enrichment at
    factors 1.25 / 1.5 / 2.0 (power);
  * certified-subcritical reachability on the H0 surrogate at kappa 1/4, 1/2
    for 20, 24 and 28 bits;
  * noise calibration: the surrogate's cycle-rank excess over rewire at the
    v4 A2 edge counts, in v4 delta units, against RUN-RELN-a695fe's
    0.033 +- 0.028.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
import time

import numpy as np
from fractions import Fraction

SEED_STR = "TASK-20261001-5a45b1|non-protocol|power-check"
rng = np.random.default_rng(int.from_bytes(hashlib.sha256(SEED_STR.encode()).digest()[:8], "big"))

ALPHA = 0.01          # S-4 enrichment level
R_EFF_MIN = 1.25      # S-4 minimum effect (pooled ratio)
Z_UP = 1.6448536269514722

# ---------------------------------------------------------------- statistic


def weight_matrix(n: int, edges: np.ndarray) -> np.ndarray:
    A = np.zeros((n, n), dtype=np.float64)
    if len(edges):
        u, v = edges[:, 0], edges[:, 1]
        off = u != v
        np.add.at(A, (u[off], v[off]), 1.0)
        np.add.at(A, (v[off], u[off]), 1.0)
    return A


def c34_sparse(n: int, edges: np.ndarray) -> tuple[int, int]:
    from scipy import sparse
    u, v = edges[:, 0], edges[:, 1]
    off = u != v
    rows = np.concatenate([u[off], v[off]])
    cols = np.concatenate([v[off], u[off]])
    A = sparse.coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n)).tocsr()
    A.sum_duplicates()
    A2 = (A @ A).tocsr()
    c3 = float(A2.multiply(A).sum()) / 6.0
    tr4 = float(A2.multiply(A2).sum())
    Asq = A.multiply(A)
    s = np.asarray(Asq.sum(axis=1)).ravel()
    q4 = float(Asq.multiply(Asq).sum())
    c4 = (tr4 - 2.0 * float((s * s).sum()) + q4) / 8.0
    return int(round(c3)), int(round(c4))


def c34(n: int, edges: np.ndarray) -> tuple[int, int]:
    """(C3, C4): multiplicity-weighted vertex-distinct 3- and 4-cycles."""
    if n > 150 and len(edges):
        return c34_sparse(n, edges)
    A = weight_matrix(n, edges)
    A2 = A @ A
    c3 = float(np.einsum("ij,ji->", A2, A)) / 6.0
    tr4 = float(np.einsum("ij,ji->", A2, A2))
    s = (A * A).sum(axis=1)
    q4 = float((A ** 4).sum())
    c4 = (tr4 - 2.0 * float((s * s).sum()) + q4) / 8.0
    return int(round(c3)), int(round(c4))


def brute_c34(n: int, edges) -> tuple[int, int]:
    mult = {}
    for u, v in edges:
        if u != v:
            k = (min(u, v), max(u, v))
            mult[k] = mult.get(k, 0) + 1
    m = lambda a, b: mult.get((min(a, b), max(a, b)), 0)
    c3 = sum(m(a, b) * m(b, c) * m(a, c) for a, b, c in itertools.combinations(range(n), 3))
    c4 = 0
    for quad in itertools.combinations(range(n), 4):
        a = quad[0]
        for b, c, d in itertools.permutations(quad[1:]):
            if b < d:  # each 4-cycle a-b-c-d-a once (fix a, orientation)
                c4 += m(a, b) * m(b, c) * m(c, d) * m(d, a)
    return c3, c4


def unit_check():
    for t in range(200):
        n = int(rng.integers(3, 9))
        mm = int(rng.integers(0, 16))
        e = rng.integers(0, n, size=(mm, 2))
        assert c34(n, e) == brute_c34(n, e.tolist()), (n, e.tolist())
        if mm:
            assert c34_sparse(n, e) == brute_c34(n, e.tolist())
    return ("200/200 random multigraphs (n 3..8, loops and parallel edges): dense and sparse "
            "trace formulas match brute force")


# ---------------------------------------------------------------- graphs


def relabel_touched(edges: np.ndarray) -> tuple[int, np.ndarray]:
    """Root 0 always kept; LP vertices kept iff incident to an edge (v4 OQ-6 / rule G-7)."""
    lp = np.unique(edges[edges > 0]) if len(edges) else np.array([], dtype=int)
    mp = {0: 0}
    for i, x in enumerate(lp.tolist()):
        mp[x] = i + 1
    f = np.vectorize(mp.get)
    return len(lp) + 1, f(edges) if len(edges) else edges


def h0_graph(n_lp: int, s1: float, m: int) -> tuple[int, np.ndarray]:
    """Independent-edge surrogate: 1-LP edge (u, root) w.p. s1, else uniform LP pair."""
    is1 = rng.random(m) < s1
    u = rng.integers(1, n_lp + 1, size=m)
    v = rng.integers(1, n_lp + 1, size=m)
    v[is1] = 0
    return relabel_touched(np.stack([u, v], axis=1))


def cm_rewire(edges: np.ndarray) -> np.ndarray:
    stubs = edges.reshape(-1).copy()
    rng.shuffle(stubs)
    return stubs.reshape(-1, 2)


def cycle_rank(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges.tolist():
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    comps = {}
    for x in range(n):
        comps.setdefault(find(x), []).append(x)
    c = len(comps)
    e_in = {}
    for a, _ in edges.tolist():
        r = find(a)
        e_in[r] = e_in.get(r, 0) + 1
    cwc = sum(1 for r, vs in comps.items() if e_in.get(r, 0) - len(vs) + 1 > 0)
    giant = max(len(vs) for vs in comps.values())
    return len(edges) - n + c, c, cwc, giant


def spanning_forest(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    keep = []
    for a, b in edges.tolist():
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            keep.append((a, b))
    return np.array(keep, dtype=int).reshape(-1, 2)


def plant(n: int, edges: np.ndarray, target: int, max_moves: int = 4000) -> tuple[np.ndarray, int]:
    """Degree-preserving triadic closure: pick a path a-b-c and edges (a,x), (c,y)
    disjoint from it; replace them with (a,c), (x,y). Accept iff C34 rises.
    Stops when C34 >= target. Returns (edges, final C34)."""
    e = edges.copy()
    cur = sum(c34(n, e))
    moves = 0
    while cur < target and moves < max_moves:
        moves += 1
        m = len(e)
        i, j = rng.integers(0, m, size=2)
        if i == j:
            continue
        (p0, p1), (r0, r1) = e[i], e[j]
        # orient to share vertex b
        cand = [(p0, p1, r0, r1), (p1, p0, r0, r1), (p0, p1, r1, r0), (p1, p0, r1, r0)]
        ok = [(a, b, c) for a, b, b2, c in cand if b == b2 and len({a, b, c}) == 3]
        if not ok:
            continue
        a, b, c = ok[0]
        inc_a = [k for k in np.nonzero((e == a).any(axis=1))[0] if k not in (i, j)]
        inc_c = [k for k in np.nonzero((e == c).any(axis=1))[0] if k not in (i, j)]
        if not inc_a or not inc_c:
            continue
        ka, kc = int(rng.choice(inc_a)), int(rng.choice(inc_c))
        if ka == kc:
            continue
        x = e[ka][1] if e[ka][0] == a else e[ka][0]
        y = e[kc][1] if e[kc][0] == c else e[kc][0]
        new = e.copy()
        new[ka] = (a, c)
        new[kc] = (x, y)
        val = sum(c34(n, new))
        if val > cur:
            e, cur = new, val
    return e, cur


# ---------------------------------------------------------------- fixtures (noise level of RUN-RELN-a695fe)
# n_lp and y_edge-derived budgets: exact_yield_budgets_out.json (label-free);
# 1-LP share: committed RUN-RELN-a695fe A2 outcome counts lp1/(lp1+lp2).
RUN_A2 = {  # fixture: (lp1, lp2, A2 attempts)
    "b16-s11": (15, 32), "b16-s12": (2, 27), "b16-s13": (7, 21),
    "b20-s11": (10, 88), "b20-s12": (16, 85), "b20-s13": (25, 124),
    "b24-s11": (25, 327), "b24-s12": (20, 327), "b24-s13": (20, 341),
}


def load_fixtures(path, with28=False):
    rows = json.load(open(path))["rows"]
    out = []
    for r in rows:
        lp1, lp2 = RUN_A2[r["fixture_id"]]
        out.append({"id": r["fixture_id"], "n_lp": r["n_lp"], "s1": lp1 / (lp1 + lp2),
                    "E_A2_run": lp1 + lp2,
                    "edges": {k: int(round(v["expected_edges"])) for k, v in r["budgets"].items()}})
    if with28:
        # 28-bit fixtures are not yet derived (rule F-2); surrogate sizes estimated:
        # n_lp ~ p^{2/5}/2 in [890, 1180], 1-LP share ~ 2 L / n_lp ~ 0.048.
        for i, nlp in enumerate((950, 1000, 1100)):
            out.append({"id": f"b28-est{i}", "n_lp": nlp, "s1": 0.048, "E_A2_run": None,
                        "edges": {k: round(float(Fraction(k)) * (nlp + 1)) for k in ("1/4", "1/2", "1", "2")}})
    return out


# ---------------------------------------------------------------- pooled test


def pooled_test(obs_cells, null_cells):
    """obs_cells: list of C34 values; null_cells: list of arrays (R,) aligned by replicate."""
    T = float(sum(obs_cells))
    Tn = np.sum(np.stack(null_cells), axis=0)
    R = len(Tn)
    p_up = (1 + int((Tn >= T).sum())) / (R + 1)
    p_lo = (1 + int((Tn <= T).sum())) / (R + 1)
    mu, sd = float(Tn.mean()), float(Tn.std(ddof=1))
    r = T / mu if mu > 0 else float("nan")
    r_up = (T + Z_UP * sd) / mu if mu > 0 else float("nan")
    if p_up < ALPHA and r >= R_EFF_MIN:
        verdict = "ENRICHED"
    elif r_up < R_EFF_MIN and p_up >= 0.05:
        verdict = "NULL_MATCHED"
    else:
        verdict = "INCONCLUSIVE"
    return {"T": T, "mu": mu, "sd": sd, "r": r, "r_up": r_up, "p_up": p_up, "p_lo": p_lo,
            "verdict": verdict}


def one_experiment(fixtures, R, conditions):
    """Build 18 primary cells (kappa 1, 2) and evaluate every condition on them."""
    obs = {c: [] for c in conditions}
    nulls, nulls_forest = [], []
    plant_info = []
    for fx in fixtures:
        for kap in ("1", "2"):
            m = fx["edges"][kap]
            n, e = h0_graph(fx["n_lp"], fx["s1"], m)
            null = np.array([sum(c34(n, cm_rewire(e))) for _ in range(R)], dtype=float)
            nulls.append(null)
            mu = float(null.mean())
            base = sum(c34(n, e))
            if "H0" in obs:
                obs["H0"].append(base)
            if "CM_pseudo" in obs:
                obs["CM_pseudo"].append(sum(c34(n, cm_rewire(e))))
            for f in (1.25, 1.5, 2.0):
                key = f"planted_{f}"
                if key in obs:
                    tgt = max(base, math.ceil(f * mu))
                    _, val = plant(n, e, tgt)
                    obs[key].append(val)
                    plant_info.append((fx["id"], kap, f, mu, base, tgt, val))
            if "forest" in obs:
                fe = spanning_forest(n, e)
                obs["forest"].append(sum(c34(n, fe)))
                # forest null: CM on forest stubs, smaller R (it cannot exceed T=0 test anyway)
                nulls_forest.append(np.array([sum(c34(n, cm_rewire(fe))) for _ in range(R)], dtype=float))
    res = {}
    for c in conditions:
        res[c] = pooled_test(obs[c], nulls_forest if c == "forest" else nulls)
    return res, plant_info


# ---------------------------------------------------------------- subcritical reachability


def certificate_reachability(n_lp, s1, kappas, reps):
    out = {}
    for kap in kappas:
        m = max(1, round(kap * (n_lp + 1)))
        hits, eligible, gfr = 0, 0, []
        for _ in range(reps):
            n, e = h0_graph(n_lp, s1, m)
            cr, c, cwc, giant = cycle_rank(n, e)
            gf = giant / n
            gfr.append(gf)
            if n > 40:
                eligible += 1
                if gf < 0.05 and cr <= 2 * cwc:
                    hits += 1
        out[str(kap)] = {"edges": m, "eligible_frac": eligible / reps, "certified_frac": hits / reps,
                         "giant_frac_median": float(np.median(gfr)),
                         "giant_frac_p10_p90": [float(np.quantile(gfr, 0.1)), float(np.quantile(gfr, 0.9))]}
    return out


# ---------------------------------------------------------------- noise calibration


def noise_calibration(fixtures, reps, R):
    """Surrogate analogue of the red team's O-6 number at the v4 A2 edge counts:
    mean over fixtures of log_L(cr_obs / mean cr_rewire), L = v4 C-2 count."""
    L_v4 = {"b16-s11": 6, "b16-s12": 2, "b16-s13": 6, "b20-s11": 6, "b20-s12": 7, "b20-s13": 10,
            "b24-s11": 14, "b24-s12": 12, "b24-s13": 10}
    means = []
    for _ in range(reps):
        vals = []
        for fx in fixtures:
            if fx["E_A2_run"] is None:
                continue
            n, e = h0_graph(fx["n_lp"], fx["s1"], fx["E_A2_run"])
            cr = cycle_rank(n, e)[0]
            rw = np.mean([cycle_rank(n, cm_rewire(e))[0] for _ in range(R)])
            if cr > 0 and rw > 0:
                vals.append(math.log(cr / rw) / math.log(L_v4[fx["id"]]))
        means.append(float(np.mean(vals)))
    return {"reps": reps, "rewire_R": R, "mean_of_means": float(np.mean(means)),
            "sd_of_means": float(np.std(means, ddof=1)),
            "run_value": "0.033 +- 0.028 (s.e.), RUN-RELN-a695fe via TASK-20261001-ece593"}


def main():
    fx_path, out_path = sys.argv[1], sys.argv[2]
    n_exp = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    R = int(sys.argv[4]) if len(sys.argv) > 4 else 199
    with28 = len(sys.argv) > 5 and sys.argv[5] == "with28"
    t0 = time.time()
    out = {"label": "NON-PROTOCOL synthetic power / proves-too-much check", "seed_string": SEED_STR,
           "alpha": ALPHA, "min_effect_ratio": R_EFF_MIN, "replicates_R": R, "experiments_per_condition": n_exp}
    out["unit_check"] = unit_check()
    fixtures = load_fixtures(fx_path, with28)
    out["fixture_set"] = "9 v4 fixtures + 3 estimated 28-bit surrogates" if with28 else "9 v4 fixtures (16/20/24 bits)"
    out["fixtures_used"] = fixtures
    conds = ["H0", "CM_pseudo", "forest", "planted_1.25", "planted_1.5", "planted_2.0"]
    tally = {c: {"ENRICHED": 0, "NULL_MATCHED": 0, "INCONCLUSIVE": 0} for c in conds}
    ratios = {c: [] for c in conds}
    pvals = {c: [] for c in conds}
    plant_short = 0
    for k in range(n_exp):
        res, pinfo = one_experiment(fixtures, R, conds)
        for c in conds:
            tally[c][res[c]["verdict"]] += 1
            ratios[c].append(res[c]["r"])
            pvals[c].append(res[c]["p_up"])
        plant_short += sum(1 for row in pinfo if row[6] < row[5])
        print(f"exp {k+1}/{n_exp} {time.time()-t0:.0f}s", {c: res[c]["verdict"][:4] for c in conds}, flush=True)
    out["pooled_verdict_counts"] = tally
    out["pooled_ratio_summary"] = {c: {"median": float(np.median(ratios[c])),
                                       "p05_p95": [float(np.quantile(ratios[c], 0.05)), float(np.quantile(ratios[c], 0.95))]}
                                   for c in conds}
    out["frac_p_up_below_alpha"] = {c: float(np.mean(np.array(pvals[c]) < ALPHA)) for c in conds}
    out["planting_cells_short_of_target"] = plant_short
    out["certificate_reachability"] = {
        "b20_like": certificate_reachability(108, 0.14, [0.25, 0.5], 400),
        "b24_like": certificate_reachability(335, 0.065, [0.25, 0.5], 400),
        "b28_like_estimated": certificate_reachability(1000, 0.048, [0.25, 0.5], 200),
        "note": "n_lp, 1-LP share: 20/24-bit from fixture means; 28-bit estimated (n_lp ~ p^{2/5}/2, share ~ 2 L/n_lp).",
    }
    out["noise_calibration"] = noise_calibration(fixtures, 40, 32)
    out["wall_seconds"] = time.time() - t0
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("pooled_verdict_counts", "frac_p_up_below_alpha", "pooled_ratio_summary",
                                          "planting_cells_short_of_target", "certificate_reachability",
                                          "noise_calibration", "wall_seconds")}, indent=1))


if __name__ == "__main__":
    main()
