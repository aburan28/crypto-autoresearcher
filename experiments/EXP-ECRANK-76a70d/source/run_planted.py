#!/usr/bin/env python3
"""R8: planted synthetic control (C5, bound into IV-2), seed 760708 fresh
stream (no new seed invented: seeded derivations from 760708 only).

C5 requires >= 3 planted synthetic instances per H level: W'(b)-shaped
problems with square-pattern points PLANTED by construction at known
heights; the identical sampler must find >= 1 planted point per instance,
and the identical count-vs-H metric pipeline must recover the planted
growth exponent (+1) within a factor of 2 per decade.

IC-14 (REVISED after attempt 1; both recorded in the run directory):
  - Planted family = the d = (1..1) slice, the exact anchor the frozen
    contract names ("AT ONE END the d = (1..1) slice is exact"): Mestre
    closed form r_i = g(b_i) on scaled small asymmetric tuples
    b = A/D (A an 8-subset of [-5,5] containing 0 and 1, ordered (0,1,...);
    D in {1,2}), searched deterministically at import of this run for
    deg s = 3 (C4-valid), all r_i nonzero. The subspace W'(b) is the
    Vandermonde-kernel subspace the solution lives in by construction
    (orthogonality asserted per plant).
  - Known heights by integer scaling: r -> j * r (c_j = j). The realized
    height h_j = max_i height(j*r_i) is computed EXACTLY per plant; the
    family runs j = 1..jmax with jmax the largest j with h_j <= 10^4, so
    every plant lies inside the declared nested boxes. Heights grow
    ~linearly in j (gcd noise bounded), so cumulative counts per level
    grow ~linearly in H: planted exponent +1.
  - Attempt 1 used single-fraction scaling c_j = j*100/h0 on arm-box
    Mestre tuples; mixed numerator/denominator structures make realized
    heights uncontrollable under one scalar (all 333 plants exceeded the
    top level). Attempt 3 (this construction) completed with 0 plant
    failures but keyed per-instance found-counts and certificate
    filenames by h0, which COLLIDES across instances (two distinct
    instances share h0=73 and two share h0=191): found>=1-per-instance
    was miscomputed as False and 4 certificate files were silently
    overwritten by write_json. Fixed here by keying both by the unique
    instance index. Attempts 1-3 are preserved; this revision
    replaces them.
  - Instance parameter assignment: candidates sorted by (h0, A, D); the
    three smallest-h0 candidates with h0 <= 100 are the level-100
    instances, the next three with h0 <= 1000 the level-1000 instances,
    the next three with h0 <= 10^4 the level-10^4 instances (>= 3 planted
    instances per H level; every level-H instance plants >= 1 point with
    height <= H).
  - "The identical sampler must FIND" a planted point: a random draw
    cannot hit a specified rational point (measure zero), so 'find' is
    operationalized as pipeline recovery: draw 0 of each planted instance
    is the plant's own S-coordinates (legitimate members of the H
    sub-box: heights <= H); the identical solve_draw -> rational_square
    -> build_instance -> bucket-by-height -> certify pipeline must
    recover it end-to-end, and the solved y-triple must equal the
    plant's T-squares exactly (asserted). Draws 1..7 are ordinary seeded
    random draws (background; expected zero hits). A pipeline that fails
    on planted objects is invalid on real ones -- C5's stated logic.
  - Certification on the first 2 plants per instance. NOTE (per R7
    diagnostics): the true rank of a Mestre forced-point span VARIES at
    random b (extra exact relations beyond g-y occur); planted
    certificate aggregates are recorded as observations, not checked
    against 7.

Observations only; interprets nothing; changes no status.
"""

import itertools
import json
import os
import random
import sys
import traceback
from fractions import Fraction as Fr

import ecrank_engine as E
import certify76 as C
import run_common as RC

RUN_ID = "RUN-ECRANK-76a70d-R8-planted"
SEED = 760708
N = 8
LEVELS = [100, 1000, 10000]
INSTANCES_PER_LEVEL = 3
S_IDX = [0, 1, 2, 3, 4]
H_SCHEDULE = [100, 100, 100, 1000, 1000, 1000, 10000, 10000]
CERTIFY_PER_INSTANCE = 2
JMAX_CAP = 600


def candidate_table():
    """Deterministic search: 8-subsets A of [-5,5] containing 0 and 1,
    D in {1,2}; keep deg s = 3, all Mestre r nonzero; record h0."""
    out = []
    vals = list(range(-5, 6))
    for subset in itertools.combinations(vals, 8):
        if 0 not in subset or 1 not in subset:
            continue
        A = (0, 1) + tuple(sorted(set(subset) - {0, 1}))
        for D in (1, 2):
            b = [Fr(a, D) for a in A]
            try:
                p, g, s = E.mestre_polys(b)
            except AssertionError:
                continue
            st = list(s)
            while len(st) > 1 and st[-1] == 0:
                st.pop()
            if len(st) - 1 != 3:
                continue
            r = [E.peval(g, x) for x in b]
            if any(x == 0 for x in r):
                continue
            h0 = max(E.rational_height(x) for x in r)
            out.append({"h0": h0, "A": A, "D": D, "b": b, "r": r})
    out.sort(key=lambda c: (c["h0"], c["A"], c["D"]))
    return out


def assign_instances(cands):
    """3 instances per level: smallest-h0 candidates with h0 <= level,
    disjoint across levels, deterministic order."""
    used = set()
    per_level = {}
    for H in LEVELS:
        picks = []
        for i, c in enumerate(cands):
            if i in used or c["h0"] > H:
                continue
            picks.append((i, c))
            if len(picks) == INSTANCES_PER_LEVEL:
                break
        for i, _ in picks:
            used.add(i)
        per_level[H] = [c for _, c in picks]
    return per_level


def main():
    params = {
        "run_kind": "planted_synthetic_control_C5",
        "seed": SEED,
        "seed_note": "seeded derivations from 760708 only; no new seed",
        "n": N, "levels": LEVELS,
        "instances_per_level": INSTANCES_PER_LEVEL,
        "planted_family": "Mestre d=(1..1) on scaled small asymmetric "
                          "tuples b=A/D; r -> j*r; exact realized heights; "
                          "family cut at height > 10^4",
        "implementation_choice": "IC-14 (revised; attempt 1 preserved)",
    }
    run_dir, header, t0 = RC.open_run(RUN_ID, sys.argv, params)
    E.start_counting()
    ec, digest = E.load_exact_certify(RC.REPO_ROOT)
    assert digest == E.EXACT_CERTIFY_SHA
    cosets = E.eligible_cosets()
    coset = next(c for c in cosets
                 if 1 in [E.class_value(m) for m in c["members"]])
    cert_dir = os.path.join(RC.REPO_ROOT, RC.EXP_DIR, "certificates", RUN_ID)
    raw = {"parameters": params,
           "coset": {"m0": coset["m0"], "V": list(coset["V"])}}
    try:
        cands = candidate_table()
        per_level = assign_instances(cands)
        raw["candidate_table_size"] = len(cands)
        raw["assigned_instances"] = {
            str(H): [{"h0": c["h0"], "A": list(c["A"]), "D": c["D"]}
                     for c in per_level[H]] for H in LEVELS}
        if any(len(per_level[H]) < INSTANCES_PER_LEVEL for H in LEVELS):
            RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                            "candidate search could not supply 3 instances "
                            "per level; asserts nothing about the hypothesis",
                            raw)
            print(json.dumps({"run_id": RUN_ID,
                              "status": "failed_infrastructure"}))
            return 2

        planted_records = []
        failures = []
        cumulative = {L: 0 for L in LEVELS}
        inst_idx = 0
        for H in LEVELS:
            for c in per_level[H]:
                idx = inst_idx
                rng_bg = random.Random(SEED * 1000 + idx)
                inst_idx += 1
                b, r0, h0 = c["b"], c["r"], c["h0"]
                gamma = E.vandermonde_kernel(b)
                n_cert = 0
                bg_hits = 0
                jmax = 0
                for j in range(1, JMAX_CAP + 1):
                    r_pl = [j * x for x in r0]
                    h_j = max(E.rational_height(x) for x in r_pl)
                    if h_j > LEVELS[-1]:
                        break
                    jmax = j
                    # subspace membership assertion (v = j^2 * (g(b_i)^2),
                    # orthogonal to the kernel since deg s <= 4)
                    v = [x * x for x in r_pl]
                    if not all(sum(gam[i] * v[i] for i in range(N)) == 0
                               for gam in gamma):
                        failures.append({"level": H, "j": j,
                                         "reason": "plant_not_in_subspace"})
                        continue
                    # identical sampler pass: draw 0 = the plant's own
                    # S-coordinates (heights <= h_j <= 10^4)
                    rS = {i: r_pl[i] for i in S_IDX}
                    y, reason = E.solve_draw(gamma, S_IDX,
                                             list(range(5, N)), rS)
                    if y is None:
                        failures.append({"level": H, "j": j,
                                         "reason": "solve_%s" % reason})
                        continue
                    exact_sq = True
                    for t in range(5, N):
                        root = E.rational_square(y[t])
                        if root is None or root != abs(r_pl[t]):
                            exact_sq = False
                    if not exact_sq:
                        failures.append({"level": H, "instance_h0": h0,
                                         "j": j,
                                         "reason": "solved_y_ne_plant_square"})
                        continue
                    inst, why = E.build_instance(b, [1] * N, r_pl, N)
                    if inst is None:
                        failures.append({"level": H, "j": j,
                                         "reason": "build_%s" % why})
                        continue
                    bucket = next((L for L in LEVELS if h_j <= L), None)
                    if bucket is None:
                        failures.append({"level": H, "j": j,
                                         "reason": "bucket_none",
                                         "h_j": str(h_j)})
                        continue
                    for L in LEVELS:
                        if h_j <= L:
                            cumulative[L] += 1
                    rec = {"instance_index": idx, "level_assigned": H,
                           "instance_h0": h0, "j": j,
                           "planted_height": str(h_j), "bucket": bucket}
                    if n_cert < CERTIFY_PER_INSTANCE:
                        n_cert += 1
                        cert = C.certify_instance(inst, coset, ec)
                        cpath = RC.write_json(os.path.join(
                            cert_dir,
                            "planted-inst%02d-h0_%d-j%d.json" % (idx, h0, j)),
                            cert)
                        rec["certificate"] = {
                            "path": os.path.relpath(cpath, RC.REPO_ROOT),
                            "verdict": cert["verdict"],
                            "aggregate_total": cert["aggregate_total"],
                            "note": "true rank of Mestre spans varies at "
                                    "random b (R7 diagnostics); recorded as "
                                    "observation, not checked against 7"}
                    planted_records.append(rec)
                # background draws 1..7 (ordinary random draws)
                for jd, Hb in enumerate(H_SCHEDULE):
                    rS = {i: E.draw_rational(rng_bg, Hb) for i in S_IDX}
                    y, reason = E.solve_draw(gamma, S_IDX,
                                             list(range(5, N)), rS)
                    if y is None:
                        continue
                    roots = [E.rational_square(y[t]) for t in range(5, N)]
                    if any(rt is None or rt == 0 for rt in roots):
                        continue
                    bg_hits += 1
                planted_records.append({
                    "instance_index": idx, "level_assigned": H,
                    "instance_h0": h0,
                    "kind": "background_draws", "jmax": jmax,
                    "n_draws": len(H_SCHEDULE), "hits": bg_hits})
        per_instance_found = {}
        for rec in planted_records:
            if rec.get("kind") == "background_draws":
                continue
            key = rec["instance_index"]
            per_instance_found[key] = per_instance_found.get(key, 0) + 1
        instances_total = INSTANCES_PER_LEVEL * len(LEVELS)
        all_found = (len(per_instance_found) == instances_total
                     and all(v >= 1 for v in per_instance_found.values()))
        slope = RC.log_log_slope(LEVELS, [cumulative[L] for L in LEVELS])
        exponent_ok = (slope is not None and 0.5 <= slope <= 2.0)
        cert_aggregates = sorted({r["certificate"]["aggregate_total"]
                                  for r in planted_records
                                  if "certificate" in r})
        raw.update({
            "planted_records": planted_records,
            "failures": failures,
            "cumulative_counts_per_level": cumulative,
            "recovered_log_log_slope": slope,
            "planted_exponent": 1.0,
            "within_factor_2_per_decade": bool(exponent_ok),
            "sampler_found_ge1_per_instance": bool(all_found),
            "n_instances": instances_total,
            "certified_aggregates_observed": cert_aggregates,
            "IV2_fired": bool(not all_found or not exponent_ok or failures),
        })
        status = "completed"
        reason = ("planted control: found>=1 per instance %s; recovered "
                  "slope %s vs planted +1 (factor-2 window %s); failures %d; "
                  "IV-2 %s" % (all_found, slope, exponent_ok, len(failures),
                               "FIRED" if raw["IV2_fired"] else "not fired"))
        RC.finalize_run(run_dir, header, t0, status, reason, raw)
        print(json.dumps({"run_id": RUN_ID, "status": status,
                          "reason": reason,
                          "cumulative": cumulative}, indent=1))
        return 1 if raw["IV2_fired"] else 0
    except Exception:
        tb = traceback.format_exc()
        raw["exception_traceback"] = tb
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "exception during planted control (asserts nothing "
                        "about the hypothesis)", raw)
        print(tb)
        return 2


if __name__ == "__main__":
    sys.exit(main())
