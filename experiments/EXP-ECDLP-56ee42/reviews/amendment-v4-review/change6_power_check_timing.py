"""
Independent feasibility check for V4-CHG-6's N=20-repetition synthetic power
check. Times ONE repetition (1 pre-shuffle-baseline A_noDC + 8 genuine-
shuffle A_noDC draws + 8 reading-2-shuffle A_noDC draws = 17 length-n FFTs,
matching V3-RA-2/V4-CHG-6's own stated method: the ratio needs the
pre-shuffle A_noDC as its denominator, plus 8+8 post-shuffle draws) at each
of T17/T19/T21/T23/T25, then extrapolates x20 to the disclosed T17-T25
fallback schedule (v4's own t27_carve_out_interaction permits T27 to be
marked NOT-COMPUTED if infeasible; T17-T25 is what the regime decision would
then rest on).

Uses ONLY public n from specification.yaml/ladder.json -- no curve
enumeration, no discrete log, no cache -- matching V3-RA-2/V4-CHG-6's own
declared method (synthetic null placement of m0/m1 binary values, not real
curve data). Single-threaded numpy.fft (pocketfft), 4-core sandbox machine.
"""
import time
import numpy as np

LADDER_N = {17: 131113, 19: 525361, 21: 2098321, 23: 8391797, 25: 33557891, 27: 134234689}


def a_nodc(n, v):
    V = np.fft.fft(v)
    return float(np.max(np.abs(V[1:])) / n)


def one_repetition(n):
    m0 = n // 2
    t0 = time.time()
    rng = np.random.default_rng(999)
    v0 = np.zeros(n, dtype=np.float64)
    v0[:m0] = 1.0
    v_placed = v0[rng.permutation(n)]
    _ = a_nodc(n, v_placed)  # pre-shuffle baseline (the ratio's denominator)
    for draw_idx in range(8):
        rng2 = np.random.default_rng(1000 + draw_idx)
        _ = a_nodc(n, v_placed[rng2.permutation(n)])
    for draw_idx in range(8):
        rng3 = np.random.default_rng(2000 + draw_idx)
        _ = a_nodc(n, v_placed[rng3.permutation(n)])
    return time.time() - t0


if __name__ == "__main__":
    grand_total = 0.0
    print(f"{'rung':>5} {'n':>12} {'1 rep (17 FFTs, s)':>20} {'x20 reps (s)':>14} {'x20 reps (min)':>16}")
    for T in [17, 19, 21, 23, 25]:
        n = LADDER_N[T]
        dt = one_repetition(n)
        total_20 = dt * 20
        grand_total += total_20
        print(f"T{T:<4} {n:>12} {dt:>20.4f} {total_20:>14.2f} {total_20/60:>16.2f}")

    print()
    print(f"Grand total, T17-T25, 20 reps each (17 FFTs/rep, single-threaded):")
    print(f"  {grand_total:.1f}s = {grand_total/60:.2f} min = {grand_total/3600:.4f} CPU-hours")
    print()
    print("Compare against this experiment's OWN declared budget "
          "(specification.yaml budget block):")
    print("  wall_clock_seconds_per_run: 7200 (2h) -- 'a run is one stage "
          "invocation over all six rungs'")
    print("  total_cpu_hours: 24 (the WHOLE experiment's budget, all stages)")
    print()
    over_2h_cap = grand_total > 7200
    print(f"T17-T25's 20-rep power check alone ({grand_total:.0f}s) "
          f"{'EXCEEDS' if over_2h_cap else 'stays under'} the 7200s "
          f"per-run cap, even BEFORE T27 and even though T27 is the ONLY "
          f"disclosed infrastructure risk in change_6.")
    print(f"It consumes ~{100*grand_total/3600/24:.1f}% of the entire "
          f"experiment's 24 CPU-hour total budget, for a diagnostic check "
          f"that is not itself one of Stage 0-4.")
    print()
    print("Neither v3 nor v4 states which budget line item (an existing "
          "Stage-N allocation, or a new one) the power check draws from, "
          "or discloses this aggregate-cost risk anywhere -- only T27's "
          "per-rung memory ceiling is disclosed.")
