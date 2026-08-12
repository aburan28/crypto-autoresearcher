# EXP-SIG-006 Phase B — corrected-null constructions + validation (n=9 seed 1).
#
# Constructions (all per-equation degree-histogram matched to the sem):
#   N0: old support-matched null (pinned semantics) — determinism rerun of
#       RUN-EXP-SIG-005-k (expect ncols 31,180 / rank 31,179 / extra 4,986).
#   N1: column-matched null (the mission's literal corrected construction):
#       per (eq, deg) monomials sampled from SAFE pools whose D6 up-closure
#       is inside the sem's D6 column set; rejection until the null's D6
#       column set EQUALS the sem's as a set (equal ncols by construction);
#       parity-fixed to vanish at a seeded random point z (consistent).
#   N2: consistency-forced null: old-style support-matched + parity fix at z
#       (no column constraint) — separates consistency from column effects.
#
# Gates per spec: C2 anchors (extra=0, rank==sr_pred at D3/D4/D5 for the
# SAME construction), C3 D6 validation (column equality for N1; extra=0;
# rank==sr_pred), C4 determinism (N1 built twice, identical).
# All numbers recorded regardless of gate outcomes (negative gate results
# are the decisive test of the diagnosis, not run failures).

import sys, os, time, json, argparse, platform, datetime, itertools, hashlib
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--out', required=True)
p.add_argument('--n', type=int, default=9)
p.add_argument('--seed', type=int, default=1)
p.add_argument('--soft-cap', type=int, default=1500)
p.add_argument('--max-trials', type=int, default=60)
args = p.parse_args()

EXPDIR = Path(args.out).resolve().parents[2]
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))

t_start = time.time()
out = {
    "experiment": "EXP-SIG-006", "phase": "B_corrected_nulls",
    "args": vars(args),
    "environment": {
        "sage_version": str(sage.version.version),
        "python_version": sys.version.split()[0],
        "os": platform.platform(), "machine": platform.machine(),
    },
    "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "cells": [],
}


def flush():
    out["elapsed_s_so_far"] = round(time.time() - t_start, 2)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(jsonsafe(out), fh, indent=1)


def sha256(pth):
    return hashlib.sha256(Path(pth).read_bytes()).hexdigest()


PINNED = {
    "h013_f5_signatures.sage": "1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087",
    "semaev_tree.py": "e9f1681b4e422f7a67176fffd3e5f91ab7a95c9fddc1eb925c2bb0a93a9becef",
    "ic_first_fall_fast.py": "f1c98bd8642df226760f43038d6687e73794d04b9c7a9073f244b8a0433fad61",
    "macaulay_export.py": "c00b8aad9ad47f8a3f09c39f6b65062a37562703bfd1c4f6159b1e54b1dbad97",
}
ih = {f.name: sha256(f) for f in sorted((EXPDIR / 'src').iterdir())}
out["instrument_sha256"] = ih
out["instrument_sha256_matches_pinned"] = all(ih.get(k) == v for k, v in PINNED.items())


def softcap_hit():
    return (time.time() - t_start) > args.soft_cap


n, seed = args.n, args.seed
k_ = (n + 2) // 3
nb_expected = n + 3 * k_

# ---- build sem + sem D6 column set (ground truth via coverage formula)
monosets, nb, meta = build_boolean_semaev(n, 3, seed)
eq_degs = [max(mono_deg(x) for x in f) for f in monosets]


def colset_of(ms, D):
    cols = set()
    for i, f in enumerate(ms):
        di = max(mono_deg(x) for x in f)
        for mp in f:
            for md in range(0, min(D - di, D - len(mp)) + 1):
                rest = [v for v in range(nb) if v not in mp]
                for combo in itertools.combinations(rest, md):
                    cols.add(mp | frozenset(combo))
    return cols


print("=== build sem n=%d seed=%d; computing sem D6 column set ===" % (n, seed), flush=True)
t0 = time.time()
C_sem6 = colset_of(monosets, 6)
print("  sem D6 ncols=%d (%.1fs)" % (len(C_sem6), time.time() - t0), flush=True)
out["sem"] = {"meta": meta, "eq_degs": sorted(eq_degs), "ncols_D6": len(C_sem6)}
flush()


def variety_count(ms):
    import numpy as np
    P = np.arange(2 ** nb, dtype=np.uint32)
    sol = np.ones(2 ** nb, dtype=bool)
    for f in ms:
        acc = np.zeros(2 ** nb, dtype=bool)
        for m in f:
            mm = np.uint32(0)
            for v in m:
                mm |= np.uint32(1 << v)
            acc = np.logical_xor(acc, (P & mm) == mm)
        sol &= ~acc
    return int(sol.sum())


# ---- N1 construction: safe pools + rejection on D6 column equality + parity
def upset6_within(mp, di):
    """All m' = mp u mu, |mu| <= 6-di, |m'| <= 6."""
    res = set()
    rest = [v for v in range(nb) if v not in mp]
    for md in range(0, min(6 - di, 6 - len(mp)) + 1):
        for combo in itertools.combinations(rest, md):
            res.add(mp | frozenset(combo))
    return res


print("=== N1: building safe pools (this takes a few minutes) ===", flush=True)
t0 = time.time()
# At D6 the sem's column set contains ALL monomials of degree <= 5 (RUN-a:
# sem_D6 cols_by_degree shows 1/18/153/816/3060/8568 complete) and misses
# only degree-6 monomials. So a support monomial mp (in an eq of degree di)
# is "safe" iff every SEXTIC mp u mu with |mu| = 6-|mp| <= 6-di is in C_sem6;
# if 6-|mp| > 6-di the products never reach degree 6 and mp is auto-safe.
sextics_sem6 = set(m for m in C_sem6 if len(m) == 6)


def is_safe(mp, di):
    md = 6 - len(mp)
    if md > 6 - di:
        return True
    rest = [v for v in range(nb) if v not in mp]
    for combo in itertools.combinations(rest, md):
        if (mp | frozenset(combo)) not in sextics_sem6:
            return False
    return True


pools = {}   # (i, d) -> list of safe monomials
pool_sizes = {}
for i, f in enumerate(monosets):
    di = eq_degs[i]
    by_deg = {}
    for mm in f:
        by_deg.setdefault(len(mm), 0)
        by_deg[len(mm)] += 1
    for d, cnt in sorted(by_deg.items()):
        if d == 0:
            pools[(i, d)] = [frozenset()]
            pool_sizes[str((i, d))] = 1
            continue
        safe = []
        for combo in itertools.combinations(range(nb), d):
            mp = frozenset(combo)
            if is_safe(mp, di):
                safe.append(mp)
        pools[(i, d)] = safe
        pool_sizes[str((i, d))] = len(safe)
print("  pools built (%.1fs); sizes: min=%d over required, per (i,d) recorded"
      % (time.time() - t0, min(len(v) for v in pools.values())), flush=True)
out["n1_pool_sizes"] = pool_sizes
out["n1_pool_sizes_min"] = min(len(v) for v in pools.values())
flush()

# required counts per (i,d)
required = {}
for i, f in enumerate(monosets):
    for mm in f:
        required[(i, len(mm))] = required.get((i, len(mm)), 0) + 1
out["n1_pool_feasible"] = all(len(pools[key]) >= cnt for key, cnt in required.items())
print("  pool feasibility (pool >= required count everywhere): %s"
      % out["n1_pool_feasible"], flush=True)
if not out["n1_pool_feasible"]:
    shortages = {str(key): (len(pools[key]), cnt)
                 for key, cnt in required.items() if len(pools[key]) < cnt}
    out["n1_pool_shortages"] = shortages
    print("  SHORTAGES: %s" % shortages, flush=True)
flush()

# z point for consistency (seeded, independent of sem solutions)
zrng = random.Random(stable_seed("sig6", "zpoint", n, seed))
zbits = frozenset(v for v in range(nb) if zrng.random() < 0.5)
out["zpoint"] = sorted(zbits)


def eval_at(ms_poly, z):
    return sum(1 for m in ms_poly if m <= z) % 2


def build_n1(trial_seed):
    """One rejection trial: sample from safe pools; then parity-fix at z."""
    rng = random.Random(trial_seed)
    nf = []
    for i, f in enumerate(monosets):
        by_deg = {}
        for mm in f:
            by_deg.setdefault(len(mm), 0)
            by_deg[len(mm)] += 1
        eq = set()
        for d, cnt in sorted(by_deg.items()):
            if d == 0:
                eq.add(frozenset())
                continue
            eq |= set(rng.sample(pools[(i, d)], cnt))
        nf.append(eq)
    # parity fix at z (keep degree histogram; swap within pools)
    swaps = 0
    for i, eq in enumerate(nf):
        if eval_at(eq, zbits) == 0:
            continue
        done = False
        by_deg_i = {}
        for mm in eq:
            by_deg_i.setdefault(len(mm), []).append(mm)
        for d, mons in sorted(by_deg_i.items()):
            if d == 0 or done:
                continue
            for m0 in mons:
                e0 = 1 if m0 <= zbits else 0
                for m1 in pools[(i, d)]:
                    if m1 in eq:
                        continue
                    e1 = 1 if m1 <= zbits else 0
                    if e1 != e0:
                        eq.discard(m0)
                        eq.add(m1)
                        swaps += 1
                        done = True
                        break
                if done:
                    break
        if not done:
            return None, swaps
    return nf, swaps


print("=== N1: rejection trials for D6 column equality ===", flush=True)
n1_ms, n1_trials, n1_swaps, n1_ceq = None, 0, 0, False
t0 = time.time()
for tr in range(1, args.max_trials + 1):
    cand, sw = build_n1(stable_seed("sig6", "n1", n, seed, tr))
    n1_trials = tr
    if cand is None:
        continue
    cov = colset_of(cand, 6)
    if cov == C_sem6:
        n1_ms, n1_swaps = cand, sw
        n1_ceq = True
        break
    if softcap_hit():
        break
out["n1"] = {"trials": n1_trials, "column_set_equal_sem_D6": bool(n1_ceq),
             "parity_swaps": n1_swaps, "construction_s": round(time.time() - t0, 2)}
print("  N1: trials=%d equal=%s swaps=%d (%.1fs)"
      % (n1_trials, n1_ceq, n1_swaps, time.time() - t0), flush=True)
flush()

# N1 determinism: build twice from the SAME successful trial seed
n1_det = None
if n1_ceq:
    tr_win = n1_trials
    c1, _ = build_n1(stable_seed("sig6", "n1", n, seed, tr_win))
    c2, _ = build_n1(stable_seed("sig6", "n1", n, seed, tr_win))
    n1_det = all(c1[i] == c2[i] for i in range(len(c1))) and all(
        n1_ms[i] == c1[i] for i in range(len(n1_ms)))
out["n1"]["determinism_rebuild_identical"] = bool(n1_det)
print("  N1 determinism rebuild identical: %s" % n1_det, flush=True)

# ---- N2: old-style null + parity fix at z
print("=== N2: old-style support-matched null + parity fix ===", flush=True)
n2_ms = boolean_null(monosets, nb, random.Random(stable_seed("null", n, 3, seed)))
# parity fix using global monomial pools (old-style: any monomial of same degree)
for i, eq in enumerate(n2_ms):
    if eval_at(eq, zbits) == 0:
        continue
    done = False
    by_deg_i = {}
    for mm in eq:
        by_deg_i.setdefault(len(mm), []).append(mm)
    for d, mons in sorted(by_deg_i.items()):
        if d == 0 or done:
            continue
        for m0 in mons:
            e0 = 1 if m0 <= zbits else 0
            if e0 == 0:
                continue
            # find a replacement of same degree with eval 0
            found = None
            r2 = random.Random(stable_seed("sig6", "n2fix", n, seed, i, d))
            for _ in range(200):
                m1 = frozenset(r2.sample(range(nb), d))
                if m1 not in eq and not (m1 <= zbits):
                    found = m1
                    break
            if found is not None:
                eq.discard(m0)
                eq.add(found)
                done = True
                break
        if done:
            break

# ---- measure all nulls at D3..D6
def measure_null(name, ms):
    cell = {"null": name, "status": "completed"}
    vv = variety_count(ms)
    cell["variety_size"] = vv
    print("  %s: |V| = %d" % (name, vv), flush=True)
    for D in (3, 4, 5, 6):
        if softcap_hit():
            cell["status"] = "censored_softcap_before_D%d" % D
            flush()
            return cell
        t0 = time.time()
        rec, _, _, _ = analyze_syzygy_space(ms, nb, D, extract=False)
        rec.pop("extra_reps", None)
        rec["sec"] = round(time.time() - t0, 2)
        cell["D%d" % D] = rec
        print("  %s D%d: ncols=%d rank=%d sr_pred=%d def=%d extra=%d (%.1fs)"
              % (name, D, rec["ncols"], rec["rank"], rec["sr_pred"],
                 rec["deficit"], rec["extra"], rec["sec"]), flush=True)
        flush()
    cell["gates"] = {
        "c2_anchor_d3d4d5": bool(all(cell["D%d" % D]["extra"] == 0
                                     and cell["D%d" % D]["rank"] == cell["D%d" % D]["sr_pred"]
                                     for D in (3, 4, 5))),
        "c3_d6_extra_zero": bool(cell["D6"]["extra"] == 0),
        "c3_d6_rank_eq_sr_pred": bool(cell["D6"]["rank"] == cell["D6"]["sr_pred"]),
        "c3_d6_rank_eq_ncols_minus_V": bool(cell["D6"]["rank"] == cell["D6"]["ncols"] - vv),
        "c6_kernel_identity": bool(all(
            cell["D%d" % D]["kernel_dim"] == cell["D%d" % D]["nrows"] - cell["D%d" % D]["rank"]
            and cell["D%d" % D]["extra"] == cell["D%d" % D]["kernel_dim"] - cell["D%d" % D]["rankK"]
            for D in (3, 4, 5, 6))),
    }
    flush()
    return cell


cells = []
# N0: old null determinism rerun (fresh rng, same pinned seed)
n0_ms = boolean_null(monosets, nb, random.Random(stable_seed("null", n, 3, seed)))
cells.append(measure_null("N0_old_pinned", n0_ms))
if n1_ceq:
    c = measure_null("N1_column_matched_consistent", n1_ms)
    c["column_set_equal_sem_D6"] = True
    cells.append(c)
else:
    cells.append({"null": "N1_column_matched_consistent",
                  "status": "construction_failed: no rejection trial achieved "
                            "D6 column equality within %d trials" % n1_trials,
                  "trials": n1_trials})
cells.append(measure_null("N2_consistent_forced", n2_ms))
out["cells"] = cells

out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
print("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]), flush=True)
