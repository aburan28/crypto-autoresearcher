# EXP-SIG-006 Phase B2 — N1 column-matched null via greedy cover + repair.
#
# The rejection sampler (RUN-b) failed 60/60 to hit exact D6 column equality
# (pools are tiny: min pool size 1). This script constructs N1
# deterministically: forced classes (pool==required) taken wholesale, free
# classes filled by seeded greedy set-cover over the sem's D6 sextics, then a
# local swap repair until the null's D6 column set == the sem's EXACTLY
# (equal ncols by construction). Then the standard D3..D6 validation
# (extra, rank vs sr_pred) + |V| ground truth.

import sys, os, time, json, argparse, platform, datetime, itertools, hashlib
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--out', required=True)
p.add_argument('--n', type=int, default=9)
p.add_argument('--seed', type=int, default=1)
p.add_argument('--soft-cap', type=int, default=1400)
args = p.parse_args()

EXPDIR = Path(args.out).resolve().parents[2]
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))

t_start = time.time()
out = {
    "experiment": "EXP-SIG-006", "phase": "B2_N1_greedy_repair",
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


def softcap_hit():
    return (time.time() - t_start) > args.soft_cap


n, seed = args.n, args.seed
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


C_sem6 = colset_of(monosets, 6)
sextics_sem6 = set(m for m in C_sem6 if len(m) == 6)
print("sem D6 ncols=%d sextics=%d" % (len(C_sem6), len(sextics_sem6)), flush=True)


def is_safe(mp, di):
    md = 6 - len(mp)
    if md > 6 - di:
        return True
    rest = [v for v in range(nb) if v not in mp]
    for combo in itertools.combinations(rest, md):
        if (mp | frozenset(combo)) not in sextics_sem6:
            return False
    return True


def sextic_upset(mp, di):
    """Sextics reachable from mp at D6 in an eq of degree di."""
    md = 6 - len(mp)
    if md > 6 - di:
        return set()
    rest = [v for v in range(nb) if v not in mp]
    return set(mp | frozenset(c) for c in itertools.combinations(rest, md))


# pools per (i,d)
pools = {}
required = {}
for i, f in enumerate(monosets):
    di = eq_degs[i]
    by_deg = {}
    for mm in f:
        by_deg.setdefault(len(mm), 0)
        by_deg[len(mm)] += 1
    for d, cnt in sorted(by_deg.items()):
        required[(i, d)] = cnt
        if d == 0:
            pools[(i, d)] = [frozenset()]
        else:
            pools[(i, d)] = [frozenset(c) for c in itertools.combinations(range(nb), d)
                             if is_safe(frozenset(c), di)]

rng = random.Random(stable_seed("sig6", "n1greedy", n, seed))

# upset map for every pool monomial (per class)
upset_map = {}
classes = sorted(required.keys())
for key in classes:
    i, d = key
    di = eq_degs[i]
    for mp in pools[key]:
        upset_map[(key, mp)] = sextic_upset(mp, di)

# greedy construction
chosen = {key: ([] if len(pools[key]) > required[key] else list(pools[key]))
          for key in classes}
covered = set()
for key in classes:
    for mp in chosen[key]:
        covered |= upset_map[(key, mp)]

free_classes = [key for key in classes if len(pools[key]) > required[key] and required[key] > 0]
rng.shuffle(free_classes)
for key in free_classes:
    need = required[key]
    pool = list(pools[key])
    rng.shuffle(pool)
    picked = []
    for _ in range(need):
        best, best_gain = None, -1
        for mp in pool:
            if mp in picked:
                continue
            g = len(upset_map[(key, mp)] - covered)
            if g > best_gain:
                best, best_gain = mp, g
                if g == 0 and best is not None:
                    break
        picked.append(best)
        covered |= upset_map[(key, best)]
    chosen[key] = picked

uncovered = sextics_sem6 - covered
print("greedy: uncovered after greedy = %d" % len(uncovered), flush=True)

# local swap repair
n_rep = 0
t0 = time.time()
for s in sorted(uncovered, key=lambda m: tuple(sorted(m))):
    done = False
    # candidate donors: safe monomials m subseteq s whose D6 upset CONTAINS s
    for key in classes:
        i, d = key
        if d == 0 or d > 6:
            continue
        di = eq_degs[i]
        cands = [mp for mp in pools[key]
                 if mp <= s and mp not in chosen[key]
                 and s in sextic_upset(mp, di)]
        rng.shuffle(cands)
        for mp in cands:
            up_mp = upset_map[(key, mp)]
            # find a chosen monomial whose removal loses only sextics
            # re-covered by mp (or with count >= 2)
            for m0 in chosen[key]:
                up0 = upset_map[(key, m0)]
                # check: every sextic in up0 is either covered by someone
                # else or in up_mp
                ok = True
                for x in up0:
                    if x in up_mp:
                        continue
                    # count other coverers
                    cnt = 0
                    for key2 in classes:
                        for m2 in chosen[key2]:
                            if key2 == key and m2 == m0:
                                continue
                            if x in upset_map[(key2, m2)]:
                                cnt += 1
                                break
                        if cnt:
                            break
                    if cnt == 0:
                        ok = False
                        break
                if ok:
                    chosen[key].remove(m0)
                    chosen[key].append(mp)
                    n_rep += 1
                    done = True
                    break
            if done:
                break
        if done:
            break
    if not done:
        print("  REPAIR FAILED for sextic %s" % sorted(s), flush=True)
print("repair swaps: %d (%.1fs)" % (n_rep, time.time() - t0), flush=True)

n1_ms = []
for i, f in enumerate(monosets):
    eq = set()
    for key in classes:
        if key[0] == i:
            eq |= set(chosen[key])
    n1_ms.append(eq)

cov_n1 = colset_of(n1_ms, 6)
ceq = (cov_n1 == C_sem6)
print("N1 column equality after repair: %s (ncols %d vs %d)"
      % (ceq, len(cov_n1), len(C_sem6)), flush=True)
out["n1_construction"] = {
    "method": "greedy cover + local swap repair",
    "repair_swaps": n_rep,
    "column_set_equal_sem_D6": bool(ceq),
    "ncols_n1_D6": len(cov_n1), "ncols_sem_D6": len(C_sem6),
    "n_free_classes": len(free_classes),
    "n_forced_classes": len(classes) - len(free_classes),
    "histogram_match": bool(all(len(n1_ms[i]) == len(monosets[i])
                                for i in range(len(monosets)))),
}
flush()

# variety ground truth
import numpy as np
P = np.arange(2 ** nb, dtype=np.uint32)
sol = np.ones(2 ** nb, dtype=bool)
for f in n1_ms:
    acc = np.zeros(2 ** nb, dtype=bool)
    for m in f:
        mm = np.uint32(0)
        for v in m:
            mm |= np.uint32(1 << v)
        acc = np.logical_xor(acc, (P & mm) == mm)
    sol &= ~acc
vv = int(sol.sum())
print("N1 |V| = %d" % vv, flush=True)

cell = {"null": "N1_column_matched", "variety_size": vv,
        "column_set_equal_sem_D6": bool(ceq), "status": "completed"}
for D in (3, 4, 5, 6):
    if softcap_hit():
        cell["status"] = "censored_softcap_before_D%d" % D
        break
    t0 = time.time()
    rec, _, _, _ = analyze_syzygy_space(n1_ms, nb, D, extract=False)
    rec.pop("extra_reps", None)
    rec["sec"] = round(time.time() - t0, 2)
    cell["D%d" % D] = rec
    print("  N1 D%d: ncols=%d rank=%d sr_pred=%d def=%d extra=%d (%.1fs)"
          % (D, rec["ncols"], rec["rank"], rec["sr_pred"], rec["deficit"],
             rec["extra"], rec["sec"]), flush=True)
    flush()
if "D6" in cell:
    cell["gates"] = {
        "c2_anchor_d3d4d5": bool(all(cell["D%d" % D]["extra"] == 0
                                     and cell["D%d" % D]["rank"] == cell["D%d" % D]["sr_pred"]
                                     for D in (3, 4, 5))),
        "c3_d6_extra_zero": bool(cell["D6"]["extra"] == 0),
        "c3_d6_rank_eq_sr_pred": bool(cell["D6"]["rank"] == cell["D6"]["sr_pred"]),
        "c3_d6_rank_eq_ncols_minus_V": bool(cell["D6"]["rank"] == cell["D6"]["ncols"] - vv),
        "c3_d6_ncols_eq_sem": bool(cell["D6"]["ncols"] == len(C_sem6)),
    }
out["cells"] = [cell]
out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
print("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]), flush=True)
