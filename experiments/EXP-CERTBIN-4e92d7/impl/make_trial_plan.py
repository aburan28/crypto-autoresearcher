#!/usr/bin/env python3
"""Write trial-plan-v1.json from the frozen specification alone (no drawn
value). The seeds are read from the specification file; the counts, phases,
draw procedures and interpretations are transcribed from its text.

  python3 experiments/EXP-CERTBIN-4e92d7/impl/make_trial_plan.py \
      --spec experiments/EXP-CERTBIN-4e92d7/specification.yaml \
      --run-id RUN-CERTBIN-3b7e05 --out experiments/EXP-CERTBIN-4e92d7/trial-plan-v1.json

--dev writes a DEVELOPMENT plan (different seeds, small counts) that the driver
accepts only with --dev and only for an output directory outside the repository.
"""
import argparse
import datetime
import hashlib
import json
import os
import sys

import yaml

SEED_KEYS = ["S_curve", "S_pts", "S_ref", "S_test", "S_plant", "S_randx_ref", "S_randx_test",
             "S_nullF2_ref", "S_nullF2_test", "S_nullAff_draw1", "S_nullAff_draw2", "S_nullAff_draw3",
             "S_selftest"]

INTERPRETATIONS = [
    "I-1 curve draw: A = integers(0, 2^17) then B = integers(0, 2^17) per draw from S_curve; B = 0 is redrawn and counted; the first (A, B) with #E = h*q, h in {2, 4}, q prime (Miller-Rabin, fixed bases) is accepted; every rejected draw is recorded.",
    "I-2 subgroup points: from S_pts, x = integers(0, 2^17); the lift is deterministic, y = x*H(c) with c = x + A + B/x^2 and H the half-trace (x != 0), y = sqrt(B) (x = 0); a non-liftable x is redrawn and counted; P = [h](x, y), redrawn if O; then k_Q = integers(1, q) (uniform in [1, q-1]) and Q = [k_Q]P.",
    "I-3 curve targets: per draw a = integers(0, q) then b = integers(0, q); R = [a]P + [b]Q, redrawn (counted) if R = O. A 'draw' is one (a, b) pair.",
    "I-4 the 1000 test targets of a family are 1000 accepted distinct x_R (duplicates and reference x_R rejected and counted). Targets with x_R in V are KEPT as the degenerate stratum (not redrawn) and excluded from every arm statistic and entropy, per the strata block.",
    "I-5 reference_rule: every candidate drawn from the reference stream counts as a draw (including rejected duplicates, degenerate x_R and R = O redraws for curve streams); scanning stops at 3 unsat + 2 sat or at 500 draws. References are ordered U1, U2, U3 (unsat, in scan order) then S1, S2.",
    "I-6 F-AFF references: the F-S3 reference sequence is the S_ref stream re-generated from its seed with the same rejection rules (R = O, duplicate x_R, degenerate x_R); it is scanned from the start and each candidate is classified by oracle B of THIS F-AFF draw; the first 3 unsat and 2 sat are taken (up to 500 draws). F-AFF test targets use the r bits of the 1000 F-S3 test targets in draw order (degenerate ones inherit the degenerate stratum).",
    "I-7 F-AFF draw d: from S_nullAff_draw{d}, E'^0 then E'^j for j = 0..16, each by one integers(0, 2, size=|supp|) call over the support positions of E^0 (resp. E^j) in row-major order of the 17 x 172 matrix (columns in 'mu order': degree ascending, then sorted index tuple lexicographic).",
    "I-8 F-NULLF2: one instance = one integers(0, 2, size=|U|) call over U = union_k U_k positions in row-major order; an instance identical to an earlier one (or to a reference) is rejected and counted. F-NULLF2 has no degenerate stratum and no oracle A.",
    "I-9 F-PLANT: F_V is enumerated exactly (x in V ascending; for x != 0 both points ordered by y; x = 0 gives (0, sqrt B)) and sorted by (x, y); each draw is two integers(0, |F_V|) calls from S_plant; rejections (P_1 = +-P_2, z in V, duplicate z, z an F-S3 target or reference) are counted. F-PLANT is scored against the 5 F-S3 references and the F-S3 modal reference (all 200 targets) and, per the modal rule applied per family, also against its own modal reference (targets 101..200).",
    "I-10 F-RANDX: x_R = integers(0, 2^17). References reject duplicates and degenerate x_R; test targets reject duplicates and reference x_R, and keep degenerate x_R as the degenerate stratum. Secondary cross-scoring is against the 5 F-S3 references and the F-S3 modal reference.",
    "I-11 maximizing reference (DR-3, DR-6, DR-7): the argmax of the unsat-arm T_strict retention at D = 4 over (U1, U2, U3, modal); ties go to the first in that order. Every per-reference value is also reported.",
    "I-12 M3 lower-bound case: the pooled Clopper-Pearson 95% upper bound is taken for 0 successes over the summed non-degenerate unsatisfiable arm sizes of F-AFF-1..3.",
    "I-13 M3 bootstrap (point case): 10^4 resamples, generator PCG64(S_selftest); for F-S3, F-AFF-1, F-AFF-2, F-AFF-3 in that order, one integers(0, n, size=(10^4, n)) call resamples the non-degenerate unsat arm; the modal reference's retention in a resample uses the resampled targets with idx > 100.",
    "I-14 M2 / hazards for the modal reference use targets 101..N only; r-dependence (sampled) is evaluated over the scored non-degenerate targets. For F-NULLF2, dependence and K are over replay survivors (as the spec states).",
    "I-15 C-UNIF: every F-RANDX reference including the modal (101..1000) at both D; the '99.9% binomial interval' is the equal-tailed acceptance region [lo, hi] of Binomial(n, 2^-K_rank) with at most 0.05% mass on each side outside it.",
    "I-16 tail check 'largest trace-class size vs uniform-over-distinct-traces null': Monte Carlo, 1000 replicates per (family, D, granularity), one generator PCG64(S_selftest) consumed in the fixed order families x D x granularity.",
    "I-17 trace encodings (canonical JSON, no whitespace, sha256): T_rank = the integer rank; T_set = [[sorted pivot columns],[sorted Z_D]]; T_strict = [[p,c],...]; T_ops = [[p,c,[sorted X]],...]. Target-vs-reference matches are decided by content (hash equality is cross-checked and any disagreement recorded).",
    "I-18 C-AFF is also applied to F-PLANT instances and all classified reference-scan candidates; the direct-replay check runs on the first 20 targets (draw order) of every affine-route family (F-S3, F-S3-REV, F-PLANT, F-RANDX, F-AFF-1..3) against every reference including cross-family and modal ones. For F-AFF the 'direct' instance is compared with a second, independent combination code path.",
    "I-19 C-DET (phase 7, separate process) re-eliminates the 5 F-S3 references, the F-S3 modal reference and all 1000 F-S3 test targets at D = 3 and 4, and compares T_ops hashes.",
    "I-20 PS0-PS3 are evaluated on every reference and every target of every family at both D (including degenerate targets). PS2 compares T_set by hash; for F-S3 it also includes F-PLANT; F-PLANT itself is covered through the F-S3 references.",
    "I-21 rational_flag is computed for curve-algebra families only (F-S3, F-S3-REV, F-PLANT, F-RANDX); the lift is the deterministic lift of I-2 and the four sign combinations are covered by testing x(P_1 + P_2) and x(P_1 - P_2) against x_R.",
    "I-22 pruned dense bytes = rows_pruned * cols_pruned / 8 (not rounded); DR-6 compares this number with 233,472 and 32.",
    "I-23 workers: 1 (no sharding; the serial-vs-sharded demonstration is therefore not needed and not run).",
    "I-24 DR-2: a clause that cannot be evaluated makes the verdict 'not evaluable' only if no evaluable clause decides it; the M3 consistency clause accepts 'not estimable' as the spec states. DR-3: an M3 lower bound < 10 or a not-estimable M3 leaves the M3 clauses unknown.",
    "I-25 phase 7 runs as the declared determinism command in a separate process after phases 1-6; phase 8 then runs via the declared resume form (driver command + --resume).",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--dev-seed-base", type=int, default=777000)
    ap.add_argument("--dev-targets", type=int, default=30)
    ap.add_argument("--dev-planted", type=int, default=12)
    args = ap.parse_args()
    if os.path.exists(args.out):
        print(f"refusing to overwrite {args.out}", file=sys.stderr)
        return 2
    spec_bytes = open(args.spec, "rb").read()
    spec = yaml.safe_load(spec_bytes)
    ex = spec["experiment"]
    seeds = {k: ex["seeds"][k] for k in SEED_KEYS}
    counts = {"test_targets": 1000, "planted_targets": 200, "reference_scan_max_draws": 500,
              "references_unsat": 3, "references_sat": 2, "D": [3, 4], "modal_window": [1, 100],
              "modal_scored": [101, 1000], "bootstrap_resamples": 10000, "c_aff_direct_replay_targets": 20,
              "maximum_workers": 1}
    if args.dev:
        seeds = {k: args.dev_seed_base + i for i, k in enumerate(SEED_KEYS)}
        counts["test_targets"] = args.dev_targets
        counts["planted_targets"] = args.dev_planted
    rd = f"experiments/{ex['id']}/runs/{args.run_id}"
    plan = {
        "schema": "certbin.trial_plan.v1",
        "experiment_id": ex["id"], "spec_version": ex["version"], "run_id": args.run_id,
        "development_plan": bool(args.dev),
        "spec_path": f"experiments/{ex['id']}/specification.yaml",
        "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "written_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "contains_drawn_values": False,
        "generator": ex["seeds"]["generator"],
        "seeds": seeds,
        "seed_rule": ex["seeds"]["seed_rule"],
        "counts": counts,
        "field": "F_2[t]/(t^17 + t^3 + 1)", "n": 17, "m": 2, "l": 9, "N_vars": 18,
        "fixture": {"D3": [323, 988], "D4": [2924, 4048]},
        "families": [
            {"id": "F-S3", "role": "primary", "reference_stream": "S_ref", "target_stream": "S_test", "targets": counts["test_targets"]},
            {"id": "F-S3-REV", "role": "replicate (row order reversed)", "instances": "F-S3 references and targets, identical bytes"},
            {"id": "F-PLANT", "role": "control (planted)", "target_stream": "S_plant", "targets": counts["planted_targets"], "references": "F-S3"},
            {"id": "F-RANDX", "role": "control (random x)", "reference_stream": "S_randx_ref", "target_stream": "S_randx_test", "targets": counts["test_targets"]},
            {"id": "F-AFF-1", "role": "null (same-support affine)", "draw_stream": "S_nullAff_draw1", "reference_stream": "S_ref (rescan)", "targets": "paired F-S3 r bits"},
            {"id": "F-AFF-2", "role": "null (same-support affine)", "draw_stream": "S_nullAff_draw2", "reference_stream": "S_ref (rescan)", "targets": "paired F-S3 r bits"},
            {"id": "F-AFF-3", "role": "null (same-support affine)", "draw_stream": "S_nullAff_draw3", "reference_stream": "S_ref (rescan)", "targets": "paired F-S3 r bits"},
            {"id": "F-NULLF2", "role": "null (same-support random F_2)", "reference_stream": "S_nullF2_ref", "target_stream": "S_nullF2_test", "targets": counts["test_targets"]},
        ],
        "phases": ex["execution"]["phases"],
        "commands": {
            "selftest": f"python3 experiments/{ex['id']}/impl/selftest.py --out {rd}/selftest.json",
            "driver": f"python3 experiments/{ex['id']}/impl/driver.py --spec experiments/{ex['id']}/specification.yaml --plan experiments/{ex['id']}/trial-plan-v1.json --run-id {args.run_id} --out {rd}",
            "determinism": f"python3 experiments/{ex['id']}/impl/driver.py --spec experiments/{ex['id']}/specification.yaml --plan experiments/{ex['id']}/trial-plan-v1.json --run-id {args.run_id} --out {rd} --phase determinism",
            "resume_and_phase8": f"python3 experiments/{ex['id']}/impl/driver.py --spec experiments/{ex['id']}/specification.yaml --plan experiments/{ex['id']}/trial-plan-v1.json --run-id {args.run_id} --out {rd} --resume",
        },
        "outputs": [f"{rd}/{f}" for f in [
            "selftest.json", "curve.json", "column-order-D3.json", "column-order-D4.json", "row-order-D3.json",
            "row-order-D4.json", "references.json", "F-S3-reference-oplogs-D3.jsonl.gz", "F-S3-reference-oplogs-D4.jsonl.gz",
            "targets-F-S3.jsonl.gz", "targets-F-S3-REV.jsonl.gz", "targets-F-PLANT.jsonl.gz", "targets-F-RANDX.jsonl.gz",
            "targets-F-AFF-1.jsonl.gz", "targets-F-AFF-2.jsonl.gz", "targets-F-AFF-3.jsonl.gz", "targets-F-NULLF2.jsonl.gz",
            "pivot-hazards.json", "cell-summary.json", "instrument-checks.json", "decision-rules.json", "sizing.json",
            "manifest.yaml", "raw-result.json", "command.txt", "environment.json", "stdout.log", "stderr.log",
            "run-report.md", "implementation.md", "checkpoint/"]],
        "interpretations": INTERPRETATIONS,
    }
    with open(args.out, "w") as f:
        json.dump(plan, f, indent=1)
        f.write("\n")
    print(hashlib.sha256(open(args.out, "rb").read()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
