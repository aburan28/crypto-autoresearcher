#!/usr/bin/env python3
"""
Blind re-derivation (a) -- Joint J1, TASK-20260904-410404.

Independent code, written WITHOUT reading estimator.py, stage0.py, stage1.py,
stage2.py, runrecord.py, selftest.py, or vacuity-derivation.md (blind_from
list). Derived only from:
  - ledger/proposals/IDEA-20260815-f558e4.yaml claim (B) [definitions of
    q_strict, q_maj] and proof_search_map.baseline_embedding
    (reproduction_check) [the N=23, s=3 statement],
  - experiments/EXP-ECDLP-56ee42/specification.yaml baseline_fixture block
    (the interval-partition rule: fibers {k : k in [j*N/s, (j+1)*N/s)}).

Quantity under test: at N = 23, s = 3, the interval partition of Z/23Z,
q_strict and q_maj, both exact rationals over all 529 ordered pairs.

Definitions used (from the frozen statement, not from any implementation):
  - The group is treated as Z/N (additive), consistent with "R_k = [k]P" and
    R_k + R_l = R_{k+l mod N} in the estimator definition (spec's estimator
    block, permitted for this fixture check since it only requires knowing
    the group law of a cyclic group of order N, not any code).
  - Fiber map v(k) = j  iff  k in [ floor(j*N/s), floor((j+1)*N/s) ),
    for j = 0..s-1, applied over the integer representatives k = 0..N-1.
    (This is the literal reading of specification.yaml's
    "fibers {k : k in [j*23/3, (j+1)*23/3)}"; boundaries are real numbers,
    membership of the integer k is decided by simple comparison, which is
    equivalent to floor() on the real boundary since k is an integer.)
  - q_strict = (1/N^2) * sum over ordered pairs (k,l) of
        1[ the sumset v^{-1}(v(k)) + v^{-1}(v(l)) (mod N) is contained in a
           single fiber ]
    i.e. for a given pair of fiber labels (i,j), EITHER every element of
    A_i + A_j (mod N) lands in one fiber (in which case ALL |A_i|*|A_j| pairs
    with that label pair count), OR none do. This matches the IDEA-f558e4
    claim (B) definition: "the fraction of pairs (R,R') for which the fiber
    of R+R' is FORCED by the pair of fibers (v(R), v(R'))".
  - q_maj = max over functions F: SxS -> S of
        Pr_{k,l uniform in Z/N}[ v(k+l mod N) = F(v(k), v(l)) ]
    computed exactly: for every ordered pair of fiber labels (i,j), tally the
    count of each output fiber m among the |A_i|*|A_j| actual pairs with that
    label pair, take the max count (the best choice of F(i,j) is the
    plurality output), and sum over all s^2 cells; divide by N^2.

Both q_strict and q_maj are computed as exact Python `Fraction`s -- no
floating point comparison anywhere.
"""
from fractions import Fraction
from itertools import product

N = 23
S = 3


def fiber(k: int) -> int:
    # v(k) = j iff k in [floor(j*N/s), floor((j+1)*N/s))
    # equivalent, exact-integer form: j = floor(k*s / N)
    return (k * S) // N


def main() -> None:
    fibers = [fiber(k) for k in range(N)]
    assert len(set(fibers)) == S, f"expected {S} distinct fiber labels, got {set(fibers)}"

    # Build A_j = list of k with fiber(k) == j
    A = {j: [k for k in range(N) if fibers[k] == j] for j in range(S)}
    sizes = {j: len(A[j]) for j in range(S)}
    assert sum(sizes.values()) == N

    # ---- q_strict ----
    # For each ordered (i, j), check whether the sumset A_i + A_j (mod N) is
    # contained within a single fiber. If so, all sizes[i]*sizes[j] pairs are
    # "forced" and contribute to the numerator.
    strict_numerator = 0
    strict_cells = {}
    for i, j in product(range(S), repeat=2):
        sumset_fibers = set()
        for a in A[i]:
            for b in A[j]:
                sumset_fibers.add(fiber((a + b) % N))
                if len(sumset_fibers) > 1:
                    break
            if len(sumset_fibers) > 1:
                break
        forced = len(sumset_fibers) == 1
        strict_cells[(i, j)] = forced
        if forced:
            strict_numerator += sizes[i] * sizes[j]

    q_strict = Fraction(strict_numerator, N * N)

    # ---- q_maj ----
    # For each ordered (i, j), tally the output fiber of every actual pair.
    maj_numerator = 0
    cell_reports = []
    for i, j in product(range(S), repeat=2):
        counts = [0] * S
        for a in A[i]:
            for b in A[j]:
                counts[fiber((a + b) % N)] += 1
        best = max(counts)
        best_F = counts.index(best)
        maj_numerator += best
        cell_reports.append(
            {
                "i": i,
                "j": j,
                "counts": counts,
                "best_F(i,j)": best_F,
                "best_count": best,
            }
        )

    q_maj = Fraction(maj_numerator, N * N)

    print("=== Blind re-derivation (a): N=23, s=3 interval partition ===")
    print(f"fiber sizes: {sizes}")
    print(f"strict-forced cells (i,j): {[k for k, v in strict_cells.items() if v]}")
    print(f"q_strict = {strict_numerator}/{N*N} = {q_strict} = {float(q_strict)}")
    print(f"q_maj    = {maj_numerator}/{N*N} = {q_maj} = {float(q_maj)}")
    print()
    print("Per-cell majority table (i, j, counts-by-output-fiber, argmax F(i,j), best_count):")
    for c in cell_reports:
        print(f"  ({c['i']},{c['j']}): counts={c['counts']} -> F={c['best_F(i,j)']}, best={c['best_count']}")

    recorded_q_maj = Fraction(284, 529)
    recorded_q_strict = Fraction(0, 1)

    print()
    print(f"RECORDED q_maj    = 284/529 = {float(recorded_q_maj)}")
    print(f"COMPUTED q_maj    = {maj_numerator}/{N*N} = {float(q_maj)}")
    print(f"MATCH q_maj: {q_maj == recorded_q_maj}")
    print(f"RECORDED q_strict = 0")
    print(f"COMPUTED q_strict = {strict_numerator}/{N*N} = {float(q_strict)}")
    print(f"MATCH q_strict: {q_strict == recorded_q_strict}")


if __name__ == "__main__":
    main()
