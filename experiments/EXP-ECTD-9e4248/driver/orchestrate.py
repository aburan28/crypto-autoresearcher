"""
orchestrate.py -- shared pipeline used by both run_impl.py (1-edge smoke) and
run_screen.py (>=8-edge screen): build vertical edges (with seed-policy retries on
construction failure, recorded as infrastructure per spec.replication.seed_policy),
run CTRL-COORDINATE-NULL on a subsample, CTRL-GLV-CHANNEL once, CTRL-PERMUTATION
across the completed vertical-edge sample, and apply the frozen decision table.
"""
import random
import time

from .reused import analysis
from . import vertical as V, decision as D

LOW_METER = analysis.LOW_METER
ALL_METERS = analysis.ALL_PRIMARY


def build_edges_with_retries(master_seeds, n_needed, fb_size, gb_budget, macaulay_cap,
                              bit_candidates, budget, per_pair_attempts=5000,
                              max_extra_seeds=8):
    """Attempt one vertical edge per master seed; on infra failure, draw an
    additional seed (spec.replication.seed_policy) up to max_extra_seeds beyond the
    master list, recording every attempt (never silently retrying without a
    record). Stops early if the wall-clock budget is exceeded (resource_incomplete
    territory) or n_needed edges are completed."""
    attempts_log = []
    completed = []
    extra_seed_pool = iter(range(900001, 900001 + max_extra_seeds))
    seeds_to_try = list(master_seeds)
    idx = 0
    while idx < len(seeds_to_try) and len(completed) < n_needed:
        if budget.exceeded():
            attempts_log.append({"note": "wall_clock_budget_exceeded_stopping_early"})
            break
        seed = seeds_to_try[idx]
        idx += 1
        t0 = time.time()
        edge = V.build_vertical_edge(seed, fb_size, gb_budget, macaulay_cap, bit_candidates,
                                      per_pair_attempts=per_pair_attempts)
        elapsed = time.time() - t0
        attempts_log.append({"seed": seed, "status": edge["status"], "elapsed_s": elapsed,
                              "reason": edge.get("reason")})
        if edge["status"] == "ok":
            completed.append(edge)
        else:
            try:
                extra = next(extra_seed_pool)
                seeds_to_try.append(extra)
            except StopIteration:
                pass
    return completed, attempts_log


def permutation_stability_all(completed_edges, rng):
    records = []
    for e in completed_edges:
        rec = {}
        for m in ALL_METERS:
            key = m if m != LOW_METER else m + "_ratio_high_is_anomalous"
            rec[key] = e["ratios"][m] if e["ratios"][m] != float("inf") else None
        records.append(rec)
    results = {}
    for m in ALL_METERS:
        key = m if m != LOW_METER else m + "_ratio_high_is_anomalous"
        results[m] = analysis.permutation_stability_check(records, key, rng, n_trials=5)
    return results


FROZEN_MIN_VERTICAL_EDGES = 8  # spec.inputs.min_vertical_edges -- NEVER varied per run;
# the decision table's resource_incomplete / continuity_scoped / etc. conditions are
# written against this frozen threshold, not against however many edges a given run
# (e.g. the 1-edge smoke) happens to attempt building. Conflating the two was a bug
# caught after RUN-ECTD-9e4248-impl's first execution (it produced continuity_scoped
# off n=1 because min_vertical_edges had been passed through as n_needed=1) -- fixed
# here, recorded per AGENTS.md rule 4, and the defective first run kept in the ledger
# marked invalid rather than deleted (see RUN-ECTD-9e4248-impl-v1-bug-invalid/).


def run_pipeline(master_seeds, n_needed, budget, rng_seed=999,
                  fb_size=8, gb_budget=None, macaulay_cap=6,
                  bit_candidates=None, coordinate_null_subsample=2,
                  per_pair_attempts=5000, max_extra_seeds=8):
    gb_budget = gb_budget or {"max_pairs": 20000, "max_degree": 60, "wall_seconds": 60.0}
    bit_candidates = bit_candidates or list(range(40, 45))
    rng = random.Random(rng_seed)

    t0 = time.time()
    completed, attempts_log = build_edges_with_retries(
        master_seeds, n_needed, fb_size, gb_budget, macaulay_cap, bit_candidates,
        budget, per_pair_attempts=per_pair_attempts, max_extra_seeds=max_extra_seeds)
    edges_elapsed = time.time() - t0

    # CTRL-END-RING-CERTIFICATE tally
    end_ring_fail_count = sum(1 for e in completed if not e["certificate"]["verified"])

    # CTRL-COORDINATE-NULL on a subsample of vertical-edge curves (floor curves)
    coord_null_receipts = []
    for e in completed[:coordinate_null_subsample]:
        rec = V.coordinate_null_check(e["floor"]["a"], e["floor"]["b"], e["p"],
                                       random.Random(rng.randrange(1 << 30)),
                                       fb_size, gb_budget, macaulay_cap)
        rec["seed"] = e["seed"]
        coord_null_receipts.append(rec)

    # CTRL-GLV-CHANNEL (once per run)
    glv = V.glv_instrument(random.Random(rng.randrange(1 << 30)), fb_size, gb_budget, macaulay_cap,
                            target_bits=bit_candidates[0])

    # CTRL-PERMUTATION
    perm_results = permutation_stability_all(completed, random.Random(rng.randrange(1 << 30))) if completed else {}

    decision_result = D.decide(
        completed_edges=completed, all_edges_attempted=attempts_log,
        min_vertical_edges=FROZEN_MIN_VERTICAL_EDGES, end_ring_cert_fail_count=end_ring_fail_count,
        glv_result=glv, permutation_results=perm_results,
    )

    # CTRL-NO-CLASS-INVARIANT-ENDPOINT: structural N/A unless discontinuity fired
    if decision_result["decision_branch"] == "discontinuity_nominates_endpoint":
        ctrl_no_class_invariant = {"status": "APPLIED", "note": "not implemented in this "
                                    "driver run -- would require embedding-degree/anomalous/"
                                    "smooth-order detectors on the nominated endpoint; NOT "
                                    "run because this is a toy-scale measurement run and no "
                                    "such detector was built; recorded as a genuine gap, not "
                                    "silently passed"}
    else:
        ctrl_no_class_invariant = {"status": "structural_N/A",
                                    "note": "discontinuity_nominates_endpoint did not fire; "
                                    "this control's precondition never arose (per "
                                    "DEC-20260806-4a9604 finding F-2's disposition, recorded "
                                    "explicitly rather than left unrecorded)"}

    return {
        "completed_edges": completed,
        "attempts_log": attempts_log,
        "edges_elapsed_s": edges_elapsed,
        "end_ring_fail_count": end_ring_fail_count,
        "coordinate_null_receipts": coord_null_receipts,
        "glv_instrument": glv,
        "permutation_results": perm_results,
        "decision_result": decision_result,
        "ctrl_no_class_invariant_endpoint": ctrl_no_class_invariant,
    }
