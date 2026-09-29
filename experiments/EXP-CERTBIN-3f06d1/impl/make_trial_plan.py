#!/usr/bin/env python3
"""Write trial-plan-v1.json for EXP-CERTBIN-3f06d1 from the frozen
specification alone (no drawn value). Copied from EXP-CERTBIN-4e92d7 and
rewritten for the v2 contract (three cells, per-cell seed table).

Written AFTER C-PROV (cprov.py) and before any frozen stream is drawn
(specification execution.trial_plan_rule).

  python3 experiments/EXP-CERTBIN-3f06d1/impl/make_trial_plan.py \
      --spec experiments/EXP-CERTBIN-3f06d1/specification.yaml \
      --run-id RUN-CERTBIN-6d92b5 --out experiments/EXP-CERTBIN-3f06d1/trial-plan-v1.json

--dev writes a DEVELOPMENT plan (other seeds, small counts) that the driver
accepts only with --dev and only for an output directory outside the repository.
"""
import argparse
import datetime
import hashlib
import json
import os
import sys

import yaml

INTERPRETATIONS = [
    "I-1 R1/R2 curve draw: per draw A = integers(0, 2^17) then B = integers(0, 2^17) from S_curve; B = 0 is rejected; #E is counted exactly (1 + 1 + 2 #{x != 0 : Tr(x + A + B/x^2) = 0}); R1 accepts the first draw with #E = 2q, q prime (Miller-Rabin, fixed bases); R2 accepts the first with #E = 4q, q prime and (A, B) != (97044, 126251). Every rejected draw is recorded with its reason.",
    "I-2 R1/R2 subgroup points (Stage-1 I-2 with the cell's h): from S_pts, x = integers(0, 2^17); deterministic lift y = x H(c), c = x + A + B/x^2 (x != 0), y = sqrt(B) (x = 0); non-liftable x redrawn and counted; P = [h](x, y), redrawn if O; k_Q = integers(1, q); Q = [k_Q] P.",
    "I-3 R3 curve: A, B, #E, h, q, P, Q, k_Q are read from experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json after its sha256 is checked against the TASK-20260923-c2e57b snapshot receipt; #E is recounted and must equal the archived order. R3 has no S_curve / S_pts stream.",
    "I-4 R3 V (S_V): one integers(0, 2, size=(9, 17)) call per matrix, entry (i, j) = coefficient of t^(16-j) in row i (columns in the order t^16, ..., t^0, as the specification's RREF column order); matrices of rank < 9 are rejected and recorded; V = the row space; b_0..b_8 = the reduced row echelon form with columns t^16..t^0, rows ordered by leading degree descending (b_0 has the highest leading degree). R1/R2: b_j = t^j.",
    "I-5 Assignments: u = u_1 | (u_2 << 9) with u_i the coordinates of x_i in the cell's basis (bit j of u_1 = v_j, bit j of u_2 = v_{9+j}). Oracle A enumerates x_1 = sum_j u_1[j] b_j over all 512 u_1 and keeps a root x_2 iff V.coord(x_2) exists (the linear-algebra membership test). Oracle B and the Macaulay matrices are unchanged.",
    "I-6 Degenerate stratum: x_R in V by the linear-algebra test (reduction against an echelon form of the basis); for R1/R2 this equals x_R < 2^9.",
    "I-7 Curve targets (Stage-1 I-3): per draw a = integers(0, q) then b = integers(0, q); R = [a]P + [b]Q, redrawn (counted) if R = O. The 1000 test targets are 1000 accepted distinct x_R (duplicates and reference x_R rejected and counted); degenerate x_R are kept as the degenerate stratum (Stage-1 I-4).",
    "I-8 reference_rule (Stage-1 I-5): every candidate drawn counts as a draw; stop at 3 unsat + 2 sat or at 500 draws; references ordered U1, U2, U3, S1, S2.",
    "I-9 F-AFF-1 (Stage-1 I-6, I-7, one draw): E'^0 then E'^j (j = 0..16) from S_nullAff_draw1, one integers(0, 2, size=|supp|) call each over the support positions in row-major order; references by re-scanning S_ref from its seed with the Stage-1 rejection rules, classified by this draw's oracle B; test targets use the r bits of the 1000 F-S3 test targets in idx order (degenerate ones inherit the stratum).",
    "I-10 F-NULLF2 (Stage-1 I-8): one integers(0, 2, size=|U|) call per instance over U = union_k U_k positions in row-major order; duplicates rejected and counted.",
    "I-11 F-PLANT (Stage-1 I-9): F_V enumerated as the lifts of x = comb(u), u = 0..511, both points for x != 0, (0, sqrt B) for x = 0, sorted by (x, y); two integers(0, |F_V|) calls per draw from S_plant; rejections (P_1 = +-P_2, z in V, duplicate z, z an F-S3 target or reference) counted; the planted witness is coord(x(P_1)) | coord(x(P_2)) << 9. Scored against the 5 F-S3 references and the F-S3 modal reference (all 200 targets) and its own modal reference (targets 101..200).",
    "I-12 F-RANDX (Stage-1 I-10): x_R = integers(0, 2^17); references reject duplicates and degenerate x_R; targets reject duplicates and reference x_R and keep degenerate x_R as the degenerate stratum. F-RANDX targets are not required to avoid F-S3 x_R (as Stage 1); shared x_R are listed in the phase-1 record.",
    "I-13 F-S3-REV: the 5 F-S3 references and the 200 lowest-idx F-S3 test targets, identical E, rows reversed (i -> R_D - 1 - i). Its modal reference follows the modal rule within F-S3-REV (window 1..100, scored 101..200).",
    "I-14 Phase-0 order: C-PROV runs first as impl/cprov.py (a separate invocation, no random draw), then this plan is written (trial_plan_rule: after C-PROV), then the frozen command (selftest.py && driver.py). The driver refuses to start phase 1 unless cprov.json and selftest.json both pass.",
    "I-15 Per-cell C-SELF items (curve order check, S_3 vs point addition, descent vs direct evaluation, Macaulay rows vs naive multiply, oracle A vs oracle B on 3 random x_R, V rank and V-membership vs brute force on 10^4 random elements plus all 512 members, the [#E/2] x(2E) test vs a brute-force halving search on 200 random points, and the full x(2E) enumeration vs the doubling image) run in phase 1 immediately after the cell's curve / points / V are fixed (S_curve, S_pts or S_V) and C-TR is enumerated, and BEFORE any reference or target stream of the cell is drawn. Generator PCG64(SeedSequence([S_selftest, c])). A failure stops the run. The generic items (modulus, field axioms, small-curve point counts, half-trace, random-V descent, C-FIX) are in selftest.py before any frozen stream.",
    "I-16 x(2E) class of every x: by the [#E/2] test (definition path) for all 2^17 x of the cell (this enumeration is also C-TR); each target carries its class (x2E, xE_not_2E, twist).",
    "I-17 Hull per family: the non-degenerate test targets' r-vectors in idx order, h_0 = the lowest-idx one, W = span{r - h_0} as an echelon basis (leading bit descending). F-AFF-1 uses its paired F-S3 x_R (same hull as F-S3); F-S3-REV its 200 targets; F-PLANT its 200; F-RANDX its 1000; F-NULLF2 has no hull. The modal reference's scored set (idx > 100) lies in the same hull.",
    "I-18 Restriction: a_k|_W = the vector (<a_k, w_i>)_i over that W basis, packed as an int; it represents a_k + W^perp. K_rank_hull = rank of {a_k|_W}. A pivot is hull-rank-increasing iff a_k|_W is not in the span of a_j|_W, j < k (same reference).",
    "I-19 TS1R / M2R per cell, family and D: references = the family's own U1..S2 and its own modal (F-PLANT: F-S3:U1..S2, F-S3:modal and its own modal; F-RANDX: its own references and modal; the F-S3 references cross-scored on F-RANDX are secondary and excluded). E = hull-rank-increasing pivots with |S_k| >= 100, deduplicated by (a_k|_W, the set of target idx in S_k); per measurement the exact 99.9% band [lo, hi] of Bin(|S_k|, 1/2) (lo largest with P[X < lo] <= 0.0005, hi smallest with P[X > hi] <= 0.0005, exact integers); o = #measurements with zeros outside [lo, hi]; P[Bin(m, 0.001) >= o] exact. n_rep = #(reference, pivot) pairs that are hull-dependent with |S_k| >= 100 (not deduplicated), with the check that all have h = 0. RR-4's cell verdict uses F-S3 at D = 4; other families and D = 3 are secondary.",
    "I-20 C-HZERO: every (reference, pivot) that is hull-dependent with S_k >= 1, in every affine-route family (F-S3, F-S3-REV, F-PLANT, F-RANDX, F-AFF-1), both D; fails iff zeros_k > 0. Whether r_ref lies in H is recorded per reference.",
    "I-21 C-SURV: per affine-route family, reference and D, the count of scored targets surviving the whole fixed replay (forms path) must equal the count of scored targets in the exactly computed coset Sigma (particular solution + kernel of the system e_k = 1, membership by reduction) and in Sigma_H (the same system in the coordinates of H = h_0 + W).",
    "I-22 C-FORMS: every affine-route family (a superset of F-S3, F-PLANT, F-RANDX) and every reference at both D: the vectorised forms path and an independent scalar forms path give the same first replay-zero index on every scored target, and direct replay gives the same index as the forms on the 20 lowest-idx targets; plus each reference's direct self-replay equals its forms at r_ref (the 'every reference' part of C-AFF).",
    "I-23 C-DET (phase 7, separate process): per cell the 5 F-S3 references, the F-S3 modal reference and the 200 lowest-idx F-S3 targets at D = 3 and 4; T_ops hashes compared.",
    "I-24 C-REV: per cell and D, for the 5 references and the 200 targets, rank_D, the pivot-column set (sha256 of the sorted list) and 1 in R_D must be identical between F-S3 and F-S3-REV. T_strict retention under reversal is reported as data.",
    "I-25 C-NULLS: (i) the code-path sha256 (engine, elim, macaulay, oracles, families, gf2n, curve, vspace) is recorded per unit and must be identical for every family, cell and D; (ii) F-AFF-1: for each of the 18 matrices E'^0, E'^0'..E'^16', supp(E'^j) subset of supp(E^j) and the number of ones on supp(E^j) inside the exact 99.9% band of Bin(|supp(E^j)|, 1/2) (per matrix; the pooled count is also reported); (iii) F-NULLF2: every classified instance (reference-scan candidates and targets) has support inside U_k for every k, and the pooled number of ones over all their U positions is inside the exact 99.9% band of Bin(total positions, 1/2).",
    "I-26 PS0': per cell, the 30 lowest-idx non-degenerate unsat F-S3 targets with 1 in R_4; the certificate rows are the original rows whose XOR is the row that pivots in the constant column (found by replaying the op log on a row-combination tracker); verified by verifier/verify_cert.py in a separate process that imports nothing from impl/. Fewer than 30 eligible is recorded as a shortfall. PS0 and PS1 run on every reference and target of every family at both D; PS2 and PS3 are reported as implied checks.",
    "I-27 M1 (Stage-1 M1): retention(T_strict, ref, unsat) over the non-degenerate unsat arm for U1, U2, U3 and the modal (modal: targets 101..1000); F-PLANT uses F-S3:U1..U3 and its own modal; retention_family = the maximum; CP95 exact. The maximizing reference is the argmax over (U1, U2, U3, modal), ties to the first (Stage-1 I-11).",
    "I-28 M1f: f_div per target and reference (Stage-1 definition); per arm the median and the fraction with f_div <= 0.01. RR-3's 'every unsat reference' is U1, U2, U3 of F-S3 at D = 4; the modal is reported beside it.",
    "I-29 M-R4: per family the fraction of the non-degenerate unsat arm with 1 in R_4 (and with 1 in R_3), CP95 exact; also the sat arm; D* per arm. F-RANDX split by the x(2E) class of x_R. RR-6: F-RANDX unsat arm at D = 4, x(2E) versus the pooled x(E) minus x(2E) and twist, exact one-sided Fisher test (alternative: x(2E) rate higher); 'not evaluable' if either group is empty.",
    "I-30 RR-5: the F-S3 unsat-arm 1-in-R_4 CP95 interval overlaps [0.799, 0.875] iff lo <= 0.875 and hi >= 0.799; HIGHER iff lo > 0.875; LOWER iff hi < 0.799. NULLS CLEAN iff the CP95 upper bound of the unsat-arm 1-in-R_4 rate is <= 0.05 for both F-AFF-1 and F-NULLF2 (D = 4).",
    "I-31 M3 (per cell, D = 4, T_strict): numerator retention_family(F-S3), denominator retention_family(F-AFF-1); first matching rule (1)-(4). Rule (3) lower bound = numerator / CP95 upper bound for 0 of n_den. Rule (4) bootstrap: 10^4 resamples with a fresh PCG64(S_selftest) per cell; F-S3 then F-AFF-1, one integers(0, n, size=(10^4, n)) call each; modal retention in a resample uses the resampled targets with idx > 100.",
    "I-32 RR-7: K = K_sampled of the maximizing reference (Stage-1 DR-3). 'M3 < 10': rule (4) point < 10, rule (2) ratio 0 -> true; rule (3) lower bound >= 10 -> false, < 10 -> unknown; rule (1) -> the clause 'rule (1)/(2) applies' is true.",
    "I-33 Fixed-schedule survival on F-RANDX (tail check): per own reference (incl. modal) and D, survivors / n_scored against the exact 99.9% band of Bin(n_scored, 2^-K_rank); evaluated only where K_rank < 17, otherwise recorded as determined by the identity.",
    "I-34 Trace encodings (Stage-1 I-17): canonical JSON, sha256; target-vs-reference matches decided by content with hash cross-check.",
    "I-35 Output bound: pivot-hazards-<cell>.json keeps a_k, a0_k and the hull flag for every pivot, and S_k, zeros, h_k and the exact band only up to the first pivot with S_k = 0 (all later pivots have S_k = 0); references.json per cell keeps full T_strict per D (Stage 1). Full op logs for the F-S3 references only.",
    "I-36 Cells run in the order R1, R2, R3; within a cell phases 1-6 in order; then phase 7 (separate process), phase 8 (certificates, cells.json), the verifier (separate process) and phase 9 (--resume).",
    "I-37 workers: 1. Memory cap RLIMIT_AS 4 GiB in-process; watchdog 86,400 s (timeout) per invocation; maximum_runs 2 (the second only after an infrastructure failure).",
    "I-38 RR-2: every F-S3 reference (U1, U2, U3, S1, S2 and the modal) at D = 4; D = 3 reported. RR-1: U1, U2, U3 and the modal (F-S3, D = 4, T_strict).",
    "I-39 Sigma_H: dimension dim W - K_rank_hull when the system is consistent (else empty); its elements are listed when it has <= 2^10 points; |Sigma_H intersected with T| counted over the reference's scored targets.",
    "I-40 rational_flag (Stage-1 I-21) with x_i = comb(u_i).",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--dev-seed-base", type=int, default=880000)
    ap.add_argument("--dev-targets", type=int, default=40)
    ap.add_argument("--dev-planted", type=int, default=12)
    ap.add_argument("--dev-rev", type=int, default=20)
    args = ap.parse_args()
    if os.path.exists(args.out):
        print(f"refusing to overwrite {args.out}", file=sys.stderr)
        return 2
    spec_bytes = open(args.spec, "rb").read()
    spec = yaml.safe_load(spec_bytes)
    ex = spec["experiment"]
    table = ex["seeds"]["table"]
    counts = {"test_targets": 1000, "planted_targets": 200, "rev_targets": 200, "reference_scan_max_draws": 500,
              "references_unsat": 3, "references_sat": 2, "D": [3, 4], "modal_window": [1, 100],
              "modal_scored": [101, 1000], "bootstrap_resamples": 10000, "c_aff_direct_replay_targets": 20,
              "c_det_targets": 200, "ps0prime_certificates_per_cell": 30, "ts1r_min_survivors": 100,
              "maximum_workers": 1}
    cells = {
        "R1": {"c": 1, "curve_mode": "draw", "h": 2, "exclude_stage1_curve": False, "V_mode": "poly",
               "seeds": dict(table["R1"])},
        "R2": {"c": 2, "curve_mode": "draw", "h": 4, "exclude_stage1_curve": True, "V_mode": "poly",
               "seeds": dict(table["R2"])},
        "R3": {"c": 3, "curve_mode": "stage1", "h": 4, "V_mode": "random", "seeds": dict(table["R3"])},
    }
    S_selftest = ex["seeds"]["S_selftest"]
    if args.dev:
        for ci, (cell, c) in enumerate(cells.items()):
            c["seeds"] = {k: args.dev_seed_base + 100 * ci + i for i, k in enumerate(c["seeds"])}
        counts["test_targets"] = args.dev_targets
        counts["planted_targets"] = args.dev_planted
        counts["rev_targets"] = args.dev_rev
        counts["modal_scored"] = [101, args.dev_targets]
        counts["c_det_targets"] = args.dev_rev
    rd = f"experiments/{ex['id']}/runs/{args.run_id}"
    plan = {
        "experiment_id": ex["id"], "specification_version": ex["version"], "run_id": args.run_id,
        "dev": bool(args.dev),
        "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "written_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "written_from": "the frozen specification alone; contains no drawn value",
        "generator": ex["seeds"]["generator"],
        "S_selftest": S_selftest,
        "cells": cells,
        "counts": counts,
        "parameters": {"n": 17, "m": 2, "l": 9, "modulus": "t^17 + t^3 + 1", "D": [3, 4],
                       "fixture": {"D3": [323, 988], "D4": [2924, 4048]}},
        "families_per_cell": [f["id"] for f in ex["families_per_cell"]],
        "phases": ex["execution"]["phases"],
        "commands": {"command": ex["execution"]["command"], "determinism_command": ex["execution"]["determinism_command"],
                     "verify_command": ex["execution"]["verify_command"],
                     "pre_command_cprov": f"python3 experiments/{ex['id']}/impl/cprov.py --stage1-run experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05 --out {rd}/cprov.json"},
        "outputs": [
            f"{rd}/cprov.json", f"{rd}/selftest.json", f"{rd}/cells.json",
            f"{rd}/column-order-D3.json", f"{rd}/column-order-D4.json", f"{rd}/row-order-D3.json", f"{rd}/row-order-D4.json",
            f"{rd}/references-<cell>.json", f"{rd}/F-S3-reference-oplogs-<cell>-D3.jsonl.gz", f"{rd}/F-S3-reference-oplogs-<cell>-D4.jsonl.gz",
            f"{rd}/targets-<cell>-<family>.jsonl.gz", f"{rd}/pivot-hazards-<cell>.json",
            f"{rd}/ps0prime-certificates.jsonl.gz", f"{rd}/ps0prime-verification.json",
            f"{rd}/cell-summary.json", f"{rd}/instrument-checks.json", f"{rd}/decision-rules.json", f"{rd}/sizing.json",
            f"{rd}/manifest.yaml", f"{rd}/raw-result.json", f"{rd}/command.txt", f"{rd}/environment.json",
            f"{rd}/stdout.log", f"{rd}/stderr.log", f"{rd}/run-report.md", f"{rd}/implementation.md"],
        "interpretations": INTERPRETATIONS,
    }
    with open(args.out, "w") as f:
        json.dump(plan, f, indent=1)
    print(f"wrote {args.out} (sha256 {hashlib.sha256(open(args.out, 'rb').read()).hexdigest()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
