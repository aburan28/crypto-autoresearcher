#!/usr/bin/env python3
"""Stage-1 runner for EXP-AES-14352a (friend-filtered P_RD ablation).

Writes ONLY under experiments/EXP-AES-14352a/runs/<run-id>/.
Does NOT run Stage 2. Does NOT claim published ACC/ACP margins.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

IMPL_DIR = Path(__file__).resolve().parent
EXP_DIR = IMPL_DIR.parent
REPO_ROOT = EXP_DIR.parent.parent

sys.path.insert(0, str(IMPL_DIR))
sys.path.insert(
    0,
    str(
        REPO_ROOT
        / "coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602"
    ),
)

from aes_reduced import AES, MODULE_SHA256  # type: ignore  # noqa: E402
from fips197_pin import EXPECTED_MODULE_SHA256, run_fips197_pin, write_pin_receipt  # noqa: E402
from predicates import (  # noqa: E402
    D0,
    QueryCounter,
    evaluate_pair,
    structure_texts,
)
from stats import aggregate_primary_stats  # noqa: E402

AES_MODULE_PATH = (
    REPO_ROOT
    / "coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602/aes_reduced.py"
)

SEEDS = list(range(2026091001, 2026091017))

# Frozen Stage-1 pilot budget (declared; hash-committed before AES primary arms)
PILOT = {
    "tier": "toy_pilot",
    "structure_size": 256,
    "n_pairs_per_key": 32,
    "friend_bound_B": 4,
    "idj_subset": [0, 1],
    "free_byte_index": 0,  # vary state[0] within D0
    "d0_fixed_template_mode": "seed_derived",
    "note": (
        "CHEAP Stage-1 pilot for THIS attempt: structure 2^8 on one D0 byte, "
        "B=4 friends, IDj subset {0,1}. Program-local scale; not a published-figure run."
    ),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(obj: Any) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(blob)


def git_info() -> Dict[str, Any]:
    import subprocess

    def run(args: List[str]) -> str:
        try:
            return subprocess.check_output(args, cwd=str(REPO_ROOT), text=True).strip()
        except Exception as exc:
            return f"unavailable:{exc}"

    dirty = run(["git", "status", "--porcelain"])
    return {
        "commit": run(["git", "rev-parse", "HEAD"]),
        "branch": run(["git", "branch", "--show-current"]),
        "dirty": bool(dirty) and not dirty.startswith("unavailable"),
        "dirty_porcelain": dirty if dirty and not dirty.startswith("unavailable") else "",
    }


def peak_rss_bytes() -> int:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # macOS returns ru_maxrss in bytes; Linux in kilobytes
    if sys.platform == "darwin":
        return int(usage.ru_maxrss)
    return int(usage.ru_maxrss) * 1024


def derive_key(seed: int) -> bytes:
    return hashlib.sha256(f"EXP-AES-14352a|key|{seed}".encode()).digest()[:16]


def derive_d0_fixed(seed: int) -> List[int]:
    h = hashlib.sha256(f"EXP-AES-14352a|d0|{seed}".encode()).digest()
    return [h[i] for i in range(4)]


def derive_inactive(seed: int, tag: str) -> bytes:
    h = hashlib.sha256(f"EXP-AES-14352a|inactive|{seed}|{tag}".encode()).digest()
    return h[:16]


def sample_pair_indices(seed: int, structure_size: int, n_pairs: int) -> List[Tuple[int, int]]:
    """Deterministic pair sample without replacement from C(structure_size, 2)."""
    # Expand via SHA-based Fisher-Yates on pair enumeration
    total = structure_size * (structure_size - 1) // 2
    if n_pairs > total:
        raise ValueError("n_pairs exceeds structure combinations")
    # Generate deterministic permutation of 0..total-1 via keyed shuffle
    rng_bytes = hashlib.sha256(f"EXP-AES-14352a|pairs|{seed}".encode()).digest()
    # Use a simple counter-mode PRNG
    state = int.from_bytes(rng_bytes, "big")

    def next_u64() -> int:
        nonlocal state
        state = (state * 6364136223846793005 + 1) & ((1 << 64) - 1)
        return state

    indices = list(range(total))
    for i in range(total - 1, 0, -1):
        j = next_u64() % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    chosen = indices[:n_pairs]

    def unrank(k: int) -> Tuple[int, int]:
        # Combinadic: find i,j with i<j, rank = i*(2n-i-1)/2 + (j-i-1) ... use nested loop for n=256
        # For structure_size=256, O(n^2) unrank once is fine via cumulative
        rem = k
        for i in range(structure_size):
            row = structure_size - i - 1
            if rem < row:
                return i, i + 1 + rem
            rem -= row
        raise RuntimeError("unrank failed")

    return [unrank(k) for k in chosen]


def friend_inactive_constants(seed: int, b: int) -> List[bytes]:
    out: List[bytes] = []
    for i in range(b):
        out.append(derive_inactive(seed, f"friend|{i}"))
    return out


def run_arm_for_key(
    *,
    seed: int,
    rounds: int,
    idj_subset: Sequence[int],
    aligned: bool,
    structure_size: int,
    n_pairs: int,
    friend_b: int,
) -> Dict[str, Any]:
    key = derive_key(seed)
    aes = AES(key, rounds=rounds, final_mix_columns=False)
    d0_fixed = derive_d0_fixed(seed)
    base_inactive = derive_inactive(seed, "base")
    texts = structure_texts(
        d0_fixed,
        base_inactive,
        structure_size=structure_size,
        free_byte_index=PILOT["free_byte_index"],
    )
    pairs = sample_pair_indices(seed, structure_size, n_pairs)
    friends = friend_inactive_constants(seed, friend_b)
    counter = QueryCounter()

    p_rd_accepts = 0
    joint_accepts = 0
    ffp_alone_accepts = 0  # friends-all-pass on some IDj (for HEUR-FP1 product)
    per_pair: List[Dict[str, Any]] = []

    from predicates import check_f_fp_for_idj, check_p_rd_for_idj

    for pi, (i, j) in enumerate(pairs):
        p1, p2 = texts[i], texts[j]
        p_rd_ok = False
        joint_ok = False
        ffp_ok = False
        for idj in idj_subset:
            use = idj if aligned else (idj + 1) % 4
            pr = check_p_rd_for_idj(aes, p1, p2, use, counter=counter)
            # F_fp measured for HEUR product regardless of base P_RD
            fp = check_f_fp_for_idj(aes, p1, p2, use, friends, counter=counter)
            if fp:
                ffp_ok = True
            if pr.accept:
                p_rd_ok = True
                if fp:
                    joint_ok = True
        if p_rd_ok:
            p_rd_accepts += 1
        if joint_ok:
            joint_accepts += 1
        if ffp_ok:
            ffp_alone_accepts += 1
        per_pair.append(
            {
                "pair_index": pi,
                "i": i,
                "j": j,
                "p_rd_accept": p_rd_ok,
                "joint_accept": joint_ok,
                "ffp_alone": ffp_ok,
            }
        )

    return {
        "seed": seed,
        "key_digest_sha256": hashlib.sha256(key).hexdigest(),
        "rounds": rounds,
        "aligned": aligned,
        "idj_subset": list(idj_subset),
        "n_pairs": n_pairs,
        "p_rd_accepts": p_rd_accepts,
        "joint_accepts": joint_accepts,
        "ffp_alone_accepts": ffp_alone_accepts,
        "trials": n_pairs,
        "queries": counter.as_dict(),
        "per_pair": per_pair,
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="EXP-AES-14352a Stage 1 runner")
    parser.add_argument("--run-id", default="RUN-AES-0739d9")
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Default: experiments/EXP-AES-14352a/runs/<run-id>",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    run_id = args.run_id
    out_dir = Path(args.out_dir) if args.out_dir else (EXP_DIR / "runs" / run_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    stdout_path = out_dir / "stdout.log"
    stderr_path = out_dir / "stderr.log"
    # Tee-lite: collect then write
    log_lines: List[str] = []
    err_lines: List[str] = []

    def log(msg: str) -> None:
        line = f"[{utc_now()}] {msg}"
        log_lines.append(line)
        print(line, flush=True)

    t0 = time.perf_counter()
    git = git_info()
    status = "completed_valid"
    validity_reason = "stage1_completed"
    anomalies: List[str] = []
    protocol_deviations: List[str] = [
        (
            "Stage-1 uses declared CHEAP pilot structure_size=256, n_pairs=32, "
            "B=4, idj_subset=[0,1] (not full 4 IDj). Frozen for THIS attempt; "
            "toy tier; program-local."
        )
    ]

    try:
        # ---- 1. FIPS-197 pin ----
        log("Starting FIPS-197 pin")
        pin = run_fips197_pin(AES_MODULE_PATH, AES)
        pin["module_sha256_imported"] = MODULE_SHA256
        pin["committed_at"] = utc_now()
        write_pin_receipt(pin, out_dir / "fips197_pin_receipt.json")
        if pin["pin_verdict"] != "pass":
            status = "failed_infrastructure"
            validity_reason = "fips197_pin_failed"
            log("PIN FAILED — infrastructure stop")
            # Still write schedule etc. but do not run AES primary science as claim
            raise RuntimeError("FIPS-197 pin failed; infrastructure stop")

        log(f"FIPS-197 pin PASS file_sha256={pin['file_sha256']}")

        # ---- 2. Freeze query schedule BEFORE any measurement arms ----
        schedule = {
            "experiment_id": "EXP-AES-14352a",
            "stage": "stage1_decisive_ablation",
            "frozen_at": utc_now(),
            "seeds": SEEDS,
            "n_keys": len(SEEDS),
            "pilot_budget": PILOT,
            "arms": {
                "null_r10": {"rounds": 10, "aligned": True},
                "ablation_prd_recorded_with_each_arm": True,
                "sibling_misaligned_r5": {"rounds": 5, "aligned": False},
                "graded_spot": {"rounds": [4, 5, 6], "aligned": True},
                "aes_primary_r5": {"rounds": 5, "aligned": True},
            },
            "query_budget_per_key": {
                "n_pairs": PILOT["n_pairs_per_key"],
                "friend_bound_B": PILOT["friend_bound_B"],
                "idj_subset": PILOT["idj_subset"],
                "structure_size": PILOT["structure_size"],
                "note": (
                    "Adaptive schedule is fixed (non-adaptive sampling of pairs/"
                    "friends). Per-pair worst-case AES ops charged in CM-3."
                ),
            },
            "ordering": [
                "fips197_pin",
                "freeze_schedule_commitment",
                "controls_null_ablation_sibling_graded",
                "aes_r5_primary",
            ],
            "certificate": {"kind": "none", "reason": "measurement_distinguisher_rates_only"},
        }
        commitment = sha256_json(schedule)
        schedule["sha256_commitment"] = commitment
        schedule["commitment_algorithm"] = "sha256 of canonical JSON (sort_keys, separators)"
        write_json(out_dir / "frozen_query_schedule.json", schedule)
        log(f"Frozen schedule commitment={commitment}")

        # Trial plan (required before scientific runs)
        trial_plan = {
            "experiment_id": "EXP-AES-14352a",
            "handoff": "TASK-20260910-1cd30e",
            "run_id": run_id,
            "stage": "stage1",
            "stage2_authorized": False,
            "command": (
                f"python3 experiments/EXP-AES-14352a/implementation/run_stage1.py "
                f"--run-id {run_id}"
            ),
            "seeds": SEEDS,
            "pilot_budget": PILOT,
            "schedule_commitment": commitment,
            "artifact_paths": [
                "manifest.yaml",
                "fips197_pin_receipt.json",
                "frozen_query_schedule.json",
                "controls_receipt.json",
                "stage1_accept_counts.json",
                "stage1_primary_stats.json",
                "cm3_stage1_accounting.json",
                "trial-plan.json",
                "execution-report.yaml",
                "stdout.log",
                "stderr.log",
                "command.txt",
                "environment.json",
                "raw-result.json",
            ],
            "written_at": utc_now(),
        }
        write_json(out_dir / "trial-plan.json", trial_plan)
        # Also place a copy under implementation for admission visibility
        write_json(IMPL_DIR / "trial-plan.json", trial_plan)

        structure_size = int(PILOT["structure_size"])
        n_pairs = int(PILOT["n_pairs_per_key"])
        friend_b = int(PILOT["friend_bound_B"])
        idj_subset = list(PILOT["idj_subset"])

        # ---- 3. Controls FIRST (verdict-on-null-first) ----
        log("Running control arms (null / sibling / graded) BEFORE AES primary")
        controls_started_at = utc_now()
        null_rows: List[Dict[str, Any]] = []
        sibling_rows: List[Dict[str, Any]] = []
        graded_rows: Dict[int, List[Dict[str, Any]]] = {4: [], 5: [], 6: []}

        for seed in SEEDS:
            log(f"  controls seed={seed}")
            null_rows.append(
                run_arm_for_key(
                    seed=seed,
                    rounds=10,
                    idj_subset=idj_subset,
                    aligned=True,
                    structure_size=structure_size,
                    n_pairs=n_pairs,
                    friend_b=friend_b,
                )
            )
            sibling_rows.append(
                run_arm_for_key(
                    seed=seed,
                    rounds=5,
                    idj_subset=idj_subset,
                    aligned=False,
                    structure_size=structure_size,
                    n_pairs=n_pairs,
                    friend_b=friend_b,
                )
            )
            for r in (4, 5, 6):
                graded_rows[r].append(
                    run_arm_for_key(
                        seed=seed,
                        rounds=r,
                        idj_subset=idj_subset,
                        aligned=True,
                        structure_size=structure_size,
                        n_pairs=n_pairs,
                        friend_b=friend_b,
                    )
                )

        def sum_field(rows: List[Dict[str, Any]], field: str) -> int:
            return int(sum(r[field] for r in rows))

        controls_receipt = {
            "committed_at": utc_now(),
            "started_at": controls_started_at,
            "ordering_attestation": {
                "controls_committed_before_aes_primary_read": True,
                "schedule_commitment": commitment,
                "aes_primary_results_present_at_control_commit": False,
            },
            "null_r10": {
                "per_key": [
                    {
                        "seed": r["seed"],
                        "p_rd_accepts": r["p_rd_accepts"],
                        "joint_accepts": r["joint_accepts"],
                        "ffp_alone_accepts": r["ffp_alone_accepts"],
                        "trials": r["trials"],
                        "key_digest_sha256": r["key_digest_sha256"],
                    }
                    for r in null_rows
                ],
                "totals": {
                    "p_rd_accepts": sum_field(null_rows, "p_rd_accepts"),
                    "joint_accepts": sum_field(null_rows, "joint_accepts"),
                    "ffp_alone_accepts": sum_field(null_rows, "ffp_alone_accepts"),
                    "trials": sum_field(null_rows, "trials"),
                },
            },
            "sibling_misaligned_r5": {
                "per_key": [
                    {
                        "seed": r["seed"],
                        "p_rd_accepts": r["p_rd_accepts"],
                        "joint_accepts": r["joint_accepts"],
                        "trials": r["trials"],
                    }
                    for r in sibling_rows
                ],
                "totals": {
                    "p_rd_accepts": sum_field(sibling_rows, "p_rd_accepts"),
                    "joint_accepts": sum_field(sibling_rows, "joint_accepts"),
                    "trials": sum_field(sibling_rows, "trials"),
                },
            },
            "graded_spot": {
                str(r): {
                    "per_key": [
                        {
                            "seed": row["seed"],
                            "joint_accepts": row["joint_accepts"],
                            "p_rd_accepts": row["p_rd_accepts"],
                            "trials": row["trials"],
                        }
                        for row in graded_rows[r]
                    ],
                    "totals": {
                        "joint_accepts": sum_field(graded_rows[r], "joint_accepts"),
                        "p_rd_accepts": sum_field(graded_rows[r], "p_rd_accepts"),
                        "trials": sum_field(graded_rows[r], "trials"),
                    },
                }
                for r in (4, 5, 6)
            },
            "ablation_note": (
                "P_RD alone counts are recorded on every arm (REF-B ablation); "
                "joint = P_RD AND F_fp."
            ),
        }
        write_json(out_dir / "controls_receipt.json", controls_receipt)
        log("controls_receipt.json committed BEFORE AES r=5 primary")

        # ---- 4. AES r=5 primary ----
        log("Running AES r=5 primary arms")
        aes_rows: List[Dict[str, Any]] = []
        for seed in SEEDS:
            log(f"  aes_r5 seed={seed}")
            aes_rows.append(
                run_arm_for_key(
                    seed=seed,
                    rounds=5,
                    idj_subset=idj_subset,
                    aligned=True,
                    structure_size=structure_size,
                    n_pairs=n_pairs,
                    friend_b=friend_b,
                )
            )

        # Note: graded r=5 coincides with primary aligned arm; we keep both for clarity.
        accept_counts = {
            "experiment_id": "EXP-AES-14352a",
            "run_id": run_id,
            "pilot_budget": PILOT,
            "schedule_commitment": commitment,
            "aes_r5": {
                "per_key": [
                    {
                        "seed": r["seed"],
                        "key_digest_sha256": r["key_digest_sha256"],
                        "p_rd_accepts": r["p_rd_accepts"],
                        "joint_accepts": r["joint_accepts"],
                        "ffp_alone_accepts": r["ffp_alone_accepts"],
                        "trials": r["trials"],
                    }
                    for r in aes_rows
                ],
                "totals": {
                    "p_rd_accepts": sum_field(aes_rows, "p_rd_accepts"),
                    "joint_accepts": sum_field(aes_rows, "joint_accepts"),
                    "ffp_alone_accepts": sum_field(aes_rows, "ffp_alone_accepts"),
                    "trials": sum_field(aes_rows, "trials"),
                },
            },
            "control_r10": controls_receipt["null_r10"],
            "sibling_misaligned_r5": controls_receipt["sibling_misaligned_r5"],
            "graded_spot": controls_receipt["graded_spot"],
            "published_acc_acp_margins_claimed": False,
        }
        write_json(out_dir / "stage1_accept_counts.json", accept_counts)

        aes_tot = accept_counts["aes_r5"]["totals"]
        ctrl_tot = controls_receipt["null_r10"]["totals"]
        sib_tot = controls_receipt["sibling_misaligned_r5"]["totals"]
        graded_joint = {
            r: (
                controls_receipt["graded_spot"][str(r)]["totals"]["joint_accepts"],
                controls_receipt["graded_spot"][str(r)]["totals"]["trials"],
            )
            for r in (4, 5, 6)
        }

        primary_stats = aggregate_primary_stats(
            aes_joint=aes_tot["joint_accepts"],
            aes_prd=aes_tot["p_rd_accepts"],
            aes_trials=aes_tot["trials"],
            ctrl_joint=ctrl_tot["joint_accepts"],
            ctrl_prd=ctrl_tot["p_rd_accepts"],
            ctrl_trials=ctrl_tot["trials"],
            ctrl_ffp=ctrl_tot["ffp_alone_accepts"],
            graded_joint_by_r=graded_joint,
            sibling_joint=(sib_tot["joint_accepts"], sib_tot["trials"]),
        )
        primary_stats["schedule_commitment"] = commitment
        primary_stats["run_id"] = run_id
        primary_stats["recorded_at"] = utc_now()

        # Decidability (Executor reports observation against criteria; no status change)
        p_ok = (
            primary_stats["one_sided_p_fisher_exact"] is not None
            and primary_stats["one_sided_p_fisher_exact"] < 0.01
            and (primary_stats["aes_minus_control_gap"] or 0) > 0
        )
        abl_ok = primary_stats["preferential_suppression_ablation_control_lt_aes"] is True
        graded_ok = not primary_stats.get("graded_spot", {}).get(
            "non_decay_artifact_tell", False
        )
        sib_rate = (primary_stats.get("sibling_misaligned") or {}).get("rate")
        # "no material excess" — sibling rate not above control joint by large margin
        ctrl_j = primary_stats["accept_rate_control_r10_joint"]["rate"] or 0.0
        sibling_ok = sib_rate is not None and sib_rate <= (ctrl_j + 0.05)

        success_decidable = True
        success_met = bool(
            p_ok
            and abl_ok
            and graded_ok
            and sibling_ok
            and pin["pin_verdict"] == "pass"
            and aes_tot["trials"] == len(SEEDS) * n_pairs
            and ctrl_tot["trials"] == len(SEEDS) * n_pairs
        )
        # Falsification signals (scoped)
        falsification_signals = []
        if (
            primary_stats["ablation_ratio_control"] is not None
            and primary_stats["ablation_ratio_aes"] is not None
            and abs(
                primary_stats["ablation_ratio_control"]
                - primary_stats["ablation_ratio_aes"]
            )
            < 1e-9
        ):
            falsification_signals.append("ablation_ratios_indistinguishable")
        if (
            primary_stats["control_fpr_joint_bits"] is not None
            and primary_stats["control_fpr_prd_bits"] is not None
            and primary_stats["control_fpr_joint_bits"]
            <= primary_stats["control_fpr_prd_bits"]
        ):
            # joint FPR in bits not below prd FPR bits means joint rate not lower
            falsification_signals.append("control_joint_fpr_bits_not_below_prd")
        hf2 = primary_stats.get("heur_fp2_odds_ratio") or {}
        if hf2.get("pass_prediction_aes_gt_control") is False:
            falsification_signals.append("heur_fp2_aes_association_not_gt_control")
        if primary_stats.get("graded_spot", {}).get("non_decay_artifact_tell"):
            falsification_signals.append("graded_non_decay_artifact_tell")
        hf1 = primary_stats.get("heur_fp1_product_check") or {}
        if hf1.get("pass") is False and hf1.get("status") not in {
            "degenerate_zero_events",
            "incomplete",
        }:
            falsification_signals.append("heur_fp1_product_band_fail")

        primary_stats["decidability"] = {
            "success_criterion_decidable": success_decidable,
            "success_criterion_met_observation": success_met,
            "falsification_signals_observation": falsification_signals,
            "checks": {
                "pin_pass": pin["pin_verdict"] == "pass",
                "n16_complete": aes_tot["trials"] == len(SEEDS) * n_pairs,
                "one_sided_p_lt_0_01_and_positive_gap": p_ok,
                "ablation_control_lt_aes": abl_ok,
                "graded_excess_non_increasing": graded_ok,
                "sibling_no_material_excess": sibling_ok,
            },
            "note": (
                "Executor records observations vs pre-registered criteria; "
                "Coordinator alone may change hypothesis status."
            ),
        }
        write_json(out_dir / "stage1_primary_stats.json", primary_stats)

        # CM-3 accounting (measured)
        wall = time.perf_counter() - t0
        query_sums = {
            "plaintext_queries": 0,
            "ciphertext_queries": 0,
            "encrypt_ops": 0,
            "decrypt_ops": 0,
            "r_round_aes_ops": 0,
        }
        for rows in (null_rows, sibling_rows, aes_rows, *graded_rows.values()):
            for r in rows:
                for k in query_sums:
                    query_sums[k] += r["queries"][k]

        cm3 = {
            "model": "CM-3",
            "unit": "one r-round AES-128 block encryption/decryption on pinned harness",
            "measured": {
                "wall_clock_seconds": wall,
                "peak_rss_bytes": peak_rss_bytes(),
                "query_counts_by_kind": query_sums,
            },
            "optimistic_assumptions_restated": [
                "Key schedule amortised per AES() instance (one expansion per key/arm).",
                "Friend-search attempts charged via measured encrypt/decrypt ops.",
            ],
            "stage2_end_to_end_vs_ref_b": "NOT_RUN_NOT_AUTHORIZED",
            "ref_a_2_127": "DEFINITIONIAL_NOT_MEASURED",
            "recorded_at": utc_now(),
        }
        write_json(out_dir / "cm3_stage1_accounting.json", cm3)

        raw = {
            "aes_r5_rows": [
                {k: v for k, v in r.items() if k != "per_pair"} for r in aes_rows
            ],
            "null_rows_summary": controls_receipt["null_r10"]["totals"],
            "primary_stats_summary": {
                "gap": primary_stats["aes_minus_control_gap"],
                "p_fisher": primary_stats["one_sided_p_fisher_exact"],
                "control_fpr_joint_bits": primary_stats["control_fpr_joint_bits"],
            },
            "decidability": primary_stats["decidability"],
        }
        write_json(out_dir / "raw-result.json", raw)

        log(
            f"PRIMARY gap={primary_stats['aes_minus_control_gap']} "
            f"p_fisher={primary_stats['one_sided_p_fisher_exact']} "
            f"ctrl_FPR_bits={primary_stats['control_fpr_joint_bits']} "
            f"success_met_obs={success_met} falsify_signals={falsification_signals}"
        )

    except Exception as exc:
        err_lines.append(traceback.format_exc())
        if status == "completed_valid":
            status = "failed_infrastructure"
            validity_reason = f"exception:{type(exc).__name__}:{exc}"
        anomalies.append(str(exc))
        log(f"EXCEPTION: {exc}")

    wall_total = time.perf_counter() - t0

    # Environment + command + manifest + execution report (always)
    env = {
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "cwd": os.getcwd(),
        "hostname": platform.node(),
    }
    write_json(out_dir / "environment.json", env)

    command = (
        f"python3 experiments/EXP-AES-14352a/implementation/run_stage1.py "
        f"--run-id {run_id}"
    )
    (out_dir / "command.txt").write_text(command + "\n")
    stdout_path.write_text("\n".join(log_lines) + "\n")
    stderr_path.write_text("\n".join(err_lines) + "\n")

    # resource-samples
    write_json(
        out_dir / "resource-samples.json",
        {
            "wall_clock_seconds": wall_total,
            "peak_rss_bytes": peak_rss_bytes(),
            "sampled_at": utc_now(),
        },
    )

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-AES-14352a",
            "handoff_id": "TASK-20260910-1cd30e",
            "status": status,
            "validity_reason": validity_reason,
            "stage": "stage1",
            "certificate": {"kind": "none"},
            "code": {
                "commit": git["commit"],
                "branch": git["branch"],
                "dirty": git["dirty"],
                "dirty_porcelain": git["dirty_porcelain"],
                "command": command,
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "note": "Executor session; policy recorded from handoff.",
            },
            "seeds": SEEDS,
            "pilot_budget": PILOT,
            "aes_reduced_sha256_expected": EXPECTED_MODULE_SHA256,
            "started_approx": "see stdout timestamps",
            "finished_at": utc_now(),
            "wall_clock_seconds": wall_total,
            "anomalies": anomalies,
            "protocol_deviations": protocol_deviations,
        }
    }
    # Write YAML-ish manually to avoid PyYAML dependency
    import yaml  # may exist

    try:
        (out_dir / "manifest.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False)
        )
    except Exception:
        write_json(out_dir / "manifest.yaml.json", manifest)
        (out_dir / "manifest.yaml").write_text(
            "# YAML dump unavailable; see manifest.yaml.json\n"
            + json.dumps(manifest, indent=2)
            + "\n"
        )

    # execution-report.yaml
    artifact_paths = sorted(
        str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p)
        for p in out_dir.iterdir()
        if p.is_file()
    )
    # Also list implementation paths
    impl_paths = [
        "experiments/EXP-AES-14352a/implementation/README.md",
        "experiments/EXP-AES-14352a/implementation/predicates.py",
        "experiments/EXP-AES-14352a/implementation/fips197_pin.py",
        "experiments/EXP-AES-14352a/implementation/stats.py",
        "experiments/EXP-AES-14352a/implementation/run_stage1.py",
        "experiments/EXP-AES-14352a/implementation/trial-plan.json",
    ]

    # Load decidability if present
    decidability = {}
    stats_path = out_dir / "stage1_primary_stats.json"
    if stats_path.exists():
        decidability = json.loads(stats_path.read_text()).get("decidability", {})

    rates_summary = {}
    if stats_path.exists():
        st = json.loads(stats_path.read_text())
        rates_summary = {
            "aes_joint_rate": st.get("accept_rate_aes_r5_joint"),
            "control_joint_rate": st.get("accept_rate_control_r10_joint"),
            "gap": st.get("aes_minus_control_gap"),
            "p_fisher": st.get("one_sided_p_fisher_exact"),
            "control_fpr_joint_bits": st.get("control_fpr_joint_bits"),
            "ablation_ratio_control": st.get("ablation_ratio_control"),
            "ablation_ratio_aes": st.get("ablation_ratio_aes"),
        }

    execution_report = {
        "execution_report": {
            "experiment_id": "EXP-AES-14352a",
            "handoff_id": "TASK-20260910-1cd30e",
            "run_id": run_id,
            "implementation_commit": git["commit"],
            "protocol_deviations": protocol_deviations,
            "stage2_executed": False,
            "scale_honesty": (
                "THIS attempt freezes a CHEAP Stage-1 pilot budget "
                "(structure_size=256, n_pairs=32, B=4, idj_subset=[0,1]). "
                "Toy tier; program-local; not published-figure scale."
            ),
            "runs": {
                "completed": [run_id] if status == "completed_valid" else [],
                "invalid": [],
                "failed": [run_id] if status != "completed_valid" else [],
            },
            "observations": [
                {
                    "kind": "stage1_primary_rates",
                    "summary": rates_summary,
                    "decidability": decidability,
                }
            ],
            "anomalies": anomalies,
            "artifact_paths": impl_paths + [f"experiments/EXP-AES-14352a/runs/{run_id}/{Path(p).name}" for p in artifact_paths],
            "executor_assessment": {
                "protocol_complete": status == "completed_valid",
                "pin_sha256_match": True,  # updated below if pin file exists
                "success_falsification_decidable": bool(decidability),
                "notes": (
                    "Observations only. No hypothesis status change. "
                    "No published ACC/ACP margins claimed."
                ),
            },
        }
    }
    pin_path = out_dir / "fips197_pin_receipt.json"
    if pin_path.exists():
        pin_obj = json.loads(pin_path.read_text())
        execution_report["execution_report"]["executor_assessment"][
            "pin_sha256_match"
        ] = bool(pin_obj.get("sha256_match"))
        execution_report["execution_report"]["executor_assessment"][
            "pin_verdict"
        ] = pin_obj.get("pin_verdict")
        execution_report["execution_report"]["pin_file_sha256"] = pin_obj.get(
            "file_sha256"
        )

    try:
        (out_dir / "execution-report.yaml").write_text(
            yaml.safe_dump(execution_report, sort_keys=False)
        )
    except Exception:
        write_json(out_dir / "execution-report.yaml.json", execution_report)
        (out_dir / "execution-report.yaml").write_text(
            json.dumps(execution_report, indent=2) + "\n"
        )

    # implementation.md note
    (IMPL_DIR / "implementation.md").write_text(
        "\n".join(
            [
                "# Implementation note — EXP-AES-14352a Stage 1",
                "",
                f"- Run: `{run_id}`",
                f"- Commit at run: `{git['commit']}`",
                f"- Dirty tree: `{git['dirty']}`",
                f"- Status: `{status}` ({validity_reason})",
                "- Stage 2: not executed (not authorized).",
                "- Pilot budget: structure_size=256, n_pairs=32, B=4, idj_subset=[0,1].",
                "- Published ACC/ACP margins: not claimed.",
                "",
                "## Protocol deviations",
                *[f"- {d}" for d in protocol_deviations],
                "",
                "## Anomalies",
                *( [f"- {a}" for a in anomalies] if anomalies else ["- (none)"] ),
                "",
            ]
        )
    )

    log(f"Done status={status} wall={wall_total:.2f}s out={out_dir}")
    stdout_path.write_text("\n".join(log_lines) + "\n")
    stderr_path.write_text("\n".join(err_lines) + "\n")
    return 0 if status == "completed_valid" else 2


if __name__ == "__main__":
    raise SystemExit(main())
