"""EXP-FBST-190234 deepening run -- DELIBERATE same-N curve search.

RUN-FBST-190234-001 found its same-N groups INCIDENTALLY: 300 independently
sampled curves collided by chance into 848 same-N groups, mostly depth 2-3,
one reaching depth 8 (N=3947, where 1 of 8 curves showed a rank-deficient
smallest_x base at B=16). That is thin evidence for the RATE of the rank
deficiency specifically -- the rarer and operationally sharper of the two
findings in EV-FBST-8949fc -- precisely because it is rare (5/240 groups) and
every group it occurred in had depth <= 8.

This run HUNTS for many curves of a small number of target orders, instead of
accepting whatever a birthday-paradox collision produces.

Two phases:
  1. SCOUT: sample a batch of random curves at a fixed p; tally order
     frequency; the most-frequent PRIME orders become hunting targets. This
     is more efficient than picking a target blind -- it guarantees the
     target actually occurs at a workable rate in this p's Hasse interval,
     and it deliberately revisits N=3947 (already implicated) alongside
     fresh targets, so this run can both deepen a known lead and check
     whether the effect generalises to orders that showed nothing unusual
     the first time.
  2. HUNT: for each target N, keep drawing random (A,B) at the SAME p until
     `depth` curves of EXACTLY that order are found or a trial budget is
     exhausted. Every found curve's order is independently re-verified by
     [N]P = O before it is trusted -- the same discipline EXP-HPSC-74991c
     needed after a silent point-counting defect in its first draft.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import Counter

sys.path.insert(0, "../../EXP-HPSC-74991c/code")
sys.path.insert(0, "../../EXP-FBST-190234/code")
from hpseudo_scaling import curve_order, is_prime, qr_table, _order_is_correct  # noqa: E402
from factorbase_stats import (  # noqa: E402
    cell_rng,
    construct,
    decomposition_counts,
    gini,
    sample_relations,
    validity_gate,
    walk_curve,
)

SEED = 20260808  # distinct from the main sweep's seed; this is a follow-up, not a rerun


def scout_targets(p: int, n_samples: int, top_k: int, rng: random.Random, sq):
    tally = Counter()
    for _ in range(n_samples):
        A, B = rng.randrange(p), rng.randrange(p)
        if (4 * A**3 + 27 * B**2) % p == 0:
            continue
        N = curve_order(p, A, B, sq)
        if is_prime(N):
            tally[N] += 1
    return [n for n, _ in tally.most_common(top_k)], tally


def hunt(p: int, target_N: int, depth: int, max_trials: int, rng: random.Random, sq):
    found = []
    trials = 0
    while len(found) < depth and trials < max_trials:
        trials += 1
        A, B = rng.randrange(p), rng.randrange(p)
        if (4 * A**3 + 27 * B**2) % p == 0:
            continue
        N = curve_order(p, A, B, sq)
        if N == target_N and _order_is_correct(p, A, B, N):
            found.append((A, B))
    return found, trials


def analyze_curve(p: int, A: int, B: int, N: int, sizes: list[int]):
    x_of_dl, _ = walk_curve(p, A, B, N)
    out = {}
    for size in sizes:
        row = {}
        for cons in ("uniform_random", "smallest_x", "sidon_dl", "small_multiples"):
            D = construct(cons, N, size, x_of_dl, cell_rng(N, size, cons))
            if D is None:
                continue
            c = decomposition_counts(D, N, 3)
            ok, total = validity_gate(c, size, 3)
            if not ok:
                row[cons] = {"gate_failure": True}
                continue
            rank, examined, foundn = sample_relations(D, N, cap_residues=20 * size)
            row[cons] = {
                "coverage": float((c > 0).mean()),
                "gini": gini(c),
                "relation_rank": rank,
                "relation_rank_over_B": rank / size,
            }
        out[str(size)] = row
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="raw-result.json")
    ap.add_argument("--p", type=int, default=4001)
    ap.add_argument("--scout-samples", type=int, default=3000)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--extra-targets", type=int, nargs="*", default=[3947],
                    help="Targets to revisit regardless of scouting, e.g. the depth-8 "
                         "group from RUN-FBST-190234-001 where a rank deficiency was seen")
    ap.add_argument("--depth", type=int, default=40)
    ap.add_argument("--max-trials-per-target", type=int, default=40000)
    ap.add_argument("--Bs", type=int, nargs="*", default=[16, 24])
    args = ap.parse_args()

    t0 = time.time()
    rng = random.Random(SEED)
    sq = qr_table(args.p)

    scouted, tally = scout_targets(args.p, args.scout_samples, args.top_k, rng, sq)
    targets = sorted(set(scouted) | set(args.extra_targets))
    print(f"scouted top-{args.top_k}: {scouted}; targets (incl. extras): {targets}",
          file=sys.stderr)

    groups = {}
    for N in targets:
        found, trials = hunt(args.p, N, args.depth, args.max_trials_per_target, rng, sq)
        print(f"N={N}: found {len(found)}/{args.depth} in {trials} trials "
              f"(scouted count was {tally.get(N, 'n/a')})", file=sys.stderr, flush=True)
        curves_data = []
        for (A, B) in found:
            curves_data.append({"A": A, "B": B,
                                 "stats": analyze_curve(args.p, A, B, N, args.Bs)})
        groups[str(N)] = {
            "target_N": N, "depth_achieved": len(found), "depth_requested": args.depth,
            "trials": trials, "scouted_count": tally.get(N),
            "curves": curves_data,
        }

    # ---- summarize: for smallest_x, the deficiency rate and coverage spread
    #      per (N, B); for the other three, confirm invariance at real depth
    summary = {}
    for N_str, g in groups.items():
        for B in args.Bs:
            row = {"N": g["target_N"], "B": B, "depth": g["depth_achieved"]}
            for cons in ("uniform_random", "smallest_x", "sidon_dl", "small_multiples"):
                vals = [c["stats"][str(B)].get(cons) for c in g["curves"]
                        if str(B) in c["stats"] and cons in c["stats"][str(B)]
                        and "gate_failure" not in c["stats"][str(B)][cons]]
                if not vals:
                    continue
                covs = [v["coverage"] for v in vals]
                ranks = [v["relation_rank"] for v in vals]
                row[cons] = {
                    "n": len(vals),
                    "coverage_identical": len(set(covs)) == 1,
                    "coverage_min": min(covs), "coverage_max": max(covs),
                    "coverage_spread": max(covs) - min(covs),
                    "rank_identical": len(set(ranks)) == 1,
                    "rank_values_histogram": dict(Counter(ranks)),
                    "rank_deficient_count": sum(1 for r in ranks if r < B),
                    "rank_deficiency_rate": sum(1 for r in ranks if r < B) / len(ranks),
                }
            summary[f"N={g['target_N']},B={B}"] = row

    results = {
        "experiment_id": "EXP-FBST-190234", "run_purpose": "deepen_same_N",
        "seed": SEED, "p": args.p,
        "scouting": {"samples": args.scout_samples, "top_k_prime_orders": scouted,
                    "extra_targets_revisited": args.extra_targets},
        "targets": targets, "depth_requested": args.depth,
        "groups": groups, "summary": summary,
    }
    blob = json.dumps(results, indent=2, sort_keys=True)
    open(args.out, "w").write(blob + "\n")
    print(blob)
    print(f"elapsed_seconds: {round(time.time()-t0,2)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
