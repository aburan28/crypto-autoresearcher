#!/usr/bin/env sage-python
# -*- coding: utf-8 -*-
"""
EXP-SSI-002 / RUN-SSI-002 -- calibration_probe.py

NC-2 of DEC-20260724-016, executed under the FROZEN contract
experiments/EXP-SSI-002/specification.yaml (sha256 recorded in manifest.yaml).

MEASUREMENT STAGE ONLY.  This file measures; it fits nothing and interprets
nothing.  All fitting, all gates and the extrapolation are done by
fit_analysis.py from raw-timings.json alone.

INVOCATION (contract `environment.sage_invocation`):
    /usr/local/bin/sage -python experiments/EXP-SSI-002/calibration_probe.py ...
Sage is reached ONLY through the `sage` binary.  `import sage` from the system
python3 fails on this host and is never attempted.

What is measured: the per-entry table-construction cost of ONE entry of the
list L of Algorithm 1 of the frozen source SRC-P13-WESOLOWSKI-2026, charging
(1) modular-polynomial evaluation, (2) root finding, (3) the non-backtracking
filter and (4) table insertion, each timed separately and all four totalled.

p <= 2^40 IS NOT CRYPTOGRAPHIC SIZE.  Nothing in this file produces or may be
read as a statement about the NIST-I margin.
"""

import argparse
import hashlib
import json
import math
import os
import resource
import sys
import time

# ---------------------------------------------------------------------------
# Sage startup is OUTSIDE every timed window and is reported separately
# (contract `the_measured_quantity.sage_startup_is_excluded_and_stated_separately`).
_T_STARTUP0 = time.perf_counter()
from sage.all import (GF, EllipticCurve, previous_prime, is_prime, ZZ, RR)
from sage.schemes.elliptic_curves.mod_poly import classical_modular_polynomial as CMP
import sage.schemes.elliptic_curves.mod_poly as _mod_poly_mod
SAGE_STARTUP_SECONDS = time.perf_counter() - _T_STARTUP0

# `from sage.all import *` shadows the stdlib `random`; we import it explicitly
# under a distinct name so the seeded PRNG is unambiguously the stdlib one.
import random as pyrandom

# ---------------------------------------------------------------------------
# Frozen contract constants.  Every one of these is transcribed from
# experiments/EXP-SSI-002/specification.yaml, NOT invented here.
EXPONENTS_LOG2P = [20, 23, 26, 29, 32, 35, 38, 40]      # prime_sweep.exponents_log2p
B_FIX_8_PRIMES = [2, 3, 5, 7]                           # cells.B_settings B-FIX-8
B_FIX_32_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]   # B-FIX-32
ENTRY_TARGET = 1500                                     # cells.entries_per_cell
ADMISSIBLE_MIN_ENTRIES = 300                            # cells.cell_admissibility
PER_CELL_CAP_S = 120.0                                  # budgets.per_cell_cap_seconds
PER_PRIME_CAP_S = 600.0                                 # budgets.per_prime_sub_cap_seconds
TOTAL_CAP_S = 5400.0                                    # budgets.wall_clock_seconds_total
CAL_CAP_S = 300.0                                       # budgets.calibration_control_cap_seconds
NULL_CAP_S = 180.0                                      # budgets.null_control_cap_seconds
DRIFT_DET_CAP_S = 360.0                                 # budgets.drift_and_determinism_cap_seconds
MEMORY_CAP_BYTES = 4 * 1024**3                          # budgets.memory_gb
DOWNSAMPLE_KEEP = 2000                                  # budgets.raw_timing_downsampling_rule
CAL_REPS = 100000                                       # controls CTRL-CAL: at least 1e5
CAL_BATCH = 1000
NULL_REPS = 100000
NULL_BATCH = 1000
SPOT_CHECKS = 50                                        # CTRL-COUNT

# IMPLEMENTATION DECISION (recorded, not in the contract): a ceiling on the
# number of entries produced from a SINGLE starting curve, so that one
# starting curve at large X cannot consume the whole cell cap.  Truncation is
# taken at a round boundary and is RECORDED per curve.
PER_CURVE_ENTRY_CEILING = 6000

CONTRACT_SHA_NOTE = "recorded in manifest.yaml, not asserted here"


# ---------------------------------------------------------------------------
def now():
    return time.perf_counter()


def rss_bytes():
    """Peak RSS of this process so far, in bytes (macOS ru_maxrss is bytes)."""
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes, Linux reports kibibytes.  Detect by platform.
    if sys.platform == "darwin":
        return int(ru)
    return int(ru) * 1024


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    if n % 2:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def percentile(xs, q):
    if not xs:
        return None
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    pos = q * (len(s) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(s) - 1)
    frac = pos - lo
    return s[lo] + frac * (s[hi] - s[lo])


def mad(xs):
    m = median(xs)
    if m is None:
        return None
    return median([abs(x - m) for x in xs])


def stat_block(xs):
    if not xs:
        return {"n": 0, "mean": None, "median": None, "mad": None,
                "p10": None, "p90": None, "min": None, "max": None}
    return {"n": len(xs),
            "mean": sum(xs) / len(xs),
            "median": median(xs),
            "mad": mad(xs),
            "p10": percentile(xs, 0.10),
            "p90": percentile(xs, 0.90),
            "min": min(xs),
            "max": max(xs)}


def seed_for(label):
    """Deterministic PRNG seed derived from a recorded label string."""
    h = hashlib.sha256(label.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


# ---------------------------------------------------------------------------
# Prime selection.  EVERY prime is COMPUTED here by the contract's rule.
# NO prime is hardcoded, transcribed or passed on the command line
# (contract prime_sweep.every_p_is_computed_never_transcribed).
def select_prime(k):
    """Largest prime strictly below 2^k congruent to 3 mod 4, with the number
    of candidate primes rejected by the congruence filter."""
    t0 = now()
    p = previous_prime(ZZ(2) ** k)
    rejected = 0
    while p % 4 != 3:
        p = previous_prime(p)
        rejected += 1
    return {"log2p_target": k, "p": int(p), "candidates_rejected": rejected,
            "selection_seconds": now() - t0,
            "rule": "largest prime strictly below 2^k with p = 3 mod 4 "
                    "(Sage previous_prime with congruence filter)"}


def field_and_E0(p):
    F = GF((p, 2), 'i', modulus=[1, 0, 1])
    E0 = EllipticCurve(F, [1, 0])          # y^2 = x^3 + x, j = 1728
    return F, E0


# ---------------------------------------------------------------------------
# Starting-curve walk.  NOT inside any timed window; cost reported as
# walk_seconds (contract prime_sweep.starting_curves).
#
# IMPLEMENTATION DECISION (recorded): the walk is performed with Velu
# 2-isogenies for BOTH variants, so that V-1 and V-2 cells with the same seed
# start from the SAME curve and the V-1/V-2 comparison is paired.  It also
# keeps the walk inside the F_{p^2}-rational isogeny class of E0, where
# Frobenius acts as a scalar on every torsion subgroup, so all ell+1
# ell-isogenies are F_{p^2}-rational at every step.
def walk_to_start(E0, n_steps, rng):
    t0 = now()
    E = E0
    prev_j = None
    for _ in range(n_steps):
        isos = E.isogenies_prime_degree(2)
        cands = []
        for iso in isos:
            jc = iso.codomain().j_invariant()
            if prev_j is None or jc != prev_j:
                cands.append(iso)
        if not cands:
            cands = isos
        ch = cands[rng.randrange(len(cands))]
        prev_j = E.j_invariant()
        E = ch.codomain()
    return E, now() - t0


# ---------------------------------------------------------------------------
# B settings
def b_setting(bid, p):
    """Return (B_realised, prime_set, rule_string)."""
    if bid == "B-ASY":
        # B = exp((1/3)*sqrt(ln(p/2))) rounded DOWN, contract cells.B_settings
        Bf = math.exp((1.0 / 3.0) * math.sqrt(math.log(p / 2.0)))
        B = int(math.floor(Bf))
        primes = [l for l in range(2, B + 1) if is_prime(l)]
        return B, primes, "floor(exp((1/3)*sqrt(ln(p/2)))) = floor(%.6f)" % Bf
    if bid == "B-FIX-8":
        return 8, list(B_FIX_8_PRIMES), "B = 8 fixed"
    if bid == "B-FIX-32":
        return 32, list(B_FIX_32_PRIMES), "B = 32 fixed"
    raise ValueError(bid)


def X_of(B, p):
    """X = B^{1/2} (p/2)^{1/6}  (frozen source Algorithm 2 line 1)."""
    return math.sqrt(B) * math.pow(p / 2.0, 1.0 / 6.0)


# ---------------------------------------------------------------------------
# ONE neighbour-expansion step.  THE TIMED WINDOW.
#
# Charged, per contract `the_measured_quantity.what_is_charged_and_it_is_everything`:
#   C1  modular polynomial Phi_ell(j(E'), x)      [V-2: E'.isogenies_prime_degree(ell)]
#   C2  finding its roots in F_{p^2}              [V-2: j-invariants of the codomains]
#   C3  the non-backtracking filter
#   C4  building the entry record and inserting it into the table keyed by
#       codomain, including the hash and dedup work
def expand_step_V1(ent, ell, table, entries, paths):
    w0 = time.perf_counter_ns()
    c0 = time.process_time_ns()

    t1 = time.perf_counter_ns()
    phi = CMP(ell, ent["j"])
    t2 = time.perf_counter_ns()
    rts = phi.roots()
    t3 = time.perf_counter_ns()
    # C3 non-backtracking filter: drop ONE occurrence of the j walked in from.
    # Root multiplicities are carried: at a j with extra automorphisms
    # (j = 0, 1728) Phi_ell(j, x) has repeated roots and the number of
    # ell-isogenies is the number of roots WITH MULTIPLICITY, = ell + 1.
    prev = ent["prev_j"]
    children = []
    dropped = 0
    for r, m in rts:
        mm = m
        if dropped == 0 and prev is not None and r == prev:
            mm -= 1
            dropped = 1
        for _ in range(mm):
            children.append(r)
    t4 = time.perf_counter_ns()
    produced = _insert(children, ent, ell, table, entries, paths, None)
    t5 = time.perf_counter_ns()

    w1 = time.perf_counter_ns()
    c1 = time.process_time_ns()
    return {"ell": ell,
            "wall_ns": w1 - w0, "cpu_ns": c1 - c0,
            "c1_ns": t2 - t1, "c2_ns": t3 - t2, "c3_ns": t4 - t3, "c4_ns": t5 - t4,
            "produced": len(produced),
            "roots_distinct": len(rts),
            "roots_with_multiplicity": int(sum(m for _, m in rts)),
            "backtrack_dropped": dropped,
            "poly_degree": int(phi.degree())}, produced


def expand_step_V2(ent, ell, table, entries, paths):
    w0 = time.perf_counter_ns()
    c0 = time.process_time_ns()

    t1 = time.perf_counter_ns()
    isos = ent["E"].isogenies_prime_degree(ell)
    t2 = time.perf_counter_ns()
    codoms = [iso.codomain() for iso in isos]
    js = [C.j_invariant() for C in codoms]
    t3 = time.perf_counter_ns()
    prev = ent["prev_j"]
    children = []
    curves = []
    dropped = 0
    for C, jc in zip(codoms, js):
        if dropped == 0 and prev is not None and jc == prev:
            dropped = 1
            continue
        children.append(jc)
        curves.append(C)
    t4 = time.perf_counter_ns()
    produced = _insert(children, ent, ell, table, entries, paths, curves)
    t5 = time.perf_counter_ns()

    w1 = time.perf_counter_ns()
    c1 = time.process_time_ns()
    return {"ell": ell,
            "wall_ns": w1 - w0, "cpu_ns": c1 - c0,
            "c1_ns": t2 - t1, "c2_ns": t3 - t2, "c3_ns": t4 - t3, "c4_ns": t5 - t4,
            "produced": len(produced),
            "roots_distinct": len(set(js)),
            "roots_with_multiplicity": len(js),
            "backtrack_dropped": dropped,
            "poly_degree": None}, produced


def _insert(children, ent, ell, table, entries, paths, curves):
    """C4: build the entry record and insert it into the table keyed by
    codomain, including the hash and the dedup work."""
    produced = []
    for idx, jc in enumerate(children):
        path = ent["path"] + (jc,)
        if path in paths:            # dedup work is charged
            continue
        paths.add(path)
        e = {"j": jc, "deg": ent["deg"] * ell, "path": path,
             "prev_j": ent["j"], "ell": ell}
        if curves is not None:
            e["E"] = curves[idx]
        entries.append(e)
        bucket = table.get(jc)       # hash work is charged
        if bucket is None:
            table[jc] = [e]
        else:
            bucket.append(e)
        produced.append(e)
    return produced


# ---------------------------------------------------------------------------
def run_algorithm1(E_start, p, B, primes, variant, seeding, X,
                   cell_deadline, entry_ceiling, log):
    """One execution of Algorithm 1 from one starting curve.

    Deviation from the literal text, RECORDED: lines 3-4 as written re-iterate
    over ALL of L at every round i, so an entry already expanded for the same
    ell at an earlier round is expanded again and line 7's set union discards
    the duplicates.  This implementation expands each (psi, ell) pair exactly
    once, by carrying the round's frontier.  It produces the SAME set L and
    removes pure duplicate work that would otherwise inflate the measured
    per-entry cost.
    """
    j0 = E_start.j_invariant()
    entries = []
    table = {}
    paths = set()
    seed0 = {"j": j0, "deg": 1, "path": (j0,), "prev_j": None, "ell": None}
    if variant == "V-2":
        seed0["E"] = E_start

    t_seed0 = now()
    entries.append(seed0)
    paths.add(seed0["path"])
    table[j0] = [seed0]
    seed_seconds = now() - t_seed0
    seed_entries_outside_window = 1     # the identity entry

    steps = []
    expand = expand_step_V1 if variant == "V-1" else expand_step_V2

    # SEED-B: additionally pre-supply the ell_min-neighbours of E, OUTSIDE the
    # timed window (contract GAP_1...SEED_B_first_layer_variant).
    preseeded = []
    if seeding == "SEED-B":
        ell_min = primes[0]
        tb0 = now()
        _rec, produced = expand(seed0, ell_min, table, entries, paths)
        seed_seconds += now() - tb0
        seed_entries_outside_window += len(produced)
        preseeded = list(produced)

    truncated = False
    cap_fired = False
    for ell in primes:
        if X < ell:
            continue
        imax = int(math.floor(math.log(X) / math.log(ell)))
        if seeding == "SEED-B" and ell == primes[0]:
            # layer 1 for ell_min was supplied OUTSIDE the timed window;
            # the timed windows charge only the layers built on top of it.
            frontier = list(preseeded)
            i_start = 2
        else:
            frontier = [e for e in entries if ell * e["deg"] <= X + 1e-9]
            i_start = 1
        for i in range(i_start, imax + 1):
            newf = []
            for e in frontier:
                if ell * e["deg"] > X + 1e-9:
                    continue
                if now() > cell_deadline:
                    cap_fired = True
                    break
                rec, produced = expand(e, ell, table, entries, paths)
                rec["round_i"] = i
                steps.append(rec)
                newf.extend(produced)
                if len(entries) >= entry_ceiling:
                    truncated = True
                    break
            if cap_fired or truncated:
                break
            frontier = newf
            if not frontier:
                break
        if cap_fired or truncated:
            break

    return {"entries": entries, "table": table, "steps": steps,
            "seed_seconds": seed_seconds,
            "seed_entries_outside_window": seed_entries_outside_window,
            "truncated_by_entry_ceiling": truncated,
            "cap_fired": cap_fired,
            "j0": j0}


# ---------------------------------------------------------------------------
def run_cell(cell_id, k, pinfo, bid, variant, seeding, role, phi_build,
             session_deadline, prime_clock, log):
    p = pinfo["p"]
    F, E0 = field_and_E0(p)
    B, primes, brule = b_setting(bid, p)
    X = X_of(B, p)
    n_walk = 2 * int(math.ceil(math.log(p, 2)))
    # The PRNG seed label deliberately EXCLUDES the cell's role, so that the
    # CTRL-DET re-execution of a cell uses the SAME seeds and must reproduce
    # the same entry counts, table sizes and j-invariant sets exactly.
    seed_key = "k%02d|%s|%s|%s" % (k, bid, variant, seeding)

    t_cell0 = now()
    cell_deadline = min(t_cell0 + PER_CELL_CAP_S, session_deadline,
                        prime_clock["start"] + PER_PRIME_CAP_S)
    cpu0 = time.process_time()
    rss0 = rss_bytes()

    # Phi retrieval within the cell (contract precomputation_policy).
    phi_load = {}
    if variant == "V-1":
        for l in primes:
            t = now()
            CMP(l)
            phi_load[str(l)] = now() - t

    all_steps = []
    curves = []
    total_entries = 0
    walk_seconds_total = 0.0
    seed_seconds_total = 0.0
    seed_entries_outside = 0
    table_sizes = []
    jkeys_all = set()
    truncated_curves = 0
    cap_fired = False
    curve_idx = 0
    spot_pool = []

    while True:
        if total_entries >= ENTRY_TARGET:
            break
        if now() > cell_deadline:
            cap_fired = True
            break
        label = "%s|curve%d" % (seed_key, curve_idx)
        sd = seed_for(label)
        rng = pyrandom.Random(sd)
        Es, wsec = walk_to_start(E0, n_walk, rng)
        walk_seconds_total += wsec
        res = run_algorithm1(Es, p, B, primes, variant, seeding, X,
                             cell_deadline, PER_CURVE_ENTRY_CEILING, log)
        n_new = len(res["entries"]) - res["seed_entries_outside_window"]
        # entries CHARGED to timed windows:
        charged = sum(r["produced"] for r in res["steps"])
        all_steps.extend(res["steps"])
        total_entries += charged
        seed_seconds_total += res["seed_seconds"]
        seed_entries_outside += res["seed_entries_outside_window"]
        table_sizes.append(len(res["entries"]))
        for jj in res["table"].keys():
            jkeys_all.add(str(jj))
        if res["truncated_by_entry_ceiling"]:
            truncated_curves += 1
        if res["cap_fired"]:
            cap_fired = True
        curves.append({"curve_index": curve_idx, "seed_label": label, "seed": sd,
                       "start_j": str(res["j0"]), "walk_steps": n_walk,
                       "walk_seconds": wsec,
                       "table_size_L": len(res["entries"]),
                       "entries_charged": charged,
                       "truncated_by_entry_ceiling": res["truncated_by_entry_ceiling"],
                       "cap_fired": res["cap_fired"]})
        # CTRL-COUNT spot-check pool from this curve (sampled deterministically)
        srng = pyrandom.Random(seed_for(label + "|spot"))
        pool = [e for e in res["entries"] if e["prev_j"] is not None]
        if pool:
            take = min(SPOT_CHECKS, len(pool))
            spot_pool.extend(srng.sample(pool, take))
        curve_idx += 1
        if cap_fired:
            break

    # ---- CTRL-COUNT spot checks (outside the timed windows)
    spot = {"checked": 0, "phi_zero_pass": 0, "phi_zero_fail": 0,
            "filter_pass": 0, "filter_fail": 0, "failures": []}
    srng = pyrandom.Random(seed_for(seed_key + "|spotpick"))
    sample = spot_pool if len(spot_pool) <= SPOT_CHECKS else srng.sample(spot_pool, SPOT_CHECKS)
    for e in sample:
        spot["checked"] += 1
        l = e["ell"]
        ok = (CMP(l, e["prev_j"])(e["j"]) == 0)
        if ok:
            spot["phi_zero_pass"] += 1
        else:
            spot["phi_zero_fail"] += 1
            spot["failures"].append({"kind": "phi_nonzero", "ell": int(l),
                                     "parent_j": str(e["prev_j"]), "j": str(e["j"])})
        # non-backtracking: the entry's own j must differ from its grandparent
        gp = e["path"][-3] if len(e["path"]) >= 3 else None
        if gp is None or e["j"] != gp:
            spot["filter_pass"] += 1
        else:
            spot["filter_fail"] += 1
            spot["failures"].append({"kind": "backtrack", "ell": int(l),
                                     "j": str(e["j"])})

    cpu_s = time.process_time() - cpu0
    wall_s = now() - t_cell0
    rss1 = rss_bytes()

    # ---- FULL-DATA summary statistics (computed BEFORE any downsampling)
    per_entry_vals = []
    comp = {"c1": 0, "c2": 0, "c3": 0, "c4": 0}
    win_total_ns = 0
    cpu_total_ns = 0
    by_ell = {}
    for r in all_steps:
        win_total_ns += r["wall_ns"]
        cpu_total_ns += r["cpu_ns"]
        for kk in comp:
            comp[kk] += r[kk + "_ns"]
        if r["produced"] > 0:
            v = r["wall_ns"] / 1e9 / r["produced"]
            per_entry_vals.append(v)
            be = by_ell.setdefault(str(r["ell"]), {"entries": 0, "steps": 0,
                                                   "per_entry": [], "c1": [], "c2": []})
            be["entries"] += r["produced"]
            be["steps"] += 1
            be["per_entry"].append(v)
            be["c1"].append(r["c1_ns"] / 1e9 / r["produced"])
            be["c2"].append(r["c2_ns"] / 1e9 / r["produced"])
        else:
            be = by_ell.setdefault(str(r["ell"]), {"entries": 0, "steps": 0,
                                                   "per_entry": [], "c1": [], "c2": []})
            be["steps"] += 1

    mix1 = {}
    for l, be in by_ell.items():
        mix1[l] = {"entries": be["entries"], "steps": be["steps"],
                   "median_per_entry_s": median(be["per_entry"]),
                   "median_c1_phi_or_isogeny_per_entry_s": median(be["c1"]),
                   "median_c2_rootfind_or_jinv_per_entry_s": median(be["c2"])}

    entries_charged = sum(r["produced"] for r in all_steps)
    T_entry_s_ratio = (win_total_ns / 1e9 / entries_charged) if entries_charged else None
    phi_load_total = sum(phi_load.values()) if phi_load else 0.0
    phi_build_total = sum(phi_build.get(str(l), 0.0) for l in primes) if variant == "V-1" else 0.0

    # ---- downsampling of the RAW per-step records (summaries above use FULL data)
    n_steps_full = len(all_steps)
    kds = 1
    if n_steps_full > DOWNSAMPLE_KEEP:
        kds = int(math.ceil(n_steps_full / float(DOWNSAMPLE_KEEP)))
    kept = all_steps[::kds]

    jkeys_sorted = sorted(jkeys_all)
    jset_sha = hashlib.sha256("\n".join(jkeys_sorted).encode()).hexdigest()

    admissible = entries_charged >= ADMISSIBLE_MIN_ENTRIES
    status = "completed"
    if cap_fired:
        status = "cap_fired"
    if not admissible:
        status = status + "_under_sampled"

    rec = {
        "cell_id": cell_id, "role": role,
        "log2p_target": k, "p": p, "log2p_actual": math.log(p, 2),
        "B_setting": bid, "B_realised": B, "B_rule": brule,
        "prime_set_ell": primes,
        "variant": variant, "seeding": seeding,
        "X": X, "walk_steps": n_walk,
        "starting_curves": len(curves), "curves": curves,
        "entries_charged_to_timed_windows": entries_charged,
        "seed_entries_outside_window": seed_entries_outside,
        "table_size_L_per_curve": table_sizes,
        "table_size_L_total": sum(table_sizes),
        "distinct_j_keys": len(jkeys_all),
        "jset_sha256": jset_sha,
        "timed_window_total_s": win_total_ns / 1e9,
        "timed_window_cpu_s": cpu_total_ns / 1e9,
        "component_split_s": {"c1_phi_eval_or_isogeny": comp["c1"] / 1e9,
                              "c2_root_find_or_jinvariant": comp["c2"] / 1e9,
                              "c3_nonbacktracking_filter": comp["c3"] / 1e9,
                              "c4_entry_build_and_table_insert": comp["c4"] / 1e9},
        "T_entry_s_total_over_entries": T_entry_s_ratio,
        "T_entry_s_stats_over_steps": stat_block(per_entry_vals),
        "walk_seconds": walk_seconds_total,
        "seed_seconds": seed_seconds_total,
        "seed_seconds_inside_timed_window": False,
        "phi_load_seconds": phi_load,
        "phi_load_seconds_total": phi_load_total,
        "phi_generic_build_seconds_total_for_this_prime_set": phi_build_total,
        "peak_rss_bytes_process_before_cell": rss0,
        "peak_rss_bytes_process_after_cell": rss1,
        "peak_rss_delta_bytes": rss1 - rss0,
        "estimated_bytes_per_entry_from_rss_delta":
            ((rss1 - rss0) / entries_charged) if entries_charged else None,
        "wall_seconds": wall_s, "cpu_seconds": cpu_s,
        "terminal_status": status,
        "cap_fired": cap_fired,
        "truncated_curves": truncated_curves,
        "admissible": admissible,
        "mix1_per_ell": mix1,
        "ctrl_count_spot": spot,
        "downsampling": {"pre_downsampling_step_count": n_steps_full,
                         "k": kds, "kept_step_count": len(kept),
                         "note": "SUMMARY STATISTICS ABOVE ARE COMPUTED ON THE "
                                 "FULL UNDOWNSAMPLED STEP LIST."},
        "steps_downsampled": kept,
    }
    return rec


# ---------------------------------------------------------------------------
# CTRL-CAL  (machine calibration) -- interleaved with the primary cells.
def ctrl_cal(k, p, budget_deadline):
    F, _ = field_and_E0(p)
    a = F.random_element()
    b = F.random_element()
    while a.is_zero():
        a = F.random_element()

    def batched(fn, reps, batch):
        vals = []
        done = 0
        while done < reps and now() < budget_deadline:
            t0 = time.perf_counter_ns()
            fn(batch)
            t1 = time.perf_counter_ns()
            vals.append((t1 - t0) / 1e9 / batch)
            done += batch
        return vals, done

    def do_mul(n):
        aa, bb = a, b
        for _ in range(n):
            aa * bb

    def do_inv(n):
        aa = a
        for _ in range(n):
            ~aa

    def do_noop(n):
        for _ in range(n):
            pass

    vm, nm = batched(do_mul, CAL_REPS, CAL_BATCH)
    vi, ni = batched(do_inv, CAL_REPS, CAL_BATCH)
    vn, nn = batched(do_noop, CAL_REPS, CAL_BATCH)
    return {"log2p_target": k, "p": p,
            "t_mul_s": median(vm), "t_mul_reps": nm, "t_mul_batches": len(vm),
            "t_inv_s": median(vi), "t_inv_reps": ni, "t_inv_batches": len(vi),
            "t_noop_s": median(vn), "t_noop_reps": nn, "t_noop_batches": len(vn),
            "t_mul_stats": stat_block(vm), "t_inv_stats": stat_block(vi),
            "t_noop_stats": stat_block(vn),
            "method": "median over %d-op batches of the per-op wall time; "
                      "at least %d repetitions each or the CTRL-CAL cap"
                      % (CAL_BATCH, CAL_REPS)}


# CTRL-NULL: two quantities that CANNOT depend on p.
_NULL_BUF = bytes(range(256)) * 16          # fixed 4 KiB buffer, identical at every p
_NULL_KEYS = list(range(1000))              # fixed integer keys, identical at every p


def ctrl_null(k, p, budget_deadline):
    def batched(fn, reps, batch):
        vals = []
        done = 0
        while done < reps and now() < budget_deadline:
            t0 = time.perf_counter_ns()
            fn(batch)
            t1 = time.perf_counter_ns()
            vals.append((t1 - t0) / 1e9 / batch)
            done += batch
        return vals, done

    def do_sha(n):
        for _ in range(n):
            hashlib.sha256(_NULL_BUF).digest()

    def do_dict(n):
        for _ in range(n):
            d = {}
            for key in _NULL_KEYS:
                d[key] = key
            for key in _NULL_KEYS:
                d[key]

    v1, n1 = batched(do_sha, NULL_REPS, NULL_BATCH)
    v2, n2 = batched(do_dict, 200, 1)
    return {"log2p_target": k, "p": p,
            "null1_sha256_4kib_s": median(v1), "null1_reps": n1,
            "null2_dict_1000_insert_lookup_s": median(v2), "null2_reps": n2,
            "null1_stats": stat_block(v1), "null2_stats": stat_block(v2),
            "note": "NULL-1 hashes a FIXED 4 KiB buffer byte-identical at every p; "
                    "NULL-2 inserts and looks up 1000 FIXED integer keys. Both are "
                    "p-independent by construction."}


# ---------------------------------------------------------------------------
def enforce_artifact_caps(path, per_file_cap=8 * 1024 * 1024):
    """Apply the contract's downsampling rule with k chosen as THE SMALLEST
    INTEGER BRINGING THE FILE UNDER THE CAP (budgets.raw_timing_downsampling_rule).

    The kept list of a cell is already all_steps[::k1]; taking kept[::m] is
    EXACTLY all_steps[::(k1*m)], so raising k by a multiplier is identical to
    having downsampled once at the larger k.  Summary statistics are NOT
    touched: they were computed on the FULL undownsampled step list inside the
    measurement stage and are unaffected.  NO MEASUREMENT IS REPEATED.
    """
    with open(path) as f:
        doc = json.load(f)
    base = [list(c["steps_downsampled"]) for c in doc["cells"]]
    base_k = [c["downsampling"]["k"] for c in doc["cells"]]
    m = 1
    while True:
        for c, b, k1 in zip(doc["cells"], base, base_k):
            c["steps_downsampled"] = b[::m]
            c["downsampling"]["k"] = k1 * m
            c["downsampling"]["kept_step_count"] = len(b[::m])
            c["downsampling"]["cap_enforcement_multiplier_m"] = m
        blob = json.dumps(doc, indent=1, sort_keys=False, default=str)
        if len(blob.encode()) <= per_file_cap or m > 64:
            break
        m += 1
    doc["artifact_cap_enforcement"] = {
        "per_file_cap_bytes": per_file_cap,
        "final_multiplier_m": m,
        "size_bytes_after": len(blob.encode()),
        "rule": "budgets.raw_timing_downsampling_rule: keep every k-th record with k "
                "THE SMALLEST INTEGER BRINGING THE CELL UNDER THE CAP; k and the "
                "pre-downsampling count are recorded per cell.",
        "statement": "SUMMARY STATISTICS WERE COMPUTED ON THE FULL UNDOWNSAMPLED DATA "
                     "IN THE MEASUREMENT STAGE AND ARE UNCHANGED BY THIS STEP. NO "
                     "TRUNCATED JSON DOCUMENT WAS WRITTEN AT ANY POINT: the document is "
                     "always complete and well-formed, only the retained per-step "
                     "sample is thinned. NO MEASUREMENT WAS REPEATED.",
    }
    blob = json.dumps(doc, indent=1, sort_keys=False, default=str)
    with open(path, "w") as f:
        f.write(blob)
    print("artifact cap enforcement: m=%d, size=%d bytes (cap %d)"
          % (m, len(blob.encode()), per_file_cap))
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="run directory")
    ap.add_argument("--git-commit", required=False, default=None)
    ap.add_argument("--git-dirty", required=False, default=None)
    ap.add_argument("--enforce-caps-only", action="store_true",
                    help="apply the downsampling rule to an already written "
                         "raw-timings.json; runs no measurement")
    args = ap.parse_args()
    if args.enforce_caps_only:
        enforce_artifact_caps(os.path.join(args.out, "raw-timings.json"))
        return 0
    if args.git_commit is None or args.git_dirty is None:
        ap.error("--git-commit and --git-dirty are required for a measurement run")

    t_session0 = now()
    session_deadline = t_session0 + TOTAL_CAP_S
    log = []

    def emit(msg):
        line = "[%8.2fs] %s" % (now() - t_session0, msg)
        print(line, flush=True)
        log.append(line)

    emit("EXP-SSI-002 / RUN-SSI-002 measurement stage begins.")
    emit("sage_startup_seconds = %.4f (OUTSIDE every timed window)" % SAGE_STARTUP_SECONDS)
    emit("gc left at its Sage/Python default; not tuned.")

    # ---- primes: COMPUTED, never transcribed
    primes_info = []
    for k in EXPONENTS_LOG2P:
        pi = select_prime(k)
        F, E0 = field_and_E0(pi["p"])
        t = now()
        ss = bool(E0.is_supersingular())
        pi["E0_is_supersingular"] = ss
        pi["supersingularity_check_seconds"] = now() - t
        pi["E0"] = "y^2 = x^3 + x over F_{p^2}, j = 1728"
        primes_info.append(pi)
        emit("prime k=%d p=%d rejected=%d supersingular=%s"
             % (k, pi["p"], pi["candidates_rejected"], ss))
        if not ss:
            emit("STOP FOR THIS PRIME: is_supersingular() False -- environment defect, "
                 "NOT a mathematical finding.")

    pmap = {pi["log2p_target"]: pi for pi in primes_info}
    usable = [k for k in EXPONENTS_LOG2P if pmap[k]["E0_is_supersingular"]]

    # ---- one-time generic Phi_ell build cost (precomputation, charged)
    emit("measuring generic Phi_ell build cost (precomputation_policy)")
    phi_build = {}
    _mod_poly_mod._cache.clear()
    for l in B_FIX_32_PRIMES:
        t = now()
        CMP(l)
        phi_build[str(l)] = now() - t
    emit("phi generic build seconds: " + json.dumps(
        {kk: round(vv, 5) for kk, vv in phi_build.items()}))

    # ---- cell schedule.  ROUND-ROBIN ACROSS PRIMES (config-major, prime-minor)
    # so that a monotone host drift cannot masquerade as a monotone p-dependence.
    schedule = []
    kmin, kmax = usable[0], usable[-1]
    # CTRL-DRIFT start measurements of the two extreme B-FIX-8/V-1/SEED-A cells
    schedule.append(("cell", kmin, "B-FIX-8", "V-1", "SEED-A", "PRIMARY+DRIFT-START"))
    schedule.append(("cell", kmax, "B-FIX-8", "V-1", "SEED-A", "PRIMARY+DRIFT-START"))
    configs = [("B-ASY", "V-1", "SEED-A"),
               ("B-FIX-8", "V-1", "SEED-A"),
               ("B-FIX-32", "V-1", "SEED-A"),
               ("B-FIX-8", "V-2", "SEED-A")]
    for ci, cfg in enumerate(configs):
        for k in usable:
            if ci == 0:
                schedule.append(("cal", k))
                schedule.append(("null", k))
            if cfg == ("B-FIX-8", "V-1", "SEED-A") and k in (kmin, kmax):
                continue          # already run as PRIMARY+DRIFT-START
            schedule.append(("cell", k, cfg[0], cfg[1], cfg[2], "PRIMARY"))
    for k in (kmin, kmax):
        schedule.append(("cell", k, "B-FIX-8", "V-1", "SEED-B", "SEED-B-VARIANT"))
    for k in (kmin, kmax):
        schedule.append(("cell", k, "B-FIX-8", "V-1", "SEED-A", "DRIFT-END+CTRL-DET"))

    cells = []
    cal = []
    nulls = []
    prime_clocks = {k: {"start": now(), "used": 0.0} for k in usable}
    not_reached = []
    cal_used = 0.0
    null_used = 0.0
    drift_used = 0.0
    ctrl_count_gate_fires = 0
    stopped_reason = None

    for item in schedule:
        if now() > session_deadline:
            stopped_reason = "TOTAL WALL-CLOCK BUDGET BREACH (5400 s)"
            not_reached.append(item)
            continue
        if stopped_reason:
            not_reached.append(item)
            continue
        kind = item[0]
        if kind == "cal":
            k = item[1]
            t0 = now()
            r = ctrl_cal(k, pmap[k]["p"], min(now() + (CAL_CAP_S - cal_used), session_deadline))
            cal_used += now() - t0
            cal.append(r)
            emit("CTRL-CAL k=%d t_mul=%.3e t_inv=%.3e t_noop=%.3e (cal budget used %.1fs)"
                 % (k, r["t_mul_s"], r["t_inv_s"], r["t_noop_s"], cal_used))
            continue
        if kind == "null":
            k = item[1]
            t0 = now()
            r = ctrl_null(k, pmap[k]["p"], min(now() + (NULL_CAP_S - null_used), session_deadline))
            null_used += now() - t0
            nulls.append(r)
            emit("CTRL-NULL k=%d null1=%.3e null2=%.3e (null budget used %.1fs)"
                 % (k, r["null1_sha256_4kib_s"], r["null2_dict_1000_insert_lookup_s"], null_used))
            continue

        _, k, bid, variant, seeding, role = item
        cell_id = "k%02d|%s|%s|%s|%s" % (k, bid, variant, seeding, role)
        pc = prime_clocks[k]
        if pc["used"] >= PER_PRIME_CAP_S:
            emit("SKIP %s -- per-prime sub-cap already exhausted" % cell_id)
            not_reached.append(item)
            continue
        if role.startswith("DRIFT-END") and drift_used >= DRIFT_DET_CAP_S:
            emit("SKIP %s -- drift/determinism cap exhausted" % cell_id)
            not_reached.append(item)
            continue
        pc["start"] = now() - pc["used"]
        t0 = now()
        rec = run_cell(cell_id, k, pmap[k], bid, variant, seeding, role,
                       phi_build, session_deadline, pc, log)
        dt = now() - t0
        pc["used"] += dt
        if role.startswith("DRIFT-END"):
            drift_used += dt
        cells.append(rec)
        if rec["ctrl_count_spot"]["phi_zero_fail"] or rec["ctrl_count_spot"]["filter_fail"]:
            ctrl_count_gate_fires += 1
        emit("CELL %-42s entries=%5d L=%6d T_entry=%.3e s wall=%6.2fs rss=%.0fMB %s"
             % (cell_id, rec["entries_charged_to_timed_windows"],
                rec["table_size_L_total"],
                rec["T_entry_s_total_over_entries"] or float('nan'),
                rec["wall_seconds"], rec["peak_rss_bytes_process_after_cell"] / 1e6,
                rec["terminal_status"]))
        if rss_bytes() > MEMORY_CAP_BYTES:
            stopped_reason = "MEMORY CAP BREACH (4 GB)"
            emit("STOP: " + stopped_reason)
        if ctrl_count_gate_fires > 3:
            stopped_reason = ("CTRL-COUNT-GATE fired on more than 3 cells -- "
                              "stopping per stopping_rules (implementation defect)")
            emit("STOP: " + stopped_reason)

    session_wall = now() - t_session0
    out = {
        "schema": "EXP-SSI-002.raw-timings.v1",
        "experiment_id": "EXP-SSI-002", "run_id": "RUN-SSI-002",
        "task_id": "TASK-20260731-001", "goal_id": "GOAL-P13-001",
        "batch_id": "BATCH-002",
        "git_commit": args.git_commit, "git_dirty": args.git_dirty,
        "sage_startup_seconds": SAGE_STARTUP_SECONDS,
        "session_wall_seconds": session_wall,
        "session_cpu_seconds": time.process_time(),
        "budgets": {"wall_clock_seconds_total": TOTAL_CAP_S,
                    "per_prime_sub_cap_seconds": PER_PRIME_CAP_S,
                    "per_cell_cap_seconds": PER_CELL_CAP_S,
                    "calibration_control_cap_seconds": CAL_CAP_S,
                    "null_control_cap_seconds": NULL_CAP_S,
                    "drift_and_determinism_cap_seconds": DRIFT_DET_CAP_S,
                    "memory_gb": 4},
        "budget_used": {"session_wall_seconds": session_wall,
                        "ctrl_cal_seconds": cal_used,
                        "ctrl_null_seconds": null_used,
                        "drift_end_seconds": drift_used,
                        "peak_rss_bytes": rss_bytes(),
                        "per_prime_seconds": {str(k): prime_clocks[k]["used"] for k in usable}},
        "stopped_reason": stopped_reason,
        "primes": primes_info,
        "phi_generic_build_seconds": phi_build,
        "phi_build_caveat": "PARI's polmodular has internal caching that this "
                            "harness cannot clear, so these are the wall times "
                            "actually observed in ascending ell order in a fresh "
                            "process after clearing Sage's own _cache, and are "
                            "order-of-magnitude figures for the retrieval cost.",
        "ctrl_cal": cal,
        "ctrl_null": nulls,
        "cells": cells,
        "cells_not_reached": [list(x) for x in not_reached],
        "schedule_order": [list(x) for x in schedule],
        "gc_policy": "left at the Sage/Python default; not tuned",
        "timing_source": "time.perf_counter_ns (wall) and time.process_time_ns (CPU)",
        "log": log,
    }
    # F_{p^2} elements are serialised via str(); paths are dropped from the raw
    # record (they are internal to the dedup work and are not a metric).
    for c in out["cells"]:
        for s in c["steps_downsampled"]:
            s["ell"] = int(s["ell"])
    with open(os.path.join(args.out, "raw-timings.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=False, default=str)
    emit("raw-timings.json written; session wall %.1f s" % session_wall)
    enforce_artifact_caps(os.path.join(args.out, "raw-timings.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
