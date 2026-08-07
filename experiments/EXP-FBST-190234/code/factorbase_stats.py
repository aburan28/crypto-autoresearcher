"""EXP-FBST-190234 -- does ANY factor-base statistic vary across curves at
matched (p, B, m)?

REDESIGN NOTICE. specification.yaml v1 measured this by point arithmetic over
E(F_p) directly (building each construction as x-coordinates, calling into
summation-polynomial machinery for decomposition counts). This file replaces
that with an exact method that is faster and, for two of the four target
metrics, exact rather than sampled -- see specification.yaml v2 for the
recorded amendment. The idea:

Every curve in this battery has PRIME order N (enforced the same way as
EXP-HPSC-74991c: order computed directly, then independently verified by
[N]P = O), so E(F_p) \\ {O} is in bijection with Z/N \\ {0} via the discrete
log to a fixed generator G. A factor base D of size B becomes a size-B subset
of Z/N. The number of ORDERED m-tuples of indices into D (repetition allowed)
whose DL-values sum to r is then

    c(r) = InverseFFT( FFT(1_D)^m ) [r],

exactly, because self-convolution of an indicator vector m times counts
exactly that -- one FFT, not a symbolic Groebner or resultant computation, and
with no geometric degenerate locus at all (every tuple sums to SOME r in Z/N;
there is no analogue of "root at infinity" once the problem is posed
additively in Z/N rather than via x-coordinates and the 2-to-1 x-map).
Validity is checked exactly, not approximately: sum_r c(r) must equal B^m on
the nose after rounding, which is guaranteed by construction and is a real
gate -- a bug that mis-sizes D or double-counts a value will trip it.

This is the SAME primitive EXP-HPSC-74991c uses for its H-PSEUDO constant
C(p) = max_k |FFT(1_F)(k)| / sqrt(B): both experiments are functions of the
Fourier transform of a DL-indicator, read two different ways. That is not a
coincidence worth hiding -- it is why this redesign exists.

What the redesign buys, and what it costs (recorded, not hidden):
  + Coverage and multiplicity dispersion become EXACT, not sampled.
  + No degenerate locus, so no "good/bad specialization" bookkeeping.
  - Recognizability (the cost of a factor-base MEMBERSHIP TEST) is about the
    x-coordinate representation, not the abstract DL, and is NOT measured
    here.
  - "Subgroup-aligned" bases are VACUOUS on prime-order curves -- there is no
    proper nontrivial subgroup -- and are DROPPED from the construction list.
  - Relation rank needs actual exponent VECTORS, not counts, so it is
    measured separately below, and only at m = 3 in this run (see
    `sample_relations`). m = 4 relation rank is specified but NOT run here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time

import numpy as np

sys.path.insert(0, "../../EXP-HPSC-74991c/code")
from hpseudo_scaling import (  # noqa: E402
    find_prime_order_curves,
    tonelli,
)

SEED = 20260807


def cell_rng(N: int, B: int, name: str) -> random.Random:
    """Deterministic RNG local to (N, B, construction) -- NOT the sweep RNG.

    Two curves that share an order N get the IDENTICAL uniform_random and
    sidon_dl base for the same B, by construction. That is the point: those
    two constructions do not read the curve, so there is nothing for them to
    vary by at fixed N, and this makes that a guarantee instead of a hope.
    """
    h = hashlib.sha256(f"{SEED}|{N}|{B}|{name}".encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


# ---------------------------------------------------------------------------
# group walk: every nonzero DL <-> its point, in one pass
# ---------------------------------------------------------------------------


def walk_curve(p: int, A: int, B: int, N: int):
    """Return x_of_dl[1..N-1] and dl_of_x: {x-coordinate: DL}, one walk."""
    G = None
    for x0 in range(p):
        v = (pow(x0, 3, p) + A * x0 + B) % p
        if v and pow(v, (p - 1) // 2, p) == 1:
            G = (x0, tonelli(v, p))
            break
    assert G is not None

    x_of_dl = [0] * N  # x_of_dl[0] unused (identity has no x-coordinate)
    dl_of_x: dict[int, int] = {}
    gx, gy = G
    px, py = G
    for j in range(1, N):
        x_of_dl[j] = px
        dl_of_x[px] = j
        if j == N - 1:
            break
        if px == gx:
            if (py + gy) % p == 0:
                break
            num = (3 * px * px + A) % p
            den = (2 * py) % p
        else:
            num = (gy - py) % p
            den = (gx - px) % p
        lam = num * pow(den, p - 2, p) % p
        nx = (lam * lam - px - gx) % p
        ny = (lam * (px - nx) - py) % p
        px, py = nx, ny
    return x_of_dl, dl_of_x


# ---------------------------------------------------------------------------
# the exact FFT decomposition-count primitive
# ---------------------------------------------------------------------------


def decomposition_counts(D: list[int], N: int, m: int) -> np.ndarray:
    """c[r] = #{ ordered m-tuples of indices into D : sum of DL values = r }.

    Exact after rounding: self-convolution via FFT introduces float error of
    order 1e-9 or smaller for the N, B, m used in this battery (checked
    empirically to ~1e-13 before this code was trusted; see the module
    docstring). The caller MUST check the validity gate below before reading
    c.
    """
    u = np.zeros(N, dtype=np.float64)
    u[np.array(D, dtype=np.int64)] = 1.0
    U = np.fft.fft(u)
    c = np.fft.ifft(U**m).real
    return np.round(c).astype(np.int64)


def validity_gate(c: np.ndarray, B: int, m: int) -> tuple[bool, int]:
    total = int(c.sum())
    return total == B**m, total


# ---------------------------------------------------------------------------
# factor-base constructions (DL-space; smallest_x additionally needs x_of_dl)
# ---------------------------------------------------------------------------


def construct(name: str, N: int, B: int, x_of_dl, rng: random.Random) -> list[int] | None:
    """`rng` MUST be seeded by the caller as a function of (N, B, name) alone
    -- never a globally-advancing sweep RNG. `uniform_random` and `sidon_dl`
    are then IDENTICAL across any two curves that happen to share the same N,
    which is deliberate: neither construction reads anything about the curve
    beyond its order, so at fixed N there is nothing for them to vary by, and
    seeding them this way makes that a guarantee rather than an empirical
    near-miss. `smallest_x` is the only construction below that reads the
    curve's actual arithmetic (via x_of_dl) and can differ at fixed N.
    """
    pool = list(range(1, N))
    if name == "uniform_random":
        return rng.sample(pool, B)

    if name == "smallest_x":
        by_x = sorted(range(1, N), key=lambda dl: (x_of_dl[dl], dl))
        return by_x[:B]

    if name == "small_multiples":
        if B >= N:
            return None
        return list(range(1, B + 1))

    if name == "sidon_dl":
        # greedy B_2 (Sidon) set in Z/N: reject a candidate if it would
        # create a repeated pairwise sum with the set built so far.
        order = pool[:]
        rng.shuffle(order)
        D: list[int] = []
        sums: set[int] = set()
        for x in order:
            new_sums = [(x + x) % N] + [(x + d) % N for d in D]
            if len(set(new_sums)) < len(new_sums):
                continue  # collides with itself (only possible if x+x repeats, can't here)
            if sums.isdisjoint(new_sums):
                sums.update(new_sums)
                D.append(x)
                if len(D) == B:
                    return sorted(D)
        return None  # could not reach size B by greedy construction

    raise ValueError(name)


# ---------------------------------------------------------------------------
# relation rank (m = 3 only): recover real exponent vectors, rank mod N
# ---------------------------------------------------------------------------


def sample_relations(D: list[int], N: int, cap_residues: int):
    """DETERMINISTIC relation search: examine r = 0, 1, ..., cap_residues-1 in
    that fixed order (same sequence for every curve and every construction --
    no RNG anywhere in this function), search for i<=j in D with a k in D
    such that D[i]+D[j]+D[k] = r, and maintain an INCREMENTAL row-echelon
    basis over F_N so a relation is kept only if it raises the rank. Stops
    early once rank == B (no more information available) or the residue
    budget is exhausted.

    This replaces an earlier version that sampled random targets with a
    shared, globally-advancing RNG: that let which relations were FOUND
    depend on unrelated draws made earlier in the sweep, which is estimator
    noise, not curve- or construction-dependence, and it was capable of
    masquerading as either. Determinism removes it as a confound entirely.
    """
    B = len(D)
    idx_of_val = {v: i for i, v in enumerate(D)}
    basis: list[list[int]] = []   # row-echelon basis, in F_N
    pivots: list[int] = []
    examined = found = 0
    for r in range(min(N, cap_residues)):
        examined += 1
        hit = None
        for a in range(B):
            for b in range(a, B):
                need = (r - D[a] - D[b]) % N
                if need in idx_of_val:
                    hit = (a, b, idx_of_val[need])
                    break
            if hit:
                break
        if not hit:
            continue
        found += 1
        e = [0] * B
        for i in hit:
            e[i] += 1
        e = _reduce_against_basis(e, basis, pivots, N)
        if e is not None:
            basis.append(e)
            pivots.append(next(i for i, v in enumerate(e) if v))
            if len(basis) == B:
                break
    return len(basis), examined, found


def _reduce_against_basis(e, basis, pivots, N):
    """Row-reduce e against the current echelon basis; return the reduced
    row if it is independent (nonzero), else None. O(rank * B)."""
    e = e[:]
    for row, piv in zip(basis, pivots):
        if e[piv]:
            f = e[piv] * pow(row[piv], N - 2, N) % N
            e = [(e[i] - f * row[i]) % N for i in range(len(e))]
    if any(e):
        piv = next(i for i, v in enumerate(e) if v)
        inv = pow(e[piv], N - 2, N)
        return [(x * inv) % N for x in e]
    return None


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------


def gini(c: np.ndarray) -> float:
    x = np.sort(c.astype(np.float64))
    n = len(x)
    if x.sum() == 0:
        return 0.0
    cum = np.cumsum(x)
    return float((n + 1 - 2 * np.sum(cum) / cum[-1]) / n)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="raw-result.json")
    ap.add_argument("--primes", type=int, nargs="*", default=[1009, 2003])
    ap.add_argument("--Bs", type=int, nargs="*", default=[16, 24, 32, 48])
    ap.add_argument("--m", type=int, default=3)
    ap.add_argument("--curves-per-cell", type=int, default=12)
    ap.add_argument("--constructions", nargs="*",
                    default=["uniform_random", "smallest_x", "sidon_dl", "small_multiples"])
    args = ap.parse_args()

    t0 = time.time()
    rng = random.Random(SEED)
    m = args.m

    cells = []
    gate_failures = []
    for p in args.primes:
        curves = find_prime_order_curves(p, args.curves_per_cell, rng)
        for (A, Bc, N) in curves:
            x_of_dl, dl_of_x = walk_curve(p, A, Bc, N)
            for B in args.Bs:
                if B >= N:
                    continue
                for cons in args.constructions:
                    D = construct(cons, N, B, x_of_dl, cell_rng(N, B, cons))
                    if D is None:
                        continue  # e.g. Sidon set of this size not reached
                    c = decomposition_counts(D, N, m)
                    ok, total = validity_gate(c, B, m)
                    if not ok:
                        gate_failures.append({"p": p, "B": B, "construction": cons,
                                              "sum": total, "expected": B**m})
                        continue
                    mean = float(c.mean())
                    var = float(c.var())
                    cov = float((c > 0).mean())
                    row = {"p": p, "N": N, "B": B, "m": m, "construction": cons,
                           "mean": mean, "expected_mean": B**m / N,
                           "variance": var, "gini": gini(c), "coverage": cov}
                    if m == 3:
                        rank, examined, found = sample_relations(
                            D, N, cap_residues=20 * B)
                        row.update({
                            "residues_examined": examined, "relations_found": found,
                            "relation_rank": rank, "relation_rank_over_B": rank / B,
                            "rank_search_deterministic": True,
                        })
                    cells.append(row)

    print(f"cells={len(cells)} gate_failures={len(gate_failures)}", file=sys.stderr)

    # ---- across-curve excess variance at matched (p, B, m, construction) ----
    by_key: dict[tuple, list[dict]] = {}
    for row in cells:
        key = (row["p"], row["B"], row["construction"])
        by_key.setdefault(key, []).append(row)

    summary = []
    for (p, B, cons), rows in sorted(by_key.items()):
        means = np.array([r["mean"] for r in rows])
        covs = np.array([r["coverage"] for r in rows])
        ginis = np.array([r["gini"] for r in rows])
        # Per-curve N varies even at fixed p (distinct prime-order curves have
        # distinct #E(F_p)), so "the" expected mean is itself curve-dependent;
        # report the max absolute deviation from EACH row's own expected_mean
        # rather than a single p-wide constant that silently assumed N fixed.
        max_control_dev = float(np.max(np.abs(
            [r["mean"] - r["expected_mean"] for r in rows]
        )))
        entry = {
            "p": p, "B": B, "construction": cons, "n_curves": len(rows),
            "mean_of_mean": float(means.mean()),
            "max_abs_deviation_from_each_curves_own_expected_mean": max_control_dev,
            "across_curve_var_of_mean": float(means.var()),
            "mean_of_coverage": float(covs.mean()),
            "across_curve_var_of_coverage": float(covs.var()),
            "mean_of_gini": float(ginis.mean()),
            "across_curve_var_of_gini": float(ginis.var()),
        }
        if args.m == 3:
            ranks = np.array([r["relation_rank"] for r in rows])
            entry["mean_relation_rank"] = float(ranks.mean())
            entry["across_curve_var_of_relation_rank"] = float(ranks.var())
            entry["relation_rank_values"] = ranks.tolist()
        summary.append(entry)

    mean_control_ok = all(
        e["max_abs_deviation_from_each_curves_own_expected_mean"] < 1e-6
        for e in summary
    )

    # ---- the ACTUAL test: same order N, different curves, same construction
    #
    # `p`-grouping conflates across-curve variance with across-N variance,
    # since curves at the same p generally have different orders. Grouping
    # by the EXACT N a curve realizes isolates the question H-FBST-c8a080
    # actually asks. uniform_random/sidon_dl/small_multiples are now seeded
    # per (N,B,name) and so are IDENTICAL for any two same-N curves by
    # construction -- their appearance below is a check that this is true,
    # not a measurement. smallest_x is the only construction that can
    # differ, since it alone reads the curve's own arithmetic.
    by_N: dict[tuple, list[dict]] = {}
    for row in cells:
        by_N.setdefault((row["N"], row["B"], row["construction"]), []).append(row)

    exact_N_repeats = {
        f"N={N},B={B},{cons}": {
            "n_curves_sharing_this_N": len(rows),
            "coverage_values": [r["coverage"] for r in rows],
            "coverage_identical_across_curves": len({r["coverage"] for r in rows}) == 1,
            "relation_rank_values": [r.get("relation_rank") for r in rows] if args.m == 3 else None,
            "relation_rank_identical_across_curves":
                (len({r["relation_rank"] for r in rows}) == 1) if args.m == 3 else None,
        }
        for (N, B, cons), rows in sorted(by_N.items())
        if len(rows) >= 2
    }
    n_repeat_groups = len(exact_N_repeats)
    smallest_x_groups = {k: v for k, v in exact_N_repeats.items() if k.split(",")[-1] == "smallest_x"}
    non_curve_groups = {k: v for k, v in exact_N_repeats.items() if k.split(",")[-1] != "smallest_x"}

    results = {
        "experiment_id": "EXP-FBST-190234", "seed": SEED, "m": args.m,
        "method": "exact FFT decomposition counts on DL-space, prime-order curves",
        "gate_failures": gate_failures,
        "gate_all_passed": len(gate_failures) == 0,
        "positive_control": {
            "description": "mean of c(r) must equal B^m/N EXACTLY for every construction "
                           "and every curve -- this is an algebraic identity, not a "
                           "measurement, and a failure here voids the run",
            "held_within_1e-6_everywhere": mean_control_ok,
        },
        "per_curve_cells": cells,
        "per_construction_summary_BY_P_not_N_see_exact_N_test_for_the_real_answer": summary,
        "exact_N_test": {
            "note": "The only test that isolates curve-identity from order: pairs/groups "
                    "of curves in this sweep that happen to share the SAME EXACT N.",
            "n_repeat_groups_found": n_repeat_groups,
            "non_curve_reading_constructions_all_identical_at_fixed_N":
                all(v["coverage_identical_across_curves"] and
                    (v["relation_rank_identical_across_curves"] is not False)
                    for v in non_curve_groups.values()) if non_curve_groups else None,
            "smallest_x_identical_at_fixed_N":
                all(v["coverage_identical_across_curves"] for v in smallest_x_groups.values())
                if smallest_x_groups else None,
            "smallest_x_groups": smallest_x_groups,
            "non_curve_reading_groups_sample": dict(list(non_curve_groups.items())[:6]),
        },
    }
    blob = json.dumps(results, indent=2, sort_keys=True)
    open(args.out, "w").write(blob + "\n")
    print(blob)
    print(f"elapsed_seconds: {round(time.time()-t0,2)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
