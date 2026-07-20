# EXP-TRA-001 (family TRA) -- candidate C1: transfer-operator (Ruelle/Koopman) spectral
# channel on the translation-by-P walk. Minimal falsifying experiment, frozen protocol:
#   p in {211, 1009, 4099}; C in {8, 32, 128}; S in {round(n^1/4), round(n^3/8)};
#   seeds 20260717..20260722; prime-order curves (#E = n prime).
# Deterministic: set_random_seed(seed) for Sage-side curve generation; numpy RandomState
# streams (seed, seed+1, seed+2, seed+3) for k draw, transition sampling, permutation control.
# Writes machine-readable results to runs/RUN-TRA-001-a/raw-repro.json.

import json
import platform
import subprocess
import sys
import time

import numpy as np

OUT_PATH = "experiments/EXP-TRA-001/runs/RUN-TRA-001-a/raw-repro.json"

PRIMES = [211, 1009, 4099]
CGRID = [8, 32, 128]
SEEDS = [20260717, 20260718, 20260719, 20260720, 20260721, 20260722]
S_SPECS = [("n^1/4", 0.25), ("n^3/8", 0.375)]


def git_info():
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        status = subprocess.check_output(["git", "status", "--porcelain"], text=True)
        return head, bool(status.strip())
    except Exception as e:
        return "unavailable: %s" % e, None


def xcell(R, C, p):
    if R.is_zero():
        return int(C)  # identity point: extra cell index C (x-interval cells are 0..C-1)
    x = int(R[0])
    c = (x * int(C)) // int(p)
    return min(int(C) - 1, c)


def build_cells(E, P, n_int, C, p):
    cells = [0] * n_int
    R = E(0)
    for r in range(n_int):
        cells[r] = xcell(R, C, p)
        R = R + P
    return cells


def normalize(counts, Cc):
    M = np.zeros((Cc, Cc), dtype=float)
    fill = 0
    for c in range(Cc):
        s = float(counts[c, :].sum())
        if s > 0:
            M[c, :] = counts[c, :] / s
            fill += 1
        else:
            M[c, :] = 1.0 / Cc  # unvisited row -> uniform (counted in fill)
    return M, fill


def estimate(M, cell_seq, n_int, k):
    """Core spectral localization estimator (see specification.yaml estimator_definition).
    cell_seq[t] = cell of the t-th point of the readout trajectory started at the target.
    Returns a JSON-native dict."""
    Cc = int(M.shape[0])
    vals, V = np.linalg.eig(M)
    valsT, W = np.linalg.eig(M.T)
    mags = sorted((float(abs(vv)) for vv in vals), reverse=True)[:8]
    mags = [float(m) for m in mags]
    cands = [j for j in range(len(vals))
             if abs(vals[j] - 1.0) > 1e-9 and vals[j].imag > 1e-9]
    if not cands:
        return {"informative": False,
                "reason": "no non-stationary eigenvalue with positive imaginary part",
                "top_eig_mags": mags, "count": n_int, "L": 1.0, "hit": True,
                "L_eff": 1.0, "chance": 1.0}
    maxmag = max(float(abs(vals[j])) for j in cands)
    top = [j for j in cands if abs(float(abs(vals[j])) - maxmag) <= 1e-9 * max(1.0, maxmag)]
    pick = min(top, key=lambda j: float(np.angle(vals[j])))
    lam = vals[pick]
    v = V[:, pick]
    i = int(np.argmin(np.abs(valsT - lam)))
    w = W[:, i]
    res_r = float(np.max(np.abs(M.dot(v) - lam * v)))
    res_l = float(np.max(np.abs(w.dot(M) - lam * w)))
    ip = np.dot(w, v)
    if abs(ip) < 1e-12:
        return {"informative": False, "reason": "degenerate left/right eigenpair",
                "top_eig_mags": mags, "count": n_int, "L": 1.0, "hit": True,
                "L_eff": 1.0, "chance": 1.0}
    w = w / ip  # now w . v = 1 (complex bilinear, no conjugation)
    # gauge fix: v[c_ref] real positive
    c_ref = 0 if abs(v[0]) > 1e-12 else int(np.argmax(np.abs(v)))
    alpha = float(np.angle(v[c_ref]))
    v = v * np.exp(-1j * alpha)
    w = w * np.exp(1j * alpha)
    phi = float(np.angle(lam) / (2.0 * np.pi))  # in (0, 0.5]
    T = len(cell_seq)
    kern = np.exp(-2j * np.pi * phi * np.arange(T, dtype=float))
    Avec = np.zeros(Cc, dtype=complex)
    for t in range(T):
        Avec[int(cell_seq[t])] += kern[t]
    denom = float(np.sum(np.abs(w) ** 2))
    A = complex(np.sum(np.conj(w) * Avec))
    if denom < 1e-12 or abs(A) < 1e-12:
        return {"informative": False, "reason": "vanishing readout amplitude",
                "top_eig_mags": mags, "phi": phi, "lam_abs": float(abs(lam)),
                "count": n_int, "L": 1.0, "hit": True, "L_eff": 1.0, "chance": 1.0}
    A = A / denom
    psi = float(np.angle(A) % (2.0 * np.pi))
    k_real = psi / (2.0 * np.pi * phi)
    w_step = max(1, int(round(1.0 / phi)))
    w_step = min(w_step, n_int)
    base = int(round(k_real)) % w_step
    count = (n_int - 1 - base) // w_step + 1
    L = float(n_int) / float(count)
    hit = bool((k % w_step) == base)
    return {"informative": True,
            "lam_re": float(lam.real), "lam_im": float(lam.imag),
            "lam_abs": float(abs(lam)), "phi": phi, "top_eig_mags": mags,
            "res_r": res_r, "res_l": res_l,
            "A_abs": float(abs(A)), "denom": denom, "c_ref": int(c_ref),
            "psi": psi, "k_real": float(k_real),
            "w_step": int(w_step), "base": int(base), "count": int(count),
            "L": float(L), "hit": hit,
            "L_eff": float(L if hit else 1.0), "chance": float(1.0 / L)}


def mean(xs):
    xs = list(xs)
    return float(sum(xs) / len(xs)) if xs else None


t0 = time.time()
started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
head, dirty = git_info()

instances = []
configs = []       # main EC grid (charged, S sampled transitions, T = S readout)
exact_rows = []    # exact-coarse oracle diagnostic (M_exact, T = n)
neg_ctrl = []      # random permutation operators, same grid
pos_ctrl = []      # full-resolution C = n control

for p in PRIMES:
    F = GF(p)
    for seed in SEEDS:
        # --- instance: prime-order curve, generator P, hidden k, Q = kP ---
        set_random_seed(seed)
        tries = 0
        while True:
            a = F.random_element()
            b = F.random_element()
            tries += 1
            if (4 * a ** 3 + 27 * b ** 2).is_zero():
                continue
            E = EllipticCurve(F, [a, b])
            n = ZZ(E.order())
            if n.is_prime():
                break
        n_int = int(n)
        P = E.gens()[0]
        rs_k = np.random.RandomState(int(seed))
        k = int(1 + rs_k.randint(n_int - 1))  # k in [1, n-1]
        Q = k * P
        instances.append({
            "p": int(p), "seed": int(seed), "a": str(a), "b": str(b),
            "n": n_int, "P": [str(P[0]), str(P[1])],
            "k": int(k), "Q": [str(Q[0]), str(Q[1])],
            "curve_gen_tries": int(tries)})

        # --- main grid ---
        for C in CGRID:
            Cc = C + 1
            cells = build_cells(E, P, n_int, C, p)
            # exact coarse matrix (oracle diagnostic, S -> infinity limit)
            cnt = np.zeros((Cc, Cc))
            for r in range(n_int):
                cnt[cells[r], cells[(r + 1) % n_int]] += 1.0
            M_exact, fill_exact = normalize(cnt, Cc)
            seq_full = [cells[(k + t) % n_int] for t in range(n_int)]
            res_ex = estimate(M_exact, seq_full, n_int, k)
            res_ex.update({"p": int(p), "seed": int(seed), "C": int(C),
                           "T": n_int, "fill": int(fill_exact), "n": n_int,
                           "kind": "exact_coarse_oracle"})
            exact_rows.append(res_ex)
            # sampled operator at the two frozen S values
            for (slabel, sexp) in S_SPECS:
                S = max(1, int(round(n_int ** sexp)))
                rs_s = np.random.RandomState(int(seed) + 1)
                starts = rs_s.randint(0, n_int, size=S)
                cnts = np.zeros((Cc, Cc))
                for r in starts:
                    ri = int(r)
                    cnts[cells[ri], cells[(ri + 1) % n_int]] += 1.0
                M_s, fill_s = normalize(cnts, Cc)
                T = S
                seq = [cells[(k + t) % n_int] for t in range(T)]
                res = estimate(M_s, seq, n_int, k)
                sqrt_n = float(np.sqrt(n_int))
                cost_ops = 2 * S + Cc ** 3  # S sampling + S readout + eigensolve convention
                res.update({"p": int(p), "seed": int(seed), "C": int(C), "Cc": int(Cc),
                            "S_label": slabel, "S": int(S), "T": int(T),
                            "fill": int(fill_s), "n": n_int,
                            "cost_charged_ops": int(cost_ops),
                            "cost_candidate_model_SC2": int(S * C * C),
                            "sqrt_n": sqrt_n,
                            "cost_ratio": float(cost_ops / sqrt_n),
                            "finish_ratio": float((cost_ops + np.sqrt(n_int / res["L_eff"])) / sqrt_n)})
                configs.append(res)

        # --- negative control: random permutation operators, same grid ---
        rs_p = np.random.RandomState(int(seed) + 2)
        perm = rs_p.permutation(n_int)
        for C in CGRID:
            cellsP = [(r * C) // n_int for r in range(n_int)]  # C position-interval cells
            for (slabel, sexp) in S_SPECS:
                S = max(1, int(round(n_int ** sexp)))
                rs_s2 = np.random.RandomState(int(seed) + 3)
                starts = rs_s2.randint(0, n_int, size=S)
                cntp = np.zeros((C, C))
                for r in starts:
                    ri = int(r)
                    cntp[cellsP[ri], cellsP[int(perm[ri])]] += 1.0
                M_p, fill_p = normalize(cntp, C)
                seqp = []
                x = k  # same target value as EC instance (paired)
                for t in range(S):
                    seqp.append(cellsP[x])
                    x = int(perm[x])
                resn = estimate(M_p, seqp, n_int, k)
                resn.update({"p": int(p), "seed": int(seed), "C": int(C),
                             "S_label": slabel, "S": int(S), "T": int(S),
                             "fill": int(fill_p), "n": n_int,
                             "kind": "random_permutation_control"})
                neg_ctrl.append(resn)

        # --- positive control: full resolution C = n (exact shift), must recover k ---
        phi_f = 1.0 / n_int
        tstar = (-k) % n_int
        A_f = np.exp(-2j * np.pi * phi_f * tstar)  # = e^{+2 pi i k / n}
        psi_f = float(np.angle(A_f) % (2.0 * np.pi))
        k_real_f = psi_f / (2.0 * np.pi * phi_f)
        base_f = int(round(k_real_f)) % n_int
        pos = {"p": int(p), "seed": int(seed), "n": n_int,
               "analytic": {"phi": float(phi_f), "k_real": float(k_real_f), "k": int(k),
                            "w_step": n_int, "base": int(base_f), "count": 1,
                            "L": float(n_int), "hit": bool(base_f == k)}}
        if p <= 1009:
            Msh = np.zeros((n_int, n_int))
            for r in range(n_int):
                Msh[r, (r + 1) % n_int] = 1.0
            seqf = [(k + t) % n_int for t in range(n_int)]  # cells = positions
            pos["explicit_matrix"] = estimate(Msh, seqf, n_int, k)
        pos_ctrl.append(pos)

# --- aggregates (gate arithmetic; chance floor reported alongside) ---
gate_rows = [c for c in configs if c["S_label"] == "n^1/4"]
agg = {"gate_rule": "L_eff >= n^0.05 on S = n^1/4 rows (n^1/4 <= n^0.3 < n^3/8), sustained across three sizes",
       "chance_floor_definition": "E[L_eff | no information] = mean(2 - 1/L); E[hits | chance] = sum(1/L)",
       "per_size": {}}
size_pts = []
for p in PRIMES:
    rs = [c for c in gate_rows if c["p"] == p]
    th = [c["n"] ** 0.05 for c in rs]
    Leff = [c["L_eff"] for c in rs]
    Lc = [c["L"] for c in rs]
    hits = sum(1 for c in rs if c["hit"])
    chance_hits = sum(1.0 / c["L"] for c in rs)
    row = {"n_configs": len(rs),
           "n_mean": mean([c["n"] for c in rs]),
           "threshold_n^0.05_mean": mean(th),
           "hits": int(hits),
           "chance_expected_hits": float(chance_hits),
           "L_claimed_mean": mean(Lc),
           "L_eff_mean": mean(Leff),
           "L_eff_median": float(sorted(Leff)[len(Leff) // 2]),
           "chance_floor_L_eff_mean": mean([2.0 - 1.0 / c["L"] for c in rs]),
           "frac_L_eff_ge_threshold": mean([1.0 if c["L_eff"] >= c["n"] ** 0.05 else 0.0 for c in rs]),
           "cost_ratio_mean": mean([c["cost_ratio"] for c in rs]),
           "finish_ratio_mean": mean([c["finish_ratio"] for c in rs]),
           "candidate_model_SC2_mean": mean([c["cost_candidate_model_SC2"] for c in rs])}
    agg["per_size"][str(p)] = row
    size_pts.append((row["n_mean"], row["L_eff_mean"]))
xs = np.log([pt[0] for pt in size_pts])
ys = np.log([max(pt[1], 1e-12) for pt in size_pts])
agg["L_eff_growth_exponent_delta_vs_n"] = float(np.polyfit(xs, ys, 1)[0])

neg_hits = sum(1 for c in neg_ctrl if c["hit"])
neg_chance = sum(1.0 / c["L"] for c in neg_ctrl)
neg_cross = sum(1 for c in neg_ctrl if c["L_eff"] >= c["n"] ** 0.05)
agg["negative_control"] = {"n_configs": len(neg_ctrl), "hits": int(neg_hits),
                           "chance_expected_hits": float(neg_chance),
                           "hits_ratio_observed_over_chance": float(neg_hits / neg_chance) if neg_chance > 0 else None,
                           "configs_with_L_eff_ge_threshold": int(neg_cross),
                           "L_eff_max": float(max(c["L_eff"] for c in neg_ctrl))}
pos_ok = all(pc["analytic"]["hit"] for pc in pos_ctrl)
exp_ok = all(("explicit_matrix" not in pc) or
             (pc["explicit_matrix"]["informative"] and pc["explicit_matrix"]["hit"]
              and abs(pc["explicit_matrix"]["L"] - pc["n"]) < 1e-6)
             for pc in pos_ctrl)
agg["positive_control"] = {"n_instances": len(pos_ctrl),
                           "analytic_all_hit": bool(pos_ok),
                           "explicit_matrix_all_recovered": bool(exp_ok),
                           "explicit_matrix_sizes": [211, 1009]}

law = {}
for p in PRIMES:
    for C in CGRID:
        for (slabel, _) in S_SPECS:
            rs = [c for c in configs if c["p"] == p and c["C"] == C and c["S_label"] == slabel]
            key = "p%d_C%d_S_%s" % (p, C, slabel.replace("^", ""))
            law[key] = {"L_claimed_mean": mean([c["L"] for c in rs]),
                        "L_eff_mean": mean([c["L_eff"] for c in rs]),
                        "hits": int(sum(1 for c in rs if c["hit"])),
                        "chance_expected_hits": float(sum(1.0 / c["L"] for c in rs)),
                        "informative": int(sum(1 for c in rs if c["informative"])),
                        "phi_mean": mean([c.get("phi") for c in rs if c.get("phi") is not None]),
                        "fill_mean": mean([c["fill"] for c in rs])}
law_exact = {}
for p in PRIMES:
    for C in CGRID:
        rs = [c for c in exact_rows if c["p"] == p and c["C"] == C]
        key = "p%d_C%d_exact" % (p, C)
        law_exact[key] = {"L_claimed_mean": mean([c["L"] for c in rs]),
                          "L_eff_mean": mean([c["L_eff"] for c in rs]),
                          "hits": int(sum(1 for c in rs if c["hit"])),
                          "chance_expected_hits": float(sum(1.0 / c["L"] for c in rs)),
                          "phi_mean": mean([c.get("phi") for c in rs if c.get("phi") is not None]),
                          "lam_abs_mean": mean([c.get("lam_abs") for c in rs if c.get("lam_abs") is not None])}

finished_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
wall = time.time() - t0

out = {
    "experiment_id": "EXP-TRA-001",
    "run_id": "RUN-TRA-001-a",
    "meta": {
        "command": "sage experiments/EXP-TRA-001/tra1_koopman.sage",
        "git_commit": head,
        "dirty_tree": dirty,
        "started_at": started_at,
        "finished_at": finished_at,
        "wall_seconds": wall,
        "sage_version": str(__import__("sage.version", fromlist=["version"]).version),
        "numpy_version": str(np.__version__),
        "python_version": sys.version.split()[0],
        "os": platform.platform()},
    "protocol": {
        "primes": [int(x) for x in PRIMES], "C_grid": [int(x) for x in CGRID],
        "S_grid": ["round(n^1/4)", "round(n^3/8)"], "seeds": [int(x) for x in SEEDS],
        "readout_T_rule": "T = S for charged rows; T = n for exact-coarse oracle and positive control",
        "gate": "L_eff >= n^0.05 at S <= n^0.3 sustained across three sizes"},
    "instances": instances,
    "configs": configs,
    "exact_coarse_oracle": exact_rows,
    "negative_control_random_permutation": neg_ctrl,
    "positive_control_full_resolution": pos_ctrl,
    "aggregates": agg,
    "L_law_sampled": law,
    "L_law_exact_coarse": law_exact}

def jdefault(o):
    try:
        f = float(o)
    except (TypeError, ValueError):
        return str(o)
    i = int(f)
    return i if f == i else f


with open(OUT_PATH, "w") as f:
    json.dump(out, f, indent=1, default=jdefault)

print("EXP-TRA-001 RUN-TRA-001-a done")
print("instances=%d configs=%d exact=%d neg=%d pos=%d wall=%.1fs" %
      (len(instances), len(configs), len(exact_rows), len(neg_ctrl), len(pos_ctrl), wall))
print("positive_control analytic_all_hit=%s explicit_all_recovered=%s" % (pos_ok, exp_ok))
print("negative_control hits=%d chance=%.2f crossings=%d" % (neg_hits, neg_chance, neg_cross))
for p in PRIMES:
    r = agg["per_size"][str(p)]
    print("size p=%d n_mean=%.0f hits=%d chance=%.2f L_eff_mean=%.3f floor=%.3f thresh=%.3f frac_cross=%.3f delta_pending" %
          (p, r["n_mean"], r["hits"], r["chance_expected_hits"], r["L_eff_mean"],
           r["chance_floor_L_eff_mean"], r["threshold_n^0.05_mean"], r["frac_L_eff_ge_threshold"]))
print("L_eff growth exponent delta = %.4f" % agg["L_eff_growth_exponent_delta_vs_n"])
