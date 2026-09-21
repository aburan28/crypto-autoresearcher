"""ici_lib.py — machinery for EXP-ICI-001 (H-ICI-001, handoff TASK-20260718-ICI).

Best-IC-exponent with bootstrap CIs on an extended n-ladder, honest full-cost
accounting. Ports the measurement logic of the frozen-spec solver paths from
ecdlp-autolab (git 354d8d38761f4b4e0cdad1749ae1909ccd45f7ab):

  * crossbred path   <- src/crossbred_exponent.py (optimal-split sweep, GB-seconds
                        cost model of src/crossbred_real_cost.py), sha256 ae934a../9f49b4..
  * MITM path        <- src/mitm_tree_resolution.py (t=4 tree MITM, 1/2+1/t family),
                        sha256 444c1e..
  * rho control      <- src/h040_rho_const.py op-count convention (1 op = 1 point
                        addition, exact first-repeat via full seen-set), sha256 53b56f..
  * matched null     <- T11 principle (src/t11_null_harness.sage, sha256 3085e3..):
                        identical shape profile, structure stripped. GF(2) adaptation:
                        Boolean coefficients are all 1, so matching = same per-generator
                        monomial-count AND same monomial-degree multiset, random support.
  * system builder   <- vendored src_copies/semaev_tree.py, sha256 e9f1681b.. (exact copy)

Determinism: all instance generation and substitution constants come from
seeded random.Random streams (seed layout below), never from global RNGs.
GB timings are wall-clock and therefore NOT bit-reproducible; the same-seed
control therefore compares instance hashes exactly and metrics within noise.

Seed layout (path_code, curve_seed, n):  seed = 1_000_000*path_code + 10_000*curve_seed + n
  path_code: 1=crossbred, 2=mitm, 3=rho, 4=null.
"""

import json
import math
import os
import random
import resource
import signal
import sys
import time
from hashlib import sha256
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src_copies"))

from sage.all import GF, EllipticCurve, PolynomialRing, BooleanPolynomialRing  # noqa: E402

from semaev_tree import (  # noqa: E402  (vendored, sha256 e9f1681b4e422f7a67176fffd3e5f91ab7a95c9fddc1eb925c2bb0a93a9becef)
    build_chained_system_symbolic,
    weil_descend_to_F2,
    gen_decomposable_R,
    make_V_subspace,
)

PATH_CODES = {"crossbred": 1, "mitm": 2, "rho": 3, "null": 4}


def cell_seed(path, curve_seed, n):
    return 1_000_000 * PATH_CODES[path] + 10_000 * int(curve_seed) + int(n)


def peak_rss_bytes():
    # Darwin: ru_maxrss is bytes; Linux: kilobytes. We run on Darwin arm64.
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


# ---------------------------------------------------------------- field/curve

def build_curve(n, curve_seed):
    """Fq = F_{2^n}; curve Y^2 + XY = X^3 + X^2 + B (Semaev 2015 form, A=1),
    B nonzero derived from seeded bit stream (version-stable, no Sage RNG)."""
    n = int(n)
    curve_seed = int(curve_seed)
    Fq = GF(2 ** n, name="alpha")
    alpha = Fq.gen()
    rng = random.Random(7_000_000 + 10_000 * curve_seed + n)
    B = Fq(0)
    while B == 0:
        B = Fq(0)
        for j in range(n):
            if rng.getrandbits(1):
                B += alpha ** j
    E = EllipticCurve(Fq, [1, Fq(1), 0, 0, B])
    return Fq, E, alpha, B


def fq_to_int(v):
    return sum(int(b) << i for i, b in enumerate(v._vector_()))


def bits_of(v, n):
    return "".join(str(int(b)) for b in v._vector_())


# ---------------------------------------------------------------- instances

def make_targets(E, t, V_sub, n_targets, seed):
    """n_targets decomposable R (sum of t factor-base points), seeded.
    Returns list of (R_X, P_list)."""
    rng = random.Random(seed)
    out = []
    attempts = 0
    while len(out) < n_targets and attempts < 400:
        attempts += 1
        try:
            R, P_list = gen_decomposable_R(E, t, V_sub, rng=rng)
            out.append((R[0], P_list))
        except Exception:
            continue
    return out


def descend_system(t, Fq, B, R_X, n, k, alpha):
    Rh, polys, _ = build_chained_system_symbolic(t, Fq, B, R_X)
    Bring, dpolys = weil_descend_to_F2(polys, n, k, alpha, Rh)
    return Bring, dpolys


def system_hash(dpolys):
    h = sha256()
    for p in dpolys:
        monos = sorted(
            tuple(sorted(g.index() for g in m.variables())) for m in p.monomials()
        )
        for mono in monos:
            h.update(bytes(str(mono), "ascii") + b";")
        h.update(b"|")
    return h.hexdigest()


def verify_planted_chain(Fq, B, R_X, P_list):
    """Exact verification of the planted decomposition in Fq (no Boolean side):
    u_i = x(P_1+..+P_{i+1}); check the chained S_3 equations vanish and
    S_3(u_{t-2}, x_t, R_X) = 0."""
    def s3(x, y, z):
        return (x * y + x * z + y * z) ** 2 + x * y * z + B
    t = len(P_list)
    xs = [P[0] for P in P_list]
    acc = P_list[0]
    us = []
    for i in range(t - 2):
        acc = acc + P_list[i + 1]
        us.append(acc[0])
    # S_3(u_1, x_1, x_2) = 0
    if s3(us[0], xs[0], xs[1]) != 0:
        return False
    for i in range(t - 3):
        if s3(us[i], us[i + 1], xs[i + 2]) != 0:
            return False
    return s3(us[-1], xs[-1], R_X) == 0


# ---------------------------------------------------------------- timeouts

class _TO(Exception):
    pass


def _alarm(signum, frame):
    raise _TO()


signal.signal(signal.SIGALRM, _alarm)


# ---------------------------------------------------------------- crossbred

def crossbred_sweep(dpolys, Bring, nb, kfix_fracs, guesses, per_gb_timeout,
                    rng, target_deadline):
    """Port of crossbred_exponent.py:optimal_crossbred_cost with per-candidate
    records and a wall-clock target deadline. Sweeps k_fix ASCENDING (small
    brute force, hard GB first) so the costly side is always explored; a
    timed-out candidate is recorded as censored with lower-bound cost — it can
    only hide the optimum if 2^k*T < best with T > timeout, i.e. k + log2(T) >
    best would have to beat best with T larger than best/2^k, impossible when
    log2(timeout) >= best - k; checked in the returned bias flag."""
    gens = list(Bring.gens())
    per_gb_timeout = float(per_gb_timeout)
    guesses = int(guesses)
    nb = int(nb)
    cands = sorted({int(f * nb) for f in kfix_fracs})
    cands = [c for c in cands if 1 <= c < nb]
    rows = []
    best = None  # (k_fix, log2_total, per_guess)
    for k_fix in cands:
        if time.time() > target_deadline:
            rows.append({"k_fix": k_fix, "status": "censored_budget"})
            continue
        times = []
        any_to = False
        for _g in range(guesses):
            if time.time() > target_deadline:
                any_to = True
                break
            sub = {gens[vi]: Bring(rng.randint(0, 1)) for vi in range(nb - k_fix, nb)}
            sys_sub = [ps for ps in (p.subs(sub) for p in dpolys) if ps != 0]
            signal.setitimer(signal.ITIMER_REAL, per_gb_timeout)
            t0 = time.time()
            try:
                _GB = Bring.ideal(sys_sub).groebner_basis()
                times.append(time.time() - t0)
            except _TO:
                times.append(float(per_gb_timeout))
                any_to = True
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
        if not times:
            rows.append({"k_fix": k_fix, "status": "censored_budget"})
            continue
        per_guess = median(times)
        log2_total = k_fix + math.log2(max(per_guess, 1e-9))
        status = "timeout" if any_to else "ok"
        rows.append({"k_fix": k_fix, "status": status,
                     "median_per_guess_s": per_guess,
                     "log2_total": log2_total})
        if not any_to and (best is None or log2_total < best[1]):
            best = (k_fix, log2_total, per_guess)
    # bias check: a censored/timed-out candidate with k + log2(timeout) < best
    # could in principle hide a better split -> flag honestly.
    bias_possible = False
    if best is not None:
        for r in rows:
            if r.get("status") in ("timeout",) and \
               r["k_fix"] + math.log2(max(r["median_per_guess_s"], 1e-9)) < best[1]:
                bias_possible = True
    return best, rows, bias_possible


def run_crossbred(cfg):
    t = cfg["t"]
    out = {"run_id": cfg["run_id"], "path": "crossbred", "t": t,
           "config": {k: v for k, v in cfg.items() if k != "run_id"},
           "cells": [], "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    t_start = time.time()
    script_deadline = t_start + cfg["script_budget_s"]
    fracs = cfg["kfix_fracs"]
    consecutive_censored = 0
    for n in cfg["ladder"]:
        k = (n + t - 1) // t
        for curve_seed in cfg["curve_seeds"]:
            cell = {"n": n, "curve_seed": curve_seed, "k": k,
                    "status": "measured", "targets": []}
            if time.time() > script_deadline or consecutive_censored >= 2:
                cell["status"] = "censored_budget"
                cell["reason"] = "script budget exhausted or ladder stopped (2 consecutive censored)"
                out["cells"].append(cell)
                continue
            Fq, E, alpha, B = build_curve(n, curve_seed)
            V_sub = make_V_subspace(Fq, alpha, k)
            cseed = cell_seed("crossbred", curve_seed, n)
            tgts = make_targets(E, t, V_sub, cfg["targets_per_cell"], cseed)
            rng = random.Random(cseed ^ 0x5A5A)
            cell_deadline = time.time() + cfg["cell_budget_s"]
            n_bias = 0
            build_s = 0.0
            for ti, (R_X, P_list) in enumerate(tgts):
                row = {"idx": ti, "R_x_bits": bits_of(R_X, n),
                       "planted_verified": verify_planted_chain(Fq, B, R_X, P_list)}
                if time.time() > min(cell_deadline, script_deadline):
                    row["status"] = "censored_budget"
                    cell["targets"].append(row)
                    continue
                tb0 = time.time()
                Bring, dpolys = descend_system(t, Fq, B, R_X, n, k, alpha)
                build_s += time.time() - tb0
                row["system_sha256"] = system_hash(dpolys)
                row["nb"] = Bring.ngens()
                row["n_equations"] = len(dpolys)
                tgt_deadline = min(time.time() + cfg["target_budget_s"],
                                   cell_deadline, script_deadline)
                b0 = time.time()
                best, rows, bias = crossbred_sweep(
                    dpolys, Bring, Bring.ngens(), fracs, cfg["guesses"],
                    cfg["per_gb_timeout_s"], rng, tgt_deadline)
                row["sweep_wall_s"] = time.time() - b0
                row["candidates"] = rows
                if best is None:
                    row["status"] = "all_censored"
                else:
                    row["status"] = "ok"
                    row["best"] = {"k_fix": best[0], "log2_total": best[1],
                                   "per_guess_s": best[2],
                                   "k_fix_frac_of_nb": best[0] / Bring.ngens()}
                    n_bias += int(bias)
                cell["targets"].append(row)
            costs = [r["best"]["log2_total"] for r in cell["targets"] if r.get("best")]
            cell["n_targets_planned"] = len(tgts)
            cell["n_targets_measured"] = len(costs)
            cell["n_bias_flags"] = n_bias
            cell["build_s"] = build_s
            cell["peak_rss_bytes"] = peak_rss_bytes()
            if not costs:
                cell["status"] = "censored_budget" if cell["targets"] else "censored_no_targets"
                consecutive_censored += 1
            else:
                cell["cell_median_log2cost"] = median(costs)
                if len(costs) < cfg["targets_per_cell"]:
                    cell["status"] = "measured_partial"
                consecutive_censored = 0
            out["cells"].append(cell)
            _write_raw(cfg, out)  # crash-safe checkpoint
    out["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out["wall_s"] = time.time() - t_start
    out["peak_rss_bytes"] = peak_rss_bytes()
    _finalize_fits(out, t)
    _write_raw(cfg, out)
    return out


# ---------------------------------------------------------------- MITM (t=4)

def _solve_s3_quad(y, z, B, Ru):
    A = (y + z) ** 2
    C = y * z
    D = (y * z) ** 2 + B
    u = Ru.gen()
    poly = A * u ** 2 + C * u + D
    if poly == 0:
        return []
    return [r for r, _m in poly.roots()]


def mitm_t4(Fq, B, V, R_x, Ru, work_deadline):
    """Port of mitm_tree_resolution.py:mitm_t4. Returns dict with work units,
    wall time, list sizes, relations, and a deadline-exceeded flag."""
    from collections import defaultdict
    work = 0
    t0 = time.time()
    L1 = defaultdict(list)
    exceeded = False
    for x1 in V:
        for x2 in V:
            work += 1
            if work % 4096 == 0 and time.time() > work_deadline:
                exceeded = True
                break
            for u1 in _solve_s3_quad(x1, x2, B, Ru):
                L1[u1].append((x1, x2))
        if exceeded:
            break
    build_s = time.time() - t0
    relations = []
    t1 = time.time()
    if not exceeded:
        for x4 in V:
            for x3 in V:
                work += 1
                if work % 4096 == 0 and time.time() > work_deadline:
                    exceeded = True
                    break
                for u2 in _solve_s3_quad(x4, R_x, B, Ru):
                    for u1 in _solve_s3_quad(u2, x3, B, Ru):
                        if u1 in L1:
                            for (x1, x2) in L1[u1]:
                                relations.append((x1, x2, x3, x4))
            if exceeded:
                break
    match_s = time.time() - t1
    return {"work_units": work, "wall_s": build_s + match_s,
            "list_build_s": build_s, "match_s": match_s,
            "L1_entries": sum(len(v) for v in L1.values()),
            "n_relations": len(relations), "relations": relations,
            "deadline_exceeded": exceeded}


def run_mitm(cfg):
    t = cfg["t"]  # 4
    out = {"run_id": cfg["run_id"], "path": "mitm", "t": t,
           "config": {k: v for k, v in cfg.items() if k != "run_id"},
           "cells": [], "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    t_start = time.time()
    script_deadline = t_start + cfg["script_budget_s"]
    consecutive_censored = 0
    for n in cfg["ladder"]:
        k = (n + t - 1) // t
        for curve_seed in cfg["curve_seeds"]:
            cell = {"n": n, "curve_seed": curve_seed, "k": k,
                    "status": "measured", "targets": []}
            if time.time() > script_deadline or consecutive_censored >= 2:
                cell["status"] = "censored_budget"
                cell["reason"] = "script budget exhausted or ladder stopped (2 consecutive censored)"
                out["cells"].append(cell)
                continue
            Fq, E, alpha, B = build_curve(n, curve_seed)
            V = make_V_subspace(Fq, alpha, k)
            Ru = PolynomialRing(Fq, "u")
            cseed = cell_seed("mitm", curve_seed, n)
            tgts = make_targets(E, t, V, cfg["targets_per_cell"], cseed)
            target_type = "planted"
            if not tgts:
                # MITM work is target-independent (full list enumeration); fall
                # back to seeded random targets when too few factor-base points
                # exist to plant a decomposition (expected at tiny n).
                target_type = "random"
                rng_t = random.Random(cseed ^ 0x1234)
                elts = [Fq(x) for x in range(2)] + list(Fq)
                tgts = [(elts[rng_t.randrange(len(elts))], None)
                        for _ in range(cfg["targets_per_cell"])]
            cell["target_type"] = target_type
            cell_deadline = time.time() + cfg["cell_budget_s"]
            for ti, (R_X, P_list) in enumerate(tgts):
                row = {"idx": ti, "R_x_bits": bits_of(R_X, n),
                       "target_type": target_type,
                       "planted_verified": (verify_planted_chain(Fq, B, R_X, P_list)
                                            if P_list is not None else None)}
                if time.time() > min(cell_deadline, script_deadline):
                    row["status"] = "censored_budget"
                    cell["targets"].append(row)
                    continue
                res = mitm_t4(Fq, B, V, R_X, Ru,
                              min(cell_deadline, script_deadline))
                if P_list is not None:
                    planted = tuple(P[0] for P in P_list)
                    row["planted_found"] = any(
                        tuple(r) == planted or tuple(r[::-1]) == planted
                        for r in res["relations"])
                else:
                    row["planted_found"] = None
                row.update({k2: res[k2] for k2 in
                            ("work_units", "wall_s", "list_build_s", "match_s",
                             "L1_entries", "n_relations", "deadline_exceeded")})
                row["log2_work"] = math.log2(max(res["work_units"], 1))
                row["log2_wall_s"] = math.log2(max(res["wall_s"], 1e-9))
                row["status"] = "deadline_partial" if res["deadline_exceeded"] else "ok"
                cell["targets"].append(row)
                del res["relations"]
            walls = [r["wall_s"] for r in cell["targets"] if r.get("status") == "ok"]
            works = [r["log2_work"] for r in cell["targets"] if r.get("status") == "ok"]
            cell["n_targets_planned"] = len(tgts)
            cell["n_targets_measured"] = len(walls)
            cell["peak_rss_bytes"] = peak_rss_bytes()
            if not walls:
                cell["status"] = "censored_budget"
                consecutive_censored += 1
            else:
                cell["cell_median_wall_s"] = median(walls)
                cell["cell_median_log2wall"] = median([math.log2(max(w, 1e-9)) for w in walls])
                cell["cell_median_log2work"] = median(works)
                if len(walls) < cfg["targets_per_cell"]:
                    cell["status"] = "measured_partial"
                consecutive_censored = 0
            out["cells"].append(cell)
            _write_raw(cfg, out)
    out["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out["wall_s"] = time.time() - t_start
    out["peak_rss_bytes"] = peak_rss_bytes()
    _finalize_fits(out, t)
    _write_raw(cfg, out)
    return out


# ---------------------------------------------------------------- rho control

def rho_walk(E, P, ord_P, Q, rng, max_ops, rw=20):
    """H040 op-count convention: 1 op = 1 point addition during the walk;
    per-run setup (A-table, start) NOT counted; exact first-repeat detection
    via full seen-set. Plain walk (no negation map); theory const 1.2533."""
    cd = [(rng.randrange(1, ord_P), rng.randrange(1, ord_P)) for _ in range(rw)]
    A = [c * P + d * Q for c, d in cd]
    a0, b0 = rng.randrange(ord_P), rng.randrange(ord_P)
    X = a0 * P + b0 * Q
    seen = {}
    ops = 0
    while ops < max_ops:
        key = (fq_to_int(X[0]), fq_to_int(X[1])) if X != E(0) else (-1, -1)
        if key in seen:
            a1, b1 = seen[key]
            den = (b0 - b1) % ord_P
            num = (a1 - a0) % ord_P
            if den == 0:
                # useless collision; perturb deterministically
                X = X + A[0]
                b0 = (b0 + cd[0][1]) % ord_P
                ops += 1
                continue
            # linear congruence den*k = num (mod ord_P); ord_P may be even
            g = math.gcd(den, ord_P)
            if num % g != 0:
                X = X + A[0]
                b0 = (b0 + cd[0][1]) % ord_P
                ops += 1
                continue
            den_r, num_r, mod_r = den // g, num // g, ord_P // g
            k0 = (num_r * pow(den_r, -1, mod_r)) % mod_r
            found = None
            if g <= 128:
                for i in range(g):
                    cand = (k0 + i * mod_r) % ord_P
                    if cand * P == Q:
                        found = int(cand)
                        break
            if found is None and g > 128:
                # too many candidates to verify cheaply; record first
                found = int(k0)
            return {"ops": ops, "solved": found is not None, "k": found}
        seen[key] = (a0, b0)
        i = fq_to_int(X[0]) % rw if X != E(0) else 0
        X = X + A[i]
        a0 = (a0 + cd[i][0]) % ord_P
        b0 = (b0 + cd[i][1]) % ord_P
        ops += 1
    return {"ops": ops, "solved": False}


def run_rho(cfg):
    out = {"run_id": cfg["run_id"], "path": "rho", "t": None,
           "config": {k: v for k, v in cfg.items() if k != "run_id"},
           "cells": [], "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    t_start = time.time()
    script_deadline = t_start + cfg["script_budget_s"]
    for n in cfg["ladder"]:
        for curve_seed in cfg["curve_seeds"]:
            cell = {"n": n, "curve_seed": curve_seed, "status": "measured",
                    "targets": []}
            if time.time() > script_deadline:
                cell["status"] = "censored_budget"
                out["cells"].append(cell)
                continue
            Fq, E, alpha, B = build_curve(n, curve_seed)
            N = E.cardinality()
            P = E.gens()[0] if E.abelian_group().ngens() >= 1 else E.random_point()
            ord_P = int(P.order())
            cseed = cell_seed("rho", curve_seed, n)
            rng = random.Random(cseed)
            for ti in range(cfg["targets_per_cell"]):
                if time.time() > script_deadline:
                    cell["targets"].append({"idx": ti, "status": "censored_budget"})
                    continue
                k_true = rng.randrange(1, ord_P)
                Q = k_true * P
                max_ops = int(cfg["rho_ops_factor"] * math.sqrt(ord_P)) + 100
                t0 = time.time()
                r = rho_walk(E, P, ord_P, Q, rng, max_ops)
                dt = time.time() - t0
                ok = r["solved"] and (r["k"] * P == Q)
                cell["targets"].append({
                    "idx": ti, "ops": r["ops"], "solved": r["solved"],
                    "verified": bool(ok), "wall_s": dt,
                    "const_vs_sqrt_ord": r["ops"] / math.sqrt(ord_P)})
            done = [r2 for r2 in cell["targets"] if r2.get("solved")]
            cell["ord_P"] = ord_P
            cell["group_order"] = int(N)
            cell["n_targets_measured"] = len(done)
            cell["peak_rss_bytes"] = peak_rss_bytes()
            if done:
                cell["cell_median_log2ops"] = median([math.log2(r2["ops"]) for r2 in done])
            else:
                cell["status"] = "censored_budget"
            out["cells"].append(cell)
            _write_raw(cfg, out)
    out["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out["wall_s"] = time.time() - t_start
    out["peak_rss_bytes"] = peak_rss_bytes()
    _finalize_fits(out, None)
    _write_raw(cfg, out)
    return out


# ---------------------------------------------------------------- matched null

def matched_null_polys(dpolys, Bring, rng):
    """T11-style matched null, GF(2) adaptation: same per-generator monomial
    count and same monomial-degree multiset; support randomized (coefficients
    in GF(2) are all 1, so randomizing coefficients is degenerate)."""
    nb = Bring.ngens()
    gens = list(Bring.gens())
    from itertools import combinations
    nulls = []
    match_ok = True
    for p in dpolys:
        degs = sorted(len(m.variables()) for m in p.monomials())
        counts = {}
        for d in degs:
            counts[d] = counts.get(d, 0) + 1
        newp = Bring(0)
        used = set()
        for d, cnt in counts.items():
            pool = list(combinations(range(nb), d)) if d > 0 else [()]
            rng.shuffle(pool)
            taken = 0
            for combo in pool:
                if combo in used:
                    continue
                used.add(combo)
                m = Bring(1)
                for vi in combo:
                    m = m * gens[vi]
                newp += m
                taken += 1
                if taken == cnt:
                    break
            if taken < cnt:
                match_ok = False
        # certify: monomial count + degree multiset identical
        nde = sorted(len(m.variables()) for m in newp.monomials())
        if nde != degs:
            match_ok = False
        nulls.append(newp)
    return nulls, match_ok


def run_null(cfg):
    """Solve-stage control: crossbred cost on T11-style matched null systems
    derived from the same instances the crossbred path used."""
    t = cfg["t"]
    out = {"run_id": cfg["run_id"], "path": "null", "t": t,
           "config": {k: v for k, v in cfg.items() if k != "run_id"},
           "cells": [], "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    t_start = time.time()
    script_deadline = t_start + cfg["script_budget_s"]
    fracs = cfg["kfix_fracs"]
    for n in cfg["ladder"]:
        k = (n + t - 1) // t
        for curve_seed in cfg["curve_seeds"]:
            cell = {"n": n, "curve_seed": curve_seed, "k": k,
                    "status": "measured", "targets": []}
            if time.time() > script_deadline:
                cell["status"] = "censored_budget"
                out["cells"].append(cell)
                continue
            Fq, E, alpha, B = build_curve(n, curve_seed)
            V_sub = make_V_subspace(Fq, alpha, k)
            cseed = cell_seed("crossbred", curve_seed, n)  # SAME instances as crossbred
            tgts = make_targets(E, t, V_sub, cfg["targets_per_cell"], cseed)
            rng = random.Random(cseed ^ 0x5A5A)
            null_rng = random.Random(cell_seed("null", curve_seed, n))
            cell_deadline = time.time() + cfg["cell_budget_s"]
            for ti, (R_X, P_list) in enumerate(tgts):
                row = {"idx": ti, "R_x_bits": bits_of(R_X, n)}
                if time.time() > min(cell_deadline, script_deadline):
                    row["status"] = "censored_budget"
                    cell["targets"].append(row)
                    continue
                Bring, dpolys = descend_system(t, Fq, B, R_X, n, k, alpha)
                row["semaev_system_sha256"] = system_hash(dpolys)
                nulls, match_ok = matched_null_polys(dpolys, Bring, null_rng)
                row["null_match_certified"] = bool(match_ok)
                row["null_system_sha256"] = system_hash(nulls)
                tgt_deadline = min(time.time() + cfg["target_budget_s"],
                                   cell_deadline, script_deadline)
                best, rows, bias = crossbred_sweep(
                    nulls, Bring, Bring.ngens(), fracs, cfg["guesses"],
                    cfg["per_gb_timeout_s"], rng, tgt_deadline)
                row["candidates"] = rows
                if best is None:
                    row["status"] = "all_censored"
                else:
                    row["status"] = "ok"
                    row["best"] = {"k_fix": best[0], "log2_total": best[1],
                                   "per_guess_s": best[2]}
                cell["targets"].append(row)
            costs = [r["best"]["log2_total"] for r in cell["targets"] if r.get("best")]
            cell["n_targets_measured"] = len(costs)
            cell["peak_rss_bytes"] = peak_rss_bytes()
            if not costs:
                cell["status"] = "censored_budget"
            else:
                cell["cell_median_log2cost"] = median(costs)
            out["cells"].append(cell)
            _write_raw(cfg, out)
    out["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out["wall_s"] = time.time() - t_start
    out["peak_rss_bytes"] = peak_rss_bytes()
    _finalize_fits(out, t)
    _write_raw(cfg, out)
    return out


# ---------------------------------------------------------------- fits

def ols_slope(xs, ys):
    m = len(xs)
    xb = sum(xs) / m
    yb = sum(ys) / m
    den = sum((x - xb) ** 2 for x in xs)
    if den == 0:
        return 0.0
    return sum((x - xb) * (y - yb) for x, y in zip(xs, ys)) / den


def bootstrap_slope(cells, key, reps, seed):
    """cells: list of (n, [values]). Resample targets within each cell,
    take cell median, OLS slope vs n. Returns (point, lo90, hi90, reps_kept)."""
    rng = random.Random(seed)
    pts = [(n, median(vals)) for n, vals in cells if vals]
    if len(pts) < 2:
        return None
    point = ols_slope([p[0] for p in pts], [p[1] for p in pts])
    slopes = []
    for _ in range(reps):
        bs = []
        for n, vals in cells:
            if not vals:
                continue
            res = [vals[rng.randrange(len(vals))] for _ in vals]
            bs.append((n, median(res)))
        if len(bs) >= 2:
            slopes.append(ols_slope([b[0] for b in bs], [b[1] for b in bs]))
    slopes.sort()
    if not slopes:
        return (point, None, None, 0)
    lo = slopes[int(0.05 * len(slopes))]
    hi = slopes[min(int(0.95 * len(slopes)), len(slopes) - 1)]
    return (point, lo, hi, len(slopes))


def per_cell_implied(cells, key, t, reps, seed):
    """Per-cell implied total exponent: median(cost)/n + 1/t with bootstrap CI."""
    rng = random.Random(seed)
    rows = []
    for n, vals in cells:
        if not vals:
            continue
        med = median(vals)
        boots = []
        for _ in range(reps):
            res = [vals[rng.randrange(len(vals))] for _ in vals]
            boots.append(median(res))
        boots.sort()
        lo = boots[int(0.05 * len(boots))]
        hi = boots[min(int(0.95 * len(boots)), len(boots) - 1)]
        shift = (1.0 / t) if t else 0.0
        rows.append({"n": n, "n_targets": len(vals),
                     "median_log2cost": med,
                     "implied_exponent": med / n + shift,
                     "implied_exponent_ci90": [lo / n + shift, hi / n + shift]})
    return rows


def _finalize_fits(out, t):
    path = out["path"]
    reps = out["config"].get("bootstrap_reps", 2000)
    seed = out["config"].get("bootstrap_seed", 20260718)
    if path in ("crossbred", "null"):
        # pool per-target costs across the 3 curve cells at each n
        pooled = {}
        for c in out["cells"]:
            pooled.setdefault(c["n"], []).extend(
                [r["best"]["log2_total"] for r in c["targets"] if r.get("best")])
        cells = sorted(pooled.items())
        fit = bootstrap_slope(cells, None, reps, seed)
        out["fits"] = {
            "cells_used": [{"n": n, "n_targets": len(v)} for n, v in cells],
            "per_pdp_slope_fit": fit,
            "total_exponent": (fit[0] + 1.0 / t) if fit else None,
            "total_exponent_ci90": ([fit[1] + 1.0 / t, fit[2] + 1.0 / t]
                                    if fit and fit[1] is not None else None),
            "per_cell_implied": per_cell_implied(cells, None, t, reps, seed + 1),
        }
    elif path == "mitm":
        pooled_w = {}
        pooled_t = {}
        for c in out["cells"]:
            pooled_w.setdefault(c["n"], []).extend(
                [r["log2_work"] for r in c["targets"] if r.get("status") == "ok"])
            pooled_t.setdefault(c["n"], []).extend(
                [r["log2_wall_s"] for r in c["targets"] if r.get("status") == "ok"])
        cells_w = sorted(pooled_w.items())
        cells_t = sorted(pooled_t.items())
        fit_w = bootstrap_slope(cells_w, None, reps, seed)
        fit_t = bootstrap_slope(cells_t, None, reps, seed + 2)
        family = []
        for tt in (4, 6, 8, 10, 12):
            if fit_w:
                family.append({"t": tt,
                               "total_exponent": fit_w[0] + 1.0 / tt,
                               "total_exponent_ci90": [fit_w[1] + 1.0 / tt,
                                                       fit_w[2] + 1.0 / tt]})
        out["fits"] = {
            "cells_used": [{"n": n, "n_targets": len(v)} for n, v in cells_w],
            "per_pdp_slope_fit_work": fit_w,
            "per_pdp_slope_fit_wall": fit_t,
            "family_total_exponents": family,
            "per_cell_implied": per_cell_implied(cells_w, None, t, reps, seed + 1),
        }
    elif path == "rho":
        pooled = {}
        for c in out["cells"]:
            pooled.setdefault(c["n"], []).extend(
                [math.log2(r["ops"]) for r in c["targets"] if r.get("solved")])
        cells = sorted(pooled.items())
        fit = bootstrap_slope(cells, None, reps, seed)
        consts = [r["const_vs_sqrt_ord"] for c in out["cells"]
                  for r in c["targets"] if r.get("solved")]
        out["fits"] = {
            "cells_used": [{"n": n, "n_targets": len(v)} for n, v in cells],
            "ops_slope_fit": fit,
            "const_median": (median(consts) if consts else None),
            "const_theory_plain": 1.2533141373155001,
        }


def _write_raw(cfg, out):
    tmp = cfg["out_path"] + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=1, default=str)
    os.replace(tmp, cfg["out_path"])


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True,
                    choices=["crossbred", "mitm", "rho", "null"])
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ladder", required=True, help="comma list of n")
    ap.add_argument("--t", type=int, default=3)
    ap.add_argument("--curve-seeds", default="1,2,3")
    ap.add_argument("--targets-per-cell", type=int, default=8)
    ap.add_argument("--guesses", type=int, default=2)
    ap.add_argument("--kfix-fracs", default="0.45,0.4,0.35,0.3,0.25,0.2,0.15,0.1")
    ap.add_argument("--per-gb-timeout-s", type=float, default=10.0)
    ap.add_argument("--target-budget-s", type=float, default=25.0)
    ap.add_argument("--cell-budget-s", type=float, default=100.0)
    ap.add_argument("--script-budget-s", type=float, default=250.0)
    ap.add_argument("--rho-ops-factor", type=float, default=25.0)
    ap.add_argument("--bootstrap-reps", type=int, default=2000)
    ap.add_argument("--bootstrap-seed", type=int, default=20260718)
    args = ap.parse_args(argv)
    cfg = {"run_id": args.run_id, "out_path": args.out,
           "ladder": [int(x) for x in args.ladder.split(",")],
           "t": args.t,
           "curve_seeds": [int(x) for x in args.curve_seeds.split(",")],
           "targets_per_cell": args.targets_per_cell,
           "guesses": args.guesses,
           "kfix_fracs": [float(x) for x in args.kfix_fracs.split(",")],
           "per_gb_timeout_s": args.per_gb_timeout_s,
           "target_budget_s": args.target_budget_s,
           "cell_budget_s": args.cell_budget_s,
           "script_budget_s": args.script_budget_s,
           "rho_ops_factor": args.rho_ops_factor,
           "bootstrap_reps": args.bootstrap_reps,
           "bootstrap_seed": args.bootstrap_seed}
    t0 = time.time()
    if args.path == "crossbred":
        out = run_crossbred(cfg)
    elif args.path == "mitm":
        out = run_mitm(cfg)
    elif args.path == "rho":
        out = run_rho(cfg)
    else:
        out = run_null(cfg)
    print("RUN %s (%s) done in %.1fs; cells: %s" % (
        args.run_id, args.path, time.time() - t0,
        [(c["n"], c["curve_seed"], c["status"]) for c in out["cells"]]))
    if out.get("fits"):
        print(json.dumps(out["fits"], indent=1, default=str))
    return 0


if __name__ == "__main__":
    main()
