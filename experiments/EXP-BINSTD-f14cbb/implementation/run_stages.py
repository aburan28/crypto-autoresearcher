"""Driver for EXP-BINSTD-f14cbb Stages 0/1/2.

Writes stage YAML/MD artifacts and immutable run packages under runs/.
Does not overwrite prior run directories.
"""
from __future__ import annotations

import json
import os
import platform
import resource
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parents[1] if (EXP.parents[1] / "tools").is_dir() else EXP.parents[0]
# EXP = experiments/EXP-BINSTD-f14cbb; parents[0]=experiments, parents[1]=repo
for p in [EXP.parent.parent, Path("/workspace")]:
    if (p / "tools" / "allocate_id.py").is_file():
        REPO = p
        break

sys.path.insert(0, str(HERE))

from cyclotomic import run_stage0
from torus_row import run_stage1, run_stage2

TASK_ID = "TASK-20261001-109e55"
EXP_ID = "EXP-BINSTD-f14cbb"
# Pre-minted and --check'd free run IDs
RUN_STAGE0 = "RUN-BINSTD-59f5ad"
RUN_STAGE1 = "RUN-BINSTD-aeaa1b"
RUN_STAGE2 = "RUN-BINSTD-9fcb73"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(REPO), text=True
        ).strip()
    except Exception:
        return "unknown"


def git_dirty() -> bool:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=str(REPO), text=True
        )
        return bool(out.strip())
    except Exception:
        return True


def peak_rss() -> int:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # Linux: ru_maxrss in kilobytes
    return int(usage.ru_maxrss * 1024)


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2, default=str)
        f.write("\n")


def write_run_package(
    run_id: str,
    stage: str,
    command: str,
    raw: Dict[str, Any],
    stdout_text: str,
    stderr_text: str,
    started: str,
    finished: str,
    wall_s: float,
    status: str,
    termination_reason: str,
    metrics: Dict[str, Any],
    seed: Optional[int] = None,
    invalid_reason: Optional[str] = None,
) -> Path:
    run_dir = EXP / "runs" / run_id
    if run_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing run {run_dir}")
    run_dir.mkdir(parents=True)

    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "dependencies": {"pyyaml": getattr(__import__("yaml"), "__version__", "unknown")},
        "hostname": platform.node(),
    }
    write_json(run_dir / "environment.json", env)
    (run_dir / "command.txt").write_text(command + "\n")
    (run_dir / "stdout.log").write_text(stdout_text)
    (run_dir / "stderr.log").write_text(stderr_text)
    write_json(run_dir / "raw-result.json", raw)

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": stage,
            "status": status,
            "termination_reason": termination_reason,
            "code": {
                "commit": git_commit(),
                "dirty": git_dirty(),
                "command": command,
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "canonical_policy": "executor-implementation",
                "backend": None,
                "provider": None,
                "resolved_model_id": None,
                "model_provenance": "not-applicable",
                "model_verified": False,
                "requested_reasoning_effort": None,
                "reasoning_effort": None,
                "fallback_used": False,
                "fallback_reason": None,
                "degraded_requirements": [],
                "independent_session": False,
                "adapter_version": None,
                "config_digest": None,
            },
            "environment": {
                "operating_system": env["operating_system"],
                "architecture": env["architecture"],
                "sage_version": None,
                "python_version": env["python_version"],
                "dependencies": env["dependencies"],
            },
            "inputs": {
                "curve_id": None,
                "seed": seed,
                "parameters": {"stage": stage},
            },
            "timing": {
                "started_at": started,
                "finished_at": finished,
                "wall_seconds": wall_s,
            },
            "resources": {
                "peak_rss_bytes": peak_rss(),
                "cpu_seconds": None,
            },
            "result": {
                "metrics": metrics,
                "valid": status == "completed_valid",
                "invalid_reason": invalid_reason,
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "verifier": "structural-arithmetic-no-discrete-log",
                    "notes": (
                        "Structural cyclotomic / Lemma-L measurement; "
                        "certificate.kind is none by docs/claims-and-verification.md "
                        "(not a DL/decomp/key claim). No break/rho claim."
                    ),
                },
            },
        }
    }
    write_yaml(run_dir / "manifest.yaml", manifest)
    return run_dir


def do_stage0() -> Dict[str, Any]:
    started = utc_now()
    t0 = time.time()
    cmd = (
        f"python3 {HERE / 'run_stages.py'} --stage 0"
    )
    try:
        result = run_stage0(20000)
        wall = time.time() - t0
        result["wall_s"] = wall
        result["peak_rss_bytes"] = peak_rss()
        term = "completed"
        status = "completed_valid"
        err = ""
    except Exception as e:
        wall = time.time() - t0
        result = {"error": str(e), "traceback": traceback.format_exc()}
        term = "failed_infrastructure"
        status = "failed_infrastructure"
        err = traceback.format_exc()

    # Write stage0 artifacts (even on partial failure, write what we have)
    s0 = EXP / "stage0"
    s0.mkdir(parents=True, exist_ok=True)

    if term == "completed":
        write_yaml(
            s0 / "cyclotomic-divisor-set.yaml",
            {
                "experiment_id": EXP_ID,
                "p": 131,
                "a": 2,
                "k_max": 20000,
                "k_set": result["hits_p131"],
                "expected_k_set": [130, 17030],
                "match": result["p131_match"],
                "unexpected_k_inspection": result["unexpected_k_inspection"],
                "unexpected_k_notes": result["unexpected_k_notes"],
                "method": "Moebius product via v_p(2^d-1) modular lifting",
                "measured_vs_modeled": "measured",
                "run_id": RUN_STAGE0,
            },
        )
        write_yaml(
            s0 / "phi-values.yaml",
            {
                "experiment_id": EXP_ID,
                "phi_values": result["phi_values"],
                "expected_phi": {130: 48, 17030: 6240},
                "match": result["phi_match"],
                "measured_vs_modeled": "measured",
                "run_id": RUN_STAGE0,
            },
        )
        write_yaml(
            s0 / "Phi_130_factorisation.yaml",
            {
                "experiment_id": EXP_ID,
                **result["Phi_130_factorisation"],
                "measured_vs_modeled": "measured",
                "run_id": RUN_STAGE0,
            },
        )
        write_yaml(
            s0 / "modulus-swap-p17.yaml",
            {
                "experiment_id": EXP_ID,
                "p": 17,
                "a": 2,
                "k_max": 20000,
                "k_set": result["hits_p17"],
                "expected_k_set": [8, 136, 2312],
                "match": result["p17_match"],
                "control": "modulus_swap_p17",
                "measured_vs_modeled": "measured",
                "run_id": RUN_STAGE0,
            },
        )
        write_yaml(
            s0 / "preregistered-predictions.yaml",
            {
                "experiment_id": EXP_ID,
                "written_before_stage1_stage2_outcome_claims": True,
                "frozen_from": "experiments/EXP-BINSTD-f14cbb/specification.yaml",
                "heuristic_under_test": [
                    "HEUR-BINSTD-41d8b2-H0",
                    "HEUR-BINSTD-41d8b2-H1",
                ],
                "predictions": {
                    "A_cyclotomic_set": {
                        "quantity": "{k<=20000: 131|Phi_k(2)}",
                        "expected": [130, 17030],
                        "phi_expected": {130: 48, 17030: 6240},
                        "measured_vs_modeled": "measured",
                    },
                    "B_Phi_130": {
                        "quantity": "Phi_130(2) factorisation and v_131",
                        "expected_value": 409368176241571,
                        "expected_cofactor": 3124947910241,
                        "expected_v_131": 1,
                        "crosscheck": "(2^65+1)/(8193*11)",
                        "measured_vs_modeled": "measured",
                    },
                    "C_toy_n17": {
                        "quantity": "n=17 Lemma L image",
                        "expected_dim": 8,
                        "expected_stable": True,
                        "expected_equals_ker_mt": True,
                        "random_b_stable_count_max": 1,
                        "measured_vs_modeled": "measured (null rate HEUR-H1 is modeled prior)",
                    },
                    "D_n131": {
                        "quantity": "n=131 image dim and T_0 equality",
                        "expected_dim": 130,
                        "expected_equals": "T_0",
                        "measured_vs_modeled": "measured",
                    },
                    "E_analytic_unknowns": {
                        "quantity": "unknowns/slot vs one-hot",
                        "expected_lower": 17030,
                        "onehot_bits": 131,
                        "measured_vs_modeled": "modeled/analytic — never a measured solver column",
                    },
                },
                "outcomes_predefined": {
                    "A": (
                        "set {130,17030}, v_131=1, n=17 dim=8 stable equals ker, "
                        "random-b stable <=1/10, n=131 dim=130 equals T_0"
                    ),
                    "B": "toy not stable OR dim outside {0,1,8,9,16,17}",
                    "C": "some k<=20000 with 131|Phi_k(2) and phi(k)<48",
                },
                "note": (
                    "Timeout/OOM is failed_infrastructure, never outcome A/B/C. "
                    "No break/rho/Couveignes–Lercier-primary-read claim."
                ),
            },
        )
        (s0 / "methodological-note.md").write_text(
            """# Methodological note — EXP-BINSTD-f14cbb

## Scope

Structural-certificate / arithmetic measurement for the KN-OPEN-095df5 torus
row under H-BINSTD-41d8b2. **No curve ECDLP**, no GHS/decomposition attack at
n>=131, no factor-base construction, no rho competitiveness claim.

## Certificate vocabulary

Every run manifest sets `certificate.kind: none` (closed set:
`discrete_log | decomposition | key_recovery | none`). This experiment emits
structural cyclotomic and Lemma-L observations only.

## Stage 0 instrument

Moebius product for `Phi_k(2)` with `v_p(2^d-1)` via modular lifting. Does
**not** assume the recalled cyclotomic-divisor lemma
(`p|Phi_k(a) <=> k=p^j ord_p(a)`); that lemma is what the census tests on
`k<=20000`. Exact `Phi_130(2)` uses the integer Moebius product plus the
`(2^65+1)/(8193*11)` cross-check.

## Stage 1 / 2 instrument

Composite-field arithmetic `F_(2^{k n}) = F_(2^k)·F_(2^n)` (`composite_field.py`)
with CRT relative Frobenius. Self-contained `gf2n_local.py` (schoolbook);
optional conceptual kinship to `EXP-CERTBIN-e94b27/impl/gf2n.py` but **no import**.

## Claim guards

- Do **not** claim Couveignes–Lercier primary text was read.
- Do **not** claim a break, factor base, or rho competitiveness.
- Timeout / OOM / crash → `failed_infrastructure`, **never** outcome A/B/C.
- Measured columns (sets, valuations, dims, stability, null counts, wall_s,
  peak_rss) stay separate from modeled/analytic priors (HEUR-H1 2^-8 cap;
  17030 unknowns/slot).
- Amazon Bedrock prohibited.
- No AUXIN edits; no H/EXP/IDEA status edits by the executor.

## Outcomes

Outcomes A/B/C are recorded as comparisons against preregistered predictions
for the Coordinator/Reviewer; this packet reports observations only.
"""
        )

    stdout = json.dumps(result, indent=2, default=str)
    write_run_package(
        RUN_STAGE0,
        "0-cyclotomic",
        cmd,
        result,
        stdout,
        err,
        started,
        utc_now(),
        wall,
        status,
        term,
        {
            "cyclotomic_k_set": result.get("hits_p131"),
            "phi_values": result.get("phi_values"),
            "v_131_Phi_130": (result.get("Phi_130_factorisation") or {}).get("v_131"),
            "p131_match": result.get("p131_match"),
            "p17_match": result.get("p17_match"),
            "wall_s": wall,
            "peak_rss_bytes": peak_rss(),
            "field_impl_used": "integer_moebius",
            "termination_reason": term,
        },
        seed=None,
        invalid_reason=None if status == "completed_valid" else term,
    )
    return {"run_id": RUN_STAGE0, "status": status, "termination_reason": term, "result": result}


def do_stage1() -> Dict[str, Any]:
    started = utc_now()
    t0 = time.time()
    cmd = f"python3 {HERE / 'run_stages.py'} --stage 1"
    seed = 20261001
    try:
        result = run_stage1(seed=seed, random_b_trials=10, order15_trials=10)
        # second seed replication note embedded
        result_seed2 = run_stage1(seed=20261002, random_b_trials=10, order15_trials=10)
        result["replication_seed_20261002"] = {
            "dim": result_seed2["toy"]["dim"],
            "stable": result_seed2["toy"]["frobenius_stable"],
            "equals_ker": result_seed2["toy"]["equals_ker_mt_sigma"],
            "random_b_stable_count": result_seed2["random_b"]["stable_count"],
            "basis_relabel_invariant": result_seed2["basis_relabel"]["basis_relabel_invariant"],
            "wall_s": result_seed2["wall_s"],
        }
        wall = time.time() - t0
        result["wall_s_total"] = wall
        result["peak_rss_bytes"] = peak_rss()
        term = result.get("termination_reason", "completed")
        if term == "completed":
            status = "completed_valid"
        else:
            status = "failed_infrastructure"
        err = ""
    except Exception as e:
        wall = time.time() - t0
        result = {"error": str(e), "traceback": traceback.format_exc()}
        term = "failed_infrastructure"
        status = "failed_infrastructure"
        err = traceback.format_exc()

    s1 = EXP / "stage1"
    s1.mkdir(parents=True, exist_ok=True)
    if "toy" in result:
        write_yaml(
            s1 / "lemma-L-toy-n17.yaml",
            {
                "experiment_id": EXP_ID,
                "run_id": RUN_STAGE1,
                "n": 17,
                "ord_n_2": 8,
                "ambient_bits": 136,
                "field_impl_used": result.get("field_impl_used"),
                "seed": seed,
                "torsor_relation_verified": result.get("torsor_relation_verified"),
                "dim": result["toy"]["dim"],
                "predicted_dim": 8,
                "frobenius_stable": result["toy"]["frobenius_stable"],
                "predicted_stable": True,
                "equals_ker_mt_sigma": result["toy"]["equals_ker_mt_sigma"],
                "minpoly_t": result.get("minpoly_t"),
                "ker_mt_dim": result.get("ker_mt_dim"),
                "both_phi17_factors": result.get("both_phi17_factors"),
                "dim_in_subset_sum": result.get("dim_in_subset_sum"),
                "stable_subset_sum_dims": result.get("stable_subset_sum_dims"),
                "replication_seed_20261002": result.get("replication_seed_20261002"),
                "measured_vs_modeled": "measured",
                "wall_s": result.get("wall_s"),
                "termination_reason": term,
            },
        )
        write_yaml(
            s1 / "nulls-random-b.yaml",
            {
                "experiment_id": EXP_ID,
                "run_id": RUN_STAGE1,
                "control": "random_b_null",
                "seed": seed,
                "trials": result["random_b"]["trials"],
                "stable_count": result["random_b"]["stable_count"],
                "predicted_stable_count_max": 1,
                "HEUR_H1_modeled_prior": "stability probability <=~2^-8 (modeled; not a measured column)",
                "results": result["random_b"]["results"],
                "replication_seed_20261002_stable_count": (
                    result.get("replication_seed_20261002") or {}
                ).get("random_b_stable_count"),
                "measured_vs_modeled": "measured (count); HEUR-H1 cap is modeled",
                "termination_reason": term,
            },
        )
        write_yaml(
            s1 / "nulls-order15.yaml",
            {
                "experiment_id": EXP_ID,
                "run_id": RUN_STAGE1,
                "control": "order15_null",
                "seed": seed,
                "t15": result["order15"]["t15"],
                "trials": result["order15"]["trials"],
                "results": result["order15"]["results"],
                "note": "Report stability/dim without claiming Lemma L on order-15 fibre",
                "measured_vs_modeled": "measured",
                "termination_reason": term,
            },
        )
        write_yaml(
            s1 / "basis-relabel.yaml",
            {
                "experiment_id": EXP_ID,
                "run_id": RUN_STAGE1,
                "control": "basis_relabel",
                **result["basis_relabel"],
                "measured_vs_modeled": "measured",
                "termination_reason": term,
            },
        )

    stdout = json.dumps(result, indent=2, default=str)
    write_run_package(
        RUN_STAGE1,
        "1-lemma-L-n17",
        cmd,
        result,
        stdout,
        err,
        started,
        utc_now(),
        wall,
        status,
        term,
        {
            "toy_n17_dim": (result.get("toy") or {}).get("dim"),
            "toy_n17_frobenius_stable": (result.get("toy") or {}).get("frobenius_stable"),
            "toy_n17_equals_ker_mt": (result.get("toy") or {}).get("equals_ker_mt_sigma"),
            "random_b_stable_count": (result.get("random_b") or {}).get("stable_count"),
            "basis_relabel_invariant": (result.get("basis_relabel") or {}).get(
                "basis_relabel_invariant"
            ),
            "wall_s": wall,
            "peak_rss_bytes": peak_rss(),
            "field_impl_used": result.get("field_impl_used"),
            "termination_reason": term,
        },
        seed=seed,
        invalid_reason=None if status == "completed_valid" else term,
    )
    return {"run_id": RUN_STAGE1, "status": status, "termination_reason": term, "result": result}


def do_stage2() -> Dict[str, Any]:
    started = utc_now()
    t0 = time.time()
    cmd = f"python3 {HERE / 'run_stages.py'} --stage 2"
    seed = 20261001
    try:
        result = run_stage2(seed=seed, wall_limit_s=7200)
        wall = time.time() - t0
        result["wall_s_driver"] = wall
        result["peak_rss_bytes"] = peak_rss()
        term = result.get("termination_reason", "completed")
        status = "completed_valid" if term == "completed" else "failed_infrastructure"
        err = result.get("error") or ""
    except Exception as e:
        wall = time.time() - t0
        result = {"error": str(e), "traceback": traceback.format_exc()}
        term = "failed_infrastructure"
        status = "failed_infrastructure"
        err = traceback.format_exc()

    s2 = EXP / "stage2"
    s2.mkdir(parents=True, exist_ok=True)
    measured = result.get("measured") or {}
    write_yaml(
        s2 / "lemma-L-n131.yaml",
        {
            "experiment_id": EXP_ID,
            "run_id": RUN_STAGE2,
            "n": 131,
            "ord_n_2": 130,
            "ambient_bits": 17030,
            "predicted_dim": 130,
            "predicted_equals": "T_0",
            "field_impl_used": measured.get("field_impl_used", "composite_field_attempted"),
            "measured": measured,
            "dim": measured.get("dim"),
            "frobenius_stable": measured.get("frobenius_stable"),
            "equals_T0": measured.get("equals_T0_ker_mt"),
            "equals_ker_Tr": measured.get("equals_ker_Tr"),
            "wall_s": result.get("wall_s"),
            "peak_rss_bytes": result.get("peak_rss_bytes"),
            "termination_reason": term,
            "error": result.get("error"),
            "optimistic_assumption_restated": result.get("optimistic_assumption_restated"),
            "measured_vs_modeled": "measured when termination_reason=completed; else infrastructure",
            "note": (
                "Timeout/OOM is failed_infrastructure — do not invent dim=130 "
                "or outcome A/B/C from infrastructure."
            ),
        },
    )
    write_yaml(
        s2 / "unknowns-per-slot.yaml",
        {
            "experiment_id": EXP_ID,
            "run_id": RUN_STAGE2,
            **(result.get("analytic_unknowns_per_slot") or {
                "unknowns_per_slot_lower": 17030,
                "onehot_bits": 131,
                "measured_vs_modeled": "modeled/analytic",
            }),
            "termination_reason": term,
            "note": (
                "Analytic/MODELED rank count from the frozen specification; "
                "not observed from a solver run."
            ),
        },
    )

    stdout = json.dumps(result, indent=2, default=str)
    write_run_package(
        RUN_STAGE2,
        "2-lemma-L-n131",
        cmd,
        result,
        stdout,
        err if isinstance(err, str) else str(err),
        started,
        utc_now(),
        wall,
        status,
        term,
        {
            "n131_dim": measured.get("dim"),
            "n131_equals_T0": measured.get("equals_T0_ker_mt"),
            "analytic_unknowns_per_slot": 17030,
            "wall_s": wall,
            "peak_rss_bytes": peak_rss(),
            "field_impl_used": measured.get("field_impl_used"),
            "termination_reason": term,
        },
        seed=seed,
        invalid_reason=None if status == "completed_valid" else term,
    )
    return {"run_id": RUN_STAGE2, "status": status, "termination_reason": term, "result": result}


def main(argv: List[str]) -> int:
    stage = None
    if "--stage" in argv:
        i = argv.index("--stage")
        stage = argv[i + 1]
    summary = {}
    if stage in (None, "0", "all"):
        print("=== STAGE 0 ===", flush=True)
        summary["stage0"] = do_stage0()
        print("stage0", summary["stage0"]["status"], summary["stage0"]["termination_reason"], flush=True)
    if stage in (None, "1", "all"):
        print("=== STAGE 1 ===", flush=True)
        summary["stage1"] = do_stage1()
        print("stage1", summary["stage1"]["status"], summary["stage1"]["termination_reason"], flush=True)
    if stage in (None, "2", "all"):
        print("=== STAGE 2 ===", flush=True)
        summary["stage2"] = do_stage2()
        print("stage2", summary["stage2"]["status"], summary["stage2"]["termination_reason"], flush=True)

    out_path = EXP / "implementation" / "driver-summary.json"
    write_json(out_path, summary)
    print("wrote", out_path, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
