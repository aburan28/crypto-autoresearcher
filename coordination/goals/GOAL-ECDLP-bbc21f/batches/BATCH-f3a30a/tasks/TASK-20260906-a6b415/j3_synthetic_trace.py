"""
J3 synthetic trace (Red Team, TASK-20260906-a6b415).

Goal: manually trace, using the ACTUAL production classes from
experiments/EXP-ECDLP-612fb1/source_v2/instrument.py (Pool, CountedSelector,
numpy_select), one full round of admission-then-cap on a small hand-crafted
pool, reproducing EXACTLY the per-target admission+cap loop body from
instrument.py::run_arm (lines ~605-676 at the time of this review), with a
print of pool size BEFORE each target's admissions, AFTER each target's
admissions (pre-truncation), and AFTER that target's truncation check.

This is not a re-implementation from scratch: it imports and exercises the
real Pool/CountedSelector/numpy_select classes so the truncation semantics
under test are the production code's own semantics, not a paraphrase of them.
The "targets" and their walks below are hand-picked (not sampled) so the
admission sequence is fully human-auditable.
"""
import os
import sys

SRC = "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-612fb1/source_v2"
sys.path.insert(0, SRC)
import instrument as I  # noqa: E402
import numpy as np


def make_pool(dps, S, h):
    class Snap:
        pass
    snap = Snap()
    snap.dps, snap.S, snap.h, snap.logs = list(dps), list(S), list(h), None
    rng = np.random.default_rng(12345)
    return I.Pool(snap, rng)


def weight_report(pool, W):
    return {d: round(w, 2) for d, w in zip(pool.dps, pool.weights(W))}


def per_admission_cap_round(pool, cap, W, targets):
    """Reproduce instrument.py's per-target admission+cap loop body
    (mode='resel_lower' style: every target here is 'solved', all its walks
    are admitted) with instrumentation printed at each checkpoint."""
    print(f"START OF ROUND: pool size = {len(pool)} (cap = {cap})")
    assert len(pool) <= cap, "pool must not already violate cap at round start (sanity)"
    for ti, walks in enumerate(targets):
        print(f"\n-- target {ti}: admitting {len(walks)} walk(s) {walks} --")
        print(f"   pool size BEFORE this target's admission: {len(pool)}")
        admitted_this_target = 0
        for (dp, length) in walks:
            pool.add_or_credit(dp, float(length), 1)
            admitted_this_target += 1
            print(f"   admitted walk -> dp={dp} length={length}  (pool size now {len(pool)}, "
                  f"BEFORE this target's own truncation check)")
        # -- per-admission cap check (mirrors instrument.py exactly) --
        if admitted_this_target > 0 and len(pool) > cap:
            w_i = pool.weights(W)
            keys_i = np.asarray(pool.keys, dtype=np.int64)
            sel_i = I.CountedSelector()
            order = sel_i.select(w_i, keys_i, cap)
            ref_i = I.numpy_select(w_i, keys_i, cap)
            assert set(order) == set(ref_i), "counted selector disagrees with numpy reference"
            pool.restrict(order)
            print(f"   >>> TRUNCATION FIRED for target {ti}: pool size {len(pool) } after restrict to top-{cap} <<<")
        else:
            print(f"   (no truncation needed for target {ti}: pool size {len(pool)} <= cap {cap})")
        print(f"   pool size AFTER target {ti}'s own admission+truncation checkpoint: {len(pool)}")
        assert len(pool) <= cap, (
            f"BREAKING ARTIFACT: pool size {len(pool)} exceeds cap {cap} at a "
            f"POST-TRUNCATION checkpoint after target {ti} -- S_peak would be dishonest")
    print(f"\nEND OF ROUND: pool size = {len(pool)}  (cap = {cap})")
    return len(pool)


def main():
    W = 4.0  # small toy W for the weight formula S_d + 4 W h_d
    cap = 5

    # Start the pool AT the cap (mirrors the real contract: for r=2 and
    # pool_cap=2T, the pool is generated to exactly r*T = pool_cap entries
    # before any online admission happens).
    dps0 = [100, 101, 102, 103, 105]
    S0 = [10.0, 8.0, 6.0, 4.0, 2.0]
    h0 = [1, 1, 1, 1, 1]
    pool = make_pool(dps0, S0, h0)
    print("initial weights:", weight_report(pool, W))

    # One round, 4 "solved" targets, each admitting a small number of walks.
    # Target 0 and 2 introduce NEW distinct DPs (growing the pool above cap);
    # target 1 only credits an EXISTING DP (no growth); target 3 introduces
    # two new DPs at once (bigger single-target jump), to check the "atomic
    # admission unit is one target's full walk set" reading.
    targets = [
        [(200, 3.0)],                 # target 0: 1 new DP -> pool grows to 6 > cap(5)
        [(101, 1.0)],                 # target 1: existing DP, no growth
        [(201, 9.0)],                 # target 2: 1 new DP -> pool grows above cap again
        [(202, 1.0), (203, 1.0)],     # target 3: 2 new DPs admitted ATOMICALLY together
    ]

    final = per_admission_cap_round(pool, cap, W, targets)
    print("\nFinal pool contents (dp: weight):", weight_report(pool, W))
    print(f"\nRESULT: pool never exceeded cap={cap} at any POST-TRUNCATION (per-target) checkpoint: "
          f"{'CONFIRMED' if final <= cap else 'VIOLATED'}")

    # -------------------------------------------------------------------
    # Now show what the OLD v1 (round-end-only) truncation would have done
    # on the identical target sequence, to make the contrast concrete.
    # -------------------------------------------------------------------
    print("\n\n=== CONTRAST: v1's round-END-ONLY truncation on the SAME target sequence ===")
    pool_v1 = make_pool(dps0, S0, h0)
    peak_v1 = len(pool_v1)
    for ti, walks in enumerate(targets):
        for (dp, length) in walks:
            pool_v1.add_or_credit(dp, float(length), 1)
        peak_v1 = max(peak_v1, len(pool_v1))
        print(f"  after target {ti} (v1: no per-admission truncation): pool size = {len(pool_v1)}")
    print(f"  v1 peak pool size reached WITHIN the round (never checked until round end): {peak_v1}")
    w_v1 = pool_v1.weights(W)
    keys_v1 = np.asarray(pool_v1.keys, dtype=np.int64)
    order_v1 = I.numpy_select(w_v1, keys_v1, cap)
    pool_v1.restrict(order_v1)
    print(f"  v1 pool size AFTER the single round-end truncation: {len(pool_v1)}")
    print(f"  => v1's S_peak for this round would be recorded from the round-end value ({len(pool_v1)}), "
          f"NOT the true within-round peak ({peak_v1}) that was transiently exceeded -- exactly the "
          f"'not applied until round end / measured wrong' defect the amendment (item f) describes, "
          f"reproduced here on a hand-traceable example.")


if __name__ == "__main__":
    main()
