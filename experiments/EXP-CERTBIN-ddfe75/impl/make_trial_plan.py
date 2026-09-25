#!/usr/bin/env python3
"""Write experiments/EXP-CERTBIN-ddfe75/trial-plan-v1.json from the
specification alone, BEFORE phase 0 (execution.trial_plan_rule). It holds
input paths and hashes, arms, seeds, slot order, keep rules, phases, output
paths, the exact power table and the executor's pre-data readings of points
the specification leaves open. No closure value and no draw."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
import stats  # noqa: E402
from common import now, sha256_file  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(common.EXP / "trial-plan-v1.json"))
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"{out} exists; the trial plan is write-once")
    plan = {
        "experiment_id": "EXP-CERTBIN-ddfe75", "version": 1, "task_id": "TASK-20260924-7c1fb2",
        "written_at": now(),
        "specification": {"path": "experiments/EXP-CERTBIN-ddfe75/specification.yaml",
                          "sha256": sha256_file(common.EXP / "specification.yaml")},
        "inputs": {p: {"bound_sha256": h} for p, h in common.INPUT_FILES.items()},
        "engine": {"package": "src/crypto_autoresearcher/gf2", "pinned_commit": common.ENGINE_COMMIT,
                   "kernels_c_sha256": common.KERNELS_C_PIN, "backend": "native",
                   "threads": "CRYPTO_AR_GF2_THREADS=2 (<= 3; lowered because another CERTBIN executor shares the 4-core machine)"},
        "resources": {"memory_cap": "3 GiB (RLIMIT_AS)", "watchdog_seconds": 86400, "maximum_runs": 2,
                      "maximum_workers": 1},
        "seeds": {"S_selftest": common.SEED_SELFTEST, **common.ARM_SEEDS},
        "generator": "numpy.random.Generator(numpy.random.PCG64(seed)), numpy 2.4.6, one per fresh arm",
        "slots": {"xr144": "U62 (listed order, ascending idx), then S62, then C20 of instance-sets.json; slot 0..143",
                  "N-CONV17, N-ELL144": "144 stream slots, x_R null"},
        "arms": {
            "archived": ["S3-U62", "S3-C20", "S3-S62", "NULL-AFF62", "NULL-F262", "NELL-A20"],
            "fresh": {
                "N-CONV": "kept Qpart(x_R); bits = g.integers(0, 2, size=|S_L|) on S_L; identity E_S3(x_R) rejected",
                "N-CONVL": "kept Qpart + Lpart; bits = g.integers(0, 2, size=|S_L cap col 0|) on the constant positions; "
                           "identity (B's own bits) and b' = 0 rejected; b' logged",
                "N-CONV17": "kept Q_k = sum_{i+j=k} v_i v_{9+j}; bits on S_L as N-CONV",
                "N-ELL144": "o2-declaration draw: M[Upos] = g.integers(0, 2, size=Upos.size); c = int(g.integers(0, 2)); "
                            "rows 0..15 kept; row 16 := v_0 + v_9 + c"}},
        "keep_rule": ("per slot, attempts a = 0..255: one draw; rejections (identity, b' = 0, duplicate of an already-kept "
                      "system of the same arm by E_sha256); then s by exhaustive 2^18 evaluation; first s = 0 -> "
                      "unsatisfiable instance; first s >= 1 -> satisfiable control; others discarded; stop when both "
                      "filled; unfilled after attempt 255 -> EXHAUSTED(cap), never redrawn"),
        "phases": ["0 C-ENGINE, C-SRC, C-SELF, C-FIX; trial plan hashed",
                   "1 archived arms, C-CONSTRUCT, C-SUPPORT, C-REG (a)-(d), C-ELL on S3-*",
                   "2 fresh draws, keep rules, draw logs",
                   "3 rc_b (R'_3, R'_4); predictions-t5.jsonl.gz written and hashed",
                   "4 M_4, W_4, W'_4; flat-v1 and wdag-v1 certificates; C-TOP, C-T4, C-WDAG; negative controls",
                   "5 C-DET (separate process)", "6 verifier (separate process)",
                   "7 aggregation, decision rules, run report (--resume)"],
        "outputs": "experiments/EXP-CERTBIN-ddfe75/runs/<RUN_ID>/ (specification required_artifacts)",
        "power_table": stats.power_table(144),
        "pre_data_readings": {
            "R1_keys": ("fresh systems are keyed '<ARM>:<slot>:<role>' (role unsat|sat) because each slot keeps two "
                        "systems; archived arms keep the RC-1 keys; NELL-A20 systems are 'NELL-A20:<label>'"),
            "R2_rejected_draws": "a rejected attempt is logged with s = null (s is computed only for non-rejected draws)",
            "R3_certificate_lines": ("one line per (system, closure, format): M_4 flat-v1 (engine); W_4 flat-v1 (engine, "
                                     "counts toward W_4 only if max |mu| <= 2, never used for w); W_4 wdag-v1 (extractor, "
                                     "the only format counted for w)"),
            "R4_uncertified": "an engine W_4 refutation with no wdag-v1 submitted (extractor failure)",
            "R5_NC-DR-5_population": ("the NC-DR-5 label is issued on the arm's unsatisfiable systems; satisfiable controls "
                                      "and the union are reported beside it; per system the reference profile is the "
                                      "substituted [0,0,16,288,2328] if rc_b substitutes, the unsubstituted M_4 "
                                      "[0,0,17,323,2771] if the kernel dimension is 0, and no reference otherwise (counted "
                                      "as not matching)"),
            "R6_C-VERIFIER_kinds": ("a kind is (closure, arm) with >= 1 engine refutation under that closure; kinds with no "
                                    "refutation under a closure are empty, not vacuous; type (c) for M_4 uses the arm's "
                                    "W_4 flat certificates with max |mu| = 3 relabelled as M_4 (vacuous if the arm has none); "
                                    "type (c) for W_4 uses such a flat certificate as a one-node wdag, else a wdag with an "
                                    "added degree-4 child"),
            "R7_archived_closures": ("M_3, M_4 and W_4 of archived arms are computed in phase 1 (needed for C-REG) and reused "
                                     "as their phase-4 records; their wdag-v1 extraction and W'_4 run in phase 4"),
            "R8_NC-DR-4_rule3": "rule (3) 'MIXED in every other case' is applied literally, also when NC-DR-1 is UNDETERMINED",
            "R9_CP95": "exact Clopper-Pearson by bisection on exact binomial tails at 60 digits (mpmath)",
            "R10_C-DET_c": "the 20 systems of C-DET (b) are recomputed a second time with threads = 1"},
        "contains_no_closure_value_and_no_draw": True,
    }
    out.write_text(json.dumps(plan, indent=1) + "\n")
    print(f"wrote {out} sha256 {sha256_file(out)}")


if __name__ == "__main__":
    main()
