#!/usr/bin/env python3
"""Independent metadata/custody checks for TASK-20260909-e361c0.

This checker reads and hashes source files but never imports or executes them.
Its malformed controls are serialized and evaluated one at a time in memory.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

import yaml


TASK = "TASK-20260909-e361c0"
PRODUCER_TASK = "TASK-20260909-129bc2"
EXPERIMENT = "EXP-ECDLP-709063"
AUTHORITY = "b63075b91ac2551abd70525bce72a64844c40ecf"
CLAIM = "7f9114194aae018905ccd010f3416b91a1a4e066"
CORRECTION_SNAPSHOT = "7ba5f7ec2ed24876a40ec083ebdc2bef0ef83b25"
SOURCE_SNAPSHOT = "1c9b23b662dbe890c5b6e40a5a05979e15e079d0"
BASELINE_SNAPSHOT = "d8f64d928c8f6a28eed97eac70b741ad3232fbd5"
REVIEW_DIR = Path(
    "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-e361c0"
)
HANDOFF_PATH = Path("ledger/handoffs/TASK-20260909-e361c0.yaml")
PLAN_PATH = Path(
    "coordination/experiment-reserve/BATCH-635652/review-plan-TASK-20260909-e361c0.yaml"
)
CLAIM_PATH = Path(
    "coordination/experiment-reserve/BATCH-635652/claims/TASK-20260909-e361c0.1.claim.json"
)
CORRECTION_DIR = Path(
    "coordination/experiment-reserve/BATCH-635652/corrections/TASK-20260909-129bc2"
)
ORIGINAL_DIR = Path(
    "experiments/EXP-ECDLP-709063/implementation/TASK-20260909-d31be5"
)
FAILED_DIR = Path(
    "experiments/EXP-ECDLP-709063/implementation/TASK-20260909-85c2fe"
)
BASELINE_DIR = Path(
    "experiments/EXP-ECDLP-709063/implementation/TASK-20260908-7771f2"
)
ORIGINAL_ARCHIVE = Path(
    "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260909-7f5fe3/snapshot.json"
)
REVIEW_ARCHIVE = Path(
    "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260909-4607fb/snapshot.json"
)
FAILED_ARCHIVE = Path(
    "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260909-ff426d/snapshot.json"
)
CORRECTION_ARCHIVE = Path(
    "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260909-c0c0d1/snapshot.json"
)
OLD_REVIEW = Path(
    "coordination/experiment-reserve/BATCH-635652/reviews/TASK-20260909-adf4e6/review.yaml"
)
ORIGINAL_HANDOFF = Path("ledger/handoffs/TASK-20260909-d31be5.yaml")
CORRECTION_HANDOFF = Path("ledger/handoffs/TASK-20260909-129bc2.yaml")
SOURCE_NAMES = ("table.py", "bsgs.py", "rho-corrected.py", "tests.py")
INPUT_CAP = 16 * 1024 * 1024
CONTROL_CAP = 1 * 1024 * 1024
CONTROL_SECONDS = 10.0
AGGREGATE_SECONDS = 1800.0
RSS_CAP_BYTES = 2 * 1024 * 1024 * 1024
EXPECTED_INPUT_BYTES = 991_976
EXPECTED_CONTROL_COUNT = 42


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def strict_json_bytes(data: bytes) -> Any:
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique_json_pairs)


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def unique_yaml_mapping(
    loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    out: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in out:
            raise ValueError(f"duplicate YAML key: {key}")
        out[key] = loader.construct_object(value_node, deep=deep)
    return out


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_yaml_mapping
)


def strict_yaml_bytes(data: bytes) -> Any:
    return yaml.load(data.decode("utf-8"), Loader=UniqueKeyLoader)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_utc(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    need(parsed.tzinfo is not None, f"timestamp lacks timezone: {value}")
    return parsed


def normalized_rss_bytes(raw: float, unit: str) -> int:
    if unit == "bytes":
        return int(raw)
    if unit == "KiB":
        return int(raw * 1024)
    raise ValueError(f"unknown RSS unit: {unit}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--claim-commit", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    target = Path(args.receipt).resolve()
    if target.exists():
        raise FileExistsError(f"refuse existing attempt receipt: {target}")

    started_at = utc_now()
    wall_start = time.monotonic()
    cpu_start = time.process_time()
    comparisons: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []
    setup_error: str | None = None
    total_input_bytes: int | None = None

    def git_bytes(commit: str, path: Path) -> bytes:
        result = subprocess.run(
            ["git", "show", f"{commit}:{path.as_posix()}"],
            cwd=repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            raise ValueError(
                f"git show failed for {commit}:{path}: "
                + result.stderr.decode("utf-8", "replace")[:1000]
            )
        return result.stdout

    def is_ancestor(first: str, second: str) -> bool:
        return (
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", first, second],
                cwd=repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            ).returncode
            == 0
        )

    def jload(path: Path) -> Any:
        return strict_json_bytes((repo / path).read_bytes())

    def yload(path: Path) -> Any:
        return strict_yaml_bytes((repo / path).read_bytes())

    def compare(name: str, fn: Callable[[], bool], detail: Any = None) -> None:
        row: dict[str, Any] = {"name": name}
        try:
            need(fn() is True, "comparison returned non-true")
            row["status"] = "passed"
            if detail is not None:
                row["detail"] = detail
        except BaseException as exc:
            row["status"] = "failed"
            row["error"] = f"{type(exc).__name__}: {str(exc)[:2000]}"
        comparisons.append(row)

    try:
        need((repo / "AGENTS.md").is_file(), "--repo lacks AGENTS.md")
        need(args.claim_commit == CLAIM, "unexpected claim commit")
        claim = strict_json_bytes(git_bytes(CLAIM, CLAIM_PATH))
        need(Path(claim["worktree"]).resolve() == repo, "--repo differs from claim")
        need(claim["task_id"] == TASK, "claim task mismatch")
        need(claim["write_scope"] == [
            (REVIEW_DIR / "review.yaml").as_posix(),
            (REVIEW_DIR / "checks.py").as_posix(),
            (REVIEW_DIR / "check-receipt.json").as_posix(),
        ], "claim write scope mismatch")

        handoff = yload(HANDOFF_PATH)["handoff"]
        plan = yload(PLAN_PATH)["review_plan"]
        need(git_bytes(AUTHORITY, HANDOFF_PATH) == (repo / HANDOFF_PATH).read_bytes(), "authority handoff drift")
        need(git_bytes(AUTHORITY, PLAN_PATH) == (repo / PLAN_PATH).read_bytes(), "authority plan drift")
        need(handoff["id"] == TASK and handoff["to"] == "validator", "handoff identity")
        need(handoff["review_plan_path"] == PLAN_PATH.as_posix(), "review plan path")
        need(plan == handoff["review_plan"], "inline/path review plan mismatch")
        need(plan["source_snapshot"] == CORRECTION_SNAPSHOT, "review source snapshot")
        need(
            plan["joints"] == [{
                "joint": "binding_supersession_and_unchanged_source_custody",
                "assigned_to": TASK,
                "attack_plan": plan["joints"][0]["attack_plan"],
                "breaking_artifact": plan["joints"][0]["breaking_artifact"],
            }],
            "unexpected joint assignment",
        )
        need(is_ancestor(CORRECTION_SNAPSHOT, AUTHORITY), "snapshot not ancestor of authority")
        need(is_ancestor(AUTHORITY, CLAIM), "authority not ancestor of claim")

        declared_inputs = handoff["inputs"]
        bindings = handoff["source_bindings"]
        need(len(declared_inputs) == len(bindings) == 42, "review input count")
        need(len(set(declared_inputs)) == 42, "duplicate review input path")
        need([row["path"] for row in bindings] == declared_inputs, "input/binding order mismatch")
        input_rows: list[dict[str, Any]] = []
        total_input_bytes = 0
        for row in bindings:
            path = Path(row["path"])
            expected = row["sha256"]
            commit = AUTHORITY if path == PLAN_PATH else CORRECTION_SNAPSHOT
            frozen = git_bytes(commit, path)
            live = (repo / path).read_bytes()
            total_input_bytes += len(frozen)
            input_rows.append({
                "path": path.as_posix(),
                "commit": commit,
                "bytes": len(frozen),
                "sha256": sha_bytes(frozen),
                "expected_sha256": expected,
                "frozen_matches": sha_bytes(frozen) == expected,
                "live_matches": sha_bytes(live) == expected,
            })
        compare(
            "all_42_declared_inputs_hash_bound",
            lambda: all(r["frozen_matches"] and r["live_matches"] for r in input_rows),
            input_rows,
        )
        compare(
            "frozen_input_size_cap",
            lambda: total_input_bytes == EXPECTED_INPUT_BYTES and total_input_bytes <= INPUT_CAP,
            {"input_count": 42, "total_bytes": total_input_bytes, "cap_bytes": INPUT_CAP},
        )

        binding_path = CORRECTION_DIR / "solver-source-bindings.json"
        producer_checker_path = CORRECTION_DIR / "binding-checks.py"
        producer_receipt_path = CORRECTION_DIR / "check-receipt.json"
        producer_report_path = CORRECTION_DIR / "implementation-report.yaml"
        old_binding_path = ORIGINAL_DIR / "solver-source-bindings.json"
        original_receipt_path = ORIGINAL_DIR / "check-receipt.json"
        original_report_path = ORIGINAL_DIR / "implementation-report.yaml"
        binding_raw = (repo / binding_path).read_bytes()
        binding = strict_json_bytes(binding_raw)
        old_binding = jload(old_binding_path)
        correction_handoff = yload(CORRECTION_HANDOFF)["handoff"]
        original_handoff = yload(ORIGINAL_HANDOFF)["handoff"]
        original_receipt = jload(original_receipt_path)
        original_report = yload(original_report_path)["execution_report"]
        producer_receipt = jload(producer_receipt_path)
        producer_report = yload(producer_report_path)["execution_report"]
        old_review = yload(OLD_REVIEW)["validation_report"]
        original_archive = jload(ORIGINAL_ARCHIVE)
        review_archive = jload(REVIEW_ARCHIVE)
        failed_archive = jload(FAILED_ARCHIVE)
        correction_archive = jload(CORRECTION_ARCHIVE)
        failed_receipt = jload(FAILED_DIR / "check-receipt.json")
        failed_report = yload(FAILED_DIR / "implementation-report.yaml")["execution_report"]

        expected_top = {
            "schema", "task_id", "experiment_id", "approval_decision_id", "scope",
            "supersedes", "current_source", "dependency_bindings",
            "historical_scalar_baseline", "historical_inherited_assertions",
            "recorded_source_execution", "independent_review", "failed_predecessor",
            "correction_preflight", "scientific_runs", "measurement_admitted",
            "source_acceptance", "new_metadata_review",
        }
        current_paths = {str(ORIGINAL_DIR / name) for name in SOURCE_NAMES}
        expected_current = {
            str(ORIGINAL_DIR / name): sha_path(repo / ORIGINAL_DIR / name)
            for name in SOURCE_NAMES
        }
        old_fields = (
            "current_task_source_sha256",
            "source_binding_preflight",
            "validation_limitation",
            "execution_policy",
        )
        correction_frozen = {
            row["path"]: row["sha256"] for row in correction_handoff["source_bindings"]
        }
        original_frozen = {
            row["path"]: row["sha256"] for row in original_handoff["source_bindings"]
        }

        def validate_candidate(candidate: dict[str, Any]) -> None:
            need(set(candidate) == expected_top, "closed top-level schema")
            need(candidate["schema"] == "crypto.autoresearch.solver_source_bindings.v2", "schema")
            need(candidate["task_id"] == PRODUCER_TASK, "producer task")
            need(candidate["experiment_id"] == EXPERIMENT, "experiment")
            need(candidate["approval_decision_id"] == "DEC-20260909-b69851", "approval")
            need(candidate["scientific_runs"] == 0, "scientific runs")
            need(candidate["measurement_admitted"] is False, "measurement admission")
            need(candidate["source_acceptance"] is False, "source acceptance")
            need(candidate["new_metadata_review"] == "pending", "review status")
            supersedes = candidate["supersedes"]
            need(set(supersedes) == {"path", "sha256", "snapshot", "replacement_scope"}, "supersedes shape")
            need(supersedes["path"] == old_binding_path.as_posix(), "superseded path")
            need(supersedes["sha256"] == sha_path(repo / old_binding_path), "superseded hash")
            need(supersedes["snapshot"] == SOURCE_SNAPSHOT, "superseded snapshot")
            need("only" in supersedes["replacement_scope"].lower(), "replacement scope")
            current = candidate["current_source"]
            need(set(current) == {"source_task_id", "snapshot", "path_sha256", "coverage_note"}, "current source shape")
            need(current["source_task_id"] == "TASK-20260909-d31be5", "source task")
            need(current["snapshot"] == SOURCE_SNAPSHOT, "source snapshot")
            need(set(current["path_sha256"]) == current_paths, "current source path set")
            need(current["path_sha256"] == expected_current, "current source digest map")
            need(not ({"current_task_source_sha256", "task_source_sha256"} & set(candidate)), "competing current map")
            hist = candidate["historical_inherited_assertions"]
            need(hist["origin"] == {"path": old_binding_path.as_posix(), "sha256": sha_path(repo / old_binding_path)}, "historical origin")
            need("not authoritative" in hist["classification"], "historical classification")
            need(hist["values"] == {key: old_binding[key] for key in old_fields}, "historical values")
            need(candidate["historical_scalar_baseline"] == old_binding["source_baseline"], "historical baseline")
            deps = candidate["dependency_bindings"]
            need(deps["binding_origin"] == {"path": ORIGINAL_HANDOFF.as_posix(), "sha256": sha_path(repo / ORIGINAL_HANDOFF)}, "dependency origin")
            need(deps["files"] == old_binding["bound_files"], "dependency files")
            for path, metadata in deps["files"].items():
                need(original_frozen[path] == metadata["sha256"], f"dependency handoff hash {path}")
                need(sha_path(repo / path) == metadata["sha256"], f"dependency live hash {path}")
            execution = candidate["recorded_source_execution"]
            need(execution["task_id"] == "TASK-20260909-d31be5", "execution task")
            need(execution["receipt"] == {"path": original_receipt_path.as_posix(), "sha256": sha_path(repo / original_receipt_path)}, "execution receipt")
            need(execution["report"] == {"path": original_report_path.as_posix(), "sha256": sha_path(repo / original_report_path)}, "execution report")
            need(execution["authority_commit"] == "e5e63414a66b0f4305b564e29c67d352c60e72d9", "execution authority")
            need(execution["published_claim_commit"] == "0bfa7d28db0eb040558259925b596a0c4ebfcf5f", "execution claim")
            need(execution["archived_source_snapshot"] == SOURCE_SNAPSHOT, "execution snapshot")
            need(execution["prior_handoff_declared_inputs"] == len(original_handoff["inputs"]) == 62, "execution input count")
            need(execution["prior_reported_source_bindings_verified"] == original_report["source_bindings_verified"] == 62, "execution verified count")
            need(execution["checks"] == {"focused": 6, "complete_suite": 365, "total": 371, "passed": 371, "failed": 0}, "execution checks")
            need(execution["inference_as_recorded"] == original_receipt["inference"], "execution inference")
            need(execution["inference_as_recorded"]["resolved_model_id"] is None, "invented model")
            need(execution["inference_as_recorded"]["model_verified"] is False, "invented model verification")
            need(execution["hard_memory_guard_claim"] is False, "invented memory guard")
            prior_review = candidate["independent_review"]
            need(prior_review["path"] == OLD_REVIEW.as_posix(), "prior review path")
            need(prior_review["sha256"] == sha_path(repo / OLD_REVIEW), "prior review hash")
            need(prior_review["snapshot"] == "c83f873a4978e79fa4722d43135a2cbc13e82336", "prior review snapshot")
            need(prior_review["overall_verdict"] == old_review["verdict"] == "failed", "prior review verdict")
            need(prior_review["finding"] == "BINDING-CUSTODY-1", "prior review finding")
            failed = candidate["failed_predecessor"]
            need(failed == {"snapshot": "2e44076ebdadb9fac6bb21b9a12257e9d7a179cc", "first_per_case_receipt": "unavailable; not reconstructed", "state": "failed"}, "failed predecessor custody")
            preflight = candidate["correction_preflight"]
            need(preflight["handoff_path"] == CORRECTION_HANDOFF.as_posix(), "correction handoff path")
            need(preflight["handoff_sha256"] == sha_path(repo / CORRECTION_HANDOFF), "correction handoff hash")
            need(preflight["declared_input_count"] == len(correction_handoff["inputs"]) == 27, "correction declared count")
            need(preflight["verified_input_count"] == len(correction_frozen) == 27, "correction verified count")
            need(preflight["path_sha256"] == correction_frozen, "correction preflight map")
            need(preflight["authority_commit"] == "6bf6ff4ee43e085b4b50ed20e50f112880ac9974", "correction authority")
            need(preflight["published_claim_commit"] == "922c21a48c2df8dc3f9e3c57809f64fdebbed010", "correction claim")

        compare("canonical_v2_binding_consistency", lambda: (validate_candidate(binding) is None))
        compare(
            "old_binding_preserved_at_source_snapshot",
            lambda: git_bytes(SOURCE_SNAPSHOT, old_binding_path) == (repo / old_binding_path).read_bytes(),
        )
        compare(
            "single_current_source_map_and_exact_snapshot_bytes",
            lambda: all(
                binding["current_source"]["path_sha256"][str(ORIGINAL_DIR / name)]
                == original_receipt["source_sha256"][name]
                == sha_bytes(git_bytes(SOURCE_SNAPSHOT, ORIGINAL_DIR / name))
                == sha_path(repo / ORIGINAL_DIR / name)
                for name in SOURCE_NAMES
            ),
            binding["current_source"]["path_sha256"],
        )
        compare(
            "original_eight_file_archive_unchanged",
            lambda: all(
                sha_path(repo / path) == digest
                and sha_bytes(git_bytes(SOURCE_SNAPSHOT, Path(path))) == digest
                for path, digest in original_archive["source_path_sha256"].items()
            ) and len(original_archive["source_path_sha256"]) == 8,
        )
        compare(
            "baseline_solver_kernel_bytes_preserved",
            lambda: all(
                (repo / ORIGINAL_DIR / name).read_bytes()
                == (repo / BASELINE_DIR / name).read_bytes()
                == git_bytes(BASELINE_SNAPSHOT, BASELINE_DIR / name)
                for name in ("bsgs.py", "rho-corrected.py")
            ),
        )
        compare(
            "original_371_case_receipt_accounting",
            lambda: (
                original_receipt["accounting"] == {
                    "total_fixed_cases": 371, "passed": 371, "failed": 0,
                    "complete_suites": 1, "maximum_cases": 800, "remaining_cases": 429,
                }
                and original_receipt["smoke"]["inner"]["count"] == 6
                and len(original_receipt["smoke"]["inner"]["cases"]) == 6
                and all(row["passed"] is True for row in original_receipt["smoke"]["inner"]["cases"])
                and len(original_receipt["attempts"]) == 1
                and original_receipt["attempts"][0]["inner"]["worker"]["executed_case_count"] == 365
                and original_receipt["attempts"][0]["inner"]["worker"]["passed"] == 365
                and original_receipt["attempts"][0]["inner"]["worker"]["failed"] == 0
                and len(original_receipt["attempts"][0]["inner"]["worker"]["cases"]) == 365
                and all(row["status"] == "passed" for row in original_receipt["attempts"][0]["inner"]["worker"]["cases"])
                and [row["ordinal"] for row in original_receipt["attempts"][0]["inner"]["worker"]["cases"]] == list(range(1, 366))
                and original_report["checks"]["smoke"] == 6
                and original_report["checks"]["full_suite"] == 365
                and original_report["checks"]["total"] == original_report["checks"]["passed"] == 371
                and original_report["checks"]["failed"] == 0
            ),
        )
        compare(
            "original_outer_nested_custody_terminal",
            lambda: (
                original_receipt["smoke"]["outer"]["initial_tool_result"]["exit_code"] == 0
                and original_receipt["attempts"][0]["outer"]["initial_tool_result"]["session_id"] == 77407
                and original_receipt["attempts"][0]["outer"]["polls"][-1]["exit_code"] == 0
                and original_receipt["attempts"][0]["inner"]["exit_code"] == 0
                and original_receipt["attempts"][0]["inner"]["process_handling"]["terminal_observed"] is True
                and original_receipt["attempts"][0]["inner"]["process_handling"]["full_popen_handle_retained"] is True
                and original_receipt["attempts"][0]["inner"]["actual_telemetry"]["maximum_workers_used"] == 1
                and "asserts no hard guard enforcement" in original_receipt["attempts"][0]["inner"]["actual_telemetry"]["hard_limit_setup"]
            ),
        )
        compare(
            "failed_predecessor_history_preserved",
            lambda: (
                failed_archive["source_task_state"] == "failed"
                and failed_archive["failed_tasks_reclassified_completed"] is False
                and failed_receipt["execution_attempt_accounting"]["attempts"][0]["complete_case_records_retained"] is False
                and failed_receipt["execution_attempt_accounting"]["total_case_executions"] == 718
                and failed_report["fixed_suite"]["completion_gate_status"] == "NOT_MET"
                and binding["failed_predecessor"]["first_per_case_receipt"] == "unavailable; not reconstructed"
            ),
        )
        compare(
            "prior_independent_review_stays_failed",
            lambda: (
                old_review["verdict"] == "failed"
                and old_review["owned_joint_verdict"] == "breaks"
                and old_review["breaking_artifacts"][0]["id"] == "BINDING-CUSTODY-1"
                and git_bytes("c83f873a4978e79fa4722d43135a2cbc13e82336", OLD_REVIEW)
                == (repo / OLD_REVIEW).read_bytes()
                and review_archive["source_path_sha256"][OLD_REVIEW.as_posix()] == sha_path(repo / OLD_REVIEW)
            ),
        )
        compare(
            "producer_correction_snapshot_exact",
            lambda: (
                correction_archive["source_task_ids"] == [PRODUCER_TASK]
                and len(correction_archive["source_path_sha256"]) == 4
                and all(
                    sha_path(repo / path) == digest
                    and sha_bytes(git_bytes(CORRECTION_SNAPSHOT, Path(path))) == digest
                    for path, digest in correction_archive["source_path_sha256"].items()
                )
            ),
        )
        compare(
            "historical_current_and_review_counts_are_separate",
            lambda: (
                binding["historical_inherited_assertions"]["values"]["source_binding_preflight"]["handoff_declared_input_count"] == 49
                and binding["recorded_source_execution"]["prior_handoff_declared_inputs"] == 62
                and binding["correction_preflight"]["declared_input_count"] == 27
                and len(handoff["inputs"]) == 42
            ),
            {"historical_stale": 49, "original_execution": 62, "correction_preflight": 27, "review_preflight": 42},
        )
        compare(
            "authority_claim_snapshot_chains",
            lambda: all((
                is_ancestor("e5e63414a66b0f4305b564e29c67d352c60e72d9", "0bfa7d28db0eb040558259925b596a0c4ebfcf5f"),
                is_ancestor("0bfa7d28db0eb040558259925b596a0c4ebfcf5f", SOURCE_SNAPSHOT),
                is_ancestor("6bf6ff4ee43e085b4b50ed20e50f112880ac9974", "922c21a48c2df8dc3f9e3c57809f64fdebbed010"),
                is_ancestor("922c21a48c2df8dc3f9e3c57809f64fdebbed010", CORRECTION_SNAPSHOT),
                is_ancestor(SOURCE_SNAPSHOT, "758abfa92b4c3a37800fa5ce28e37f9df784c74c"),
                is_ancestor("758abfa92b4c3a37800fa5ce28e37f9df784c74c", "b20284d778917d619b175e1cc15139587fa79ae2"),
                is_ancestor("b20284d778917d619b175e1cc15139587fa79ae2", "c83f873a4978e79fa4722d43135a2cbc13e82336"),
                is_ancestor(CORRECTION_SNAPSHOT, AUTHORITY),
                is_ancestor(AUTHORITY, CLAIM),
            )),
        )
        correction_claim_path = Path(
            "coordination/experiment-reserve/BATCH-635652/claims/TASK-20260909-129bc2.1.claim.json"
        )
        original_claim_path = Path(
            "coordination/experiment-reserve/BATCH-635652/claims/TASK-20260909-d31be5.1.claim.json"
        )
        compare(
            "published_claims_bind_expected_worktree",
            lambda: all(
                strict_json_bytes(git_bytes(commit, path))["worktree"] == str(repo)
                and strict_json_bytes(git_bytes(commit, path))["task_id"] == task
                for commit, path, task in (
                    ("0bfa7d28db0eb040558259925b596a0c4ebfcf5f", original_claim_path, "TASK-20260909-d31be5"),
                    ("922c21a48c2df8dc3f9e3c57809f64fdebbed010", correction_claim_path, PRODUCER_TASK),
                    (CLAIM, CLAIM_PATH, TASK),
                )
            ),
        )
        compare(
            "producer_61_comparison_receipt_custody",
            lambda: (
                producer_receipt["administrative_checker_invocations"] == 1
                and producer_receipt["administrative_comparisons_in_recorded_checker"] == 61
                and producer_receipt["passed"] == 61
                and producer_receipt["failed"] == 0
                and len(producer_receipt["attempts"]) == 1
                and producer_receipt["attempts"][0]["reservation"]["attempt"] == 1
                and producer_receipt["attempts"][0]["reservation"]["checker_sha256"] == sha_path(repo / producer_checker_path)
                and sha_bytes(producer_receipt["attempts"][0]["checker_source"].encode("utf-8")) == sha_path(repo / producer_checker_path)
                and producer_receipt["attempts"][0]["inner"]["passed"] == 61
                and producer_receipt["attempts"][0]["inner"]["failed"] == 0
                and len(producer_receipt["attempts"][0]["inner"]["administrative_comparisons"]) == 61
                and all(row["status"] == "passed" for row in producer_receipt["attempts"][0]["inner"]["administrative_comparisons"])
                and producer_receipt["attempts"][0]["inner"]["solver_module_imports"] == 0
                and producer_receipt["attempts"][0]["outer_wrapper"]["exit_code"] == 0
                and producer_receipt["attempts"][0]["outer_wrapper"]["timed_out"] is False
                and producer_receipt["attempts"][0]["outer_tool_response"]["exit_code"] == 0
                and strict_json_bytes(producer_receipt["attempts"][0]["outer_tool_response"]["output"].encode("utf-8"))
                    == producer_receipt["attempts"][0]["outer_wrapper"]
                and producer_receipt["canonical_receipt_created_after_all_attempts"] is True
                and producer_receipt["no_further_checker_invocation_planned"] is True
            ),
        )
        compare(
            "producer_receipt_time_order_and_metrics",
            lambda: (
                parse_utc(producer_receipt["attempts"][0]["reservation"]["reserved_at_UTC"])
                <= parse_utc(producer_receipt["attempts"][0]["outer_wrapper"]["started_at_UTC"])
                <= parse_utc(producer_receipt["attempts"][0]["inner"]["started_at_UTC"])
                <= parse_utc(producer_receipt["attempts"][0]["inner"]["ended_at_UTC"])
                <= parse_utc(producer_receipt["attempts"][0]["outer_wrapper"]["ended_at_UTC"])
                and producer_receipt["attempts"][0]["outer_wrapper"]["children_peak_rss_bytes"] < RSS_CAP_BYTES
                and producer_receipt["attempts"][0]["inner"]["hard_memory_guard_claim"] is False
                and producer_receipt["attempts"][0]["outer_wrapper"]["hard_memory_guard_claim"] is False
            ),
        )
        compare(
            "producer_report_is_nonadmitting_and_hash_bound",
            lambda: (
                producer_report["task_id"] == PRODUCER_TASK
                and producer_report["administrative_checker_invocations"] == 1
                and producer_report["administrative_comparisons"] == producer_report["passed"] == 61
                and producer_report["failed"] == 0
                and producer_report["scientific_runs"] == 0
                and producer_report["solver_module_imports"] == 0
                and producer_report["source_acceptance"] is False
                and producer_report["measurement_admitted"] is False
                and producer_report["inference"]["resolved_model_id"] is None
                and producer_report["inference"]["model_verified"] is False
                and producer_report["receipt_sha256"] == sha_path(repo / producer_receipt_path)
                and producer_report["source_bindings"] == {
                    binding_path.as_posix(): sha_path(repo / binding_path),
                    producer_checker_path.as_posix(): sha_path(repo / producer_checker_path),
                }
            ),
        )
        compare(
            "correction_originals_unchanged_after_producer_checks",
            lambda: (
                producer_receipt["bound_originals_unchanged_after_checks"] == correction_frozen
                and all(sha_path(repo / path) == digest for path, digest in correction_frozen.items())
            ),
        )

        validate_candidate(binding)

        def changed(path: tuple[Any, ...], value: Any = None, *, delete: bool = False) -> dict[str, Any]:
            candidate = copy.deepcopy(binding)
            cursor: Any = candidate
            for key in path[:-1]:
                cursor = cursor[key]
            if delete:
                del cursor[path[-1]]
            else:
                cursor[path[-1]] = value
            return candidate

        zero64 = "0" * 64
        controls_spec: list[tuple[str, Callable[[], bytes]]] = [
            ("wrong_schema", lambda: json.dumps(changed(("schema",), "v1")).encode()),
            ("wrong_task", lambda: json.dumps(changed(("task_id",), TASK)).encode()),
            ("wrong_experiment", lambda: json.dumps(changed(("experiment_id",), "EXP-WRONG")).encode()),
            ("wrong_approval", lambda: json.dumps(changed(("approval_decision_id",), "DEC-20260909-adc75b")).encode()),
            ("promote_source_acceptance", lambda: json.dumps(changed(("source_acceptance",), True)).encode()),
            ("promote_measurement", lambda: json.dumps(changed(("measurement_admitted",), True)).encode()),
            ("invent_scientific_run", lambda: json.dumps(changed(("scientific_runs",), 1)).encode()),
            ("premature_review_pass", lambda: json.dumps(changed(("new_metadata_review",), "passed")).encode()),
            ("missing_supersedes", lambda: json.dumps(changed(("supersedes",), delete=True)).encode()),
            ("wrong_superseded_path", lambda: json.dumps(changed(("supersedes", "path"), "wrong.json")).encode()),
            ("wrong_superseded_hash", lambda: json.dumps(changed(("supersedes", "sha256"), zero64)).encode()),
            ("wrong_superseded_snapshot", lambda: json.dumps(changed(("supersedes", "snapshot"), CORRECTION_SNAPSHOT)).encode()),
            ("missing_historical_origin", lambda: json.dumps(changed(("historical_inherited_assertions", "origin"), delete=True)).encode()),
            ("wrong_historical_origin_hash", lambda: json.dumps(changed(("historical_inherited_assertions", "origin", "sha256"), zero64)).encode()),
            ("missing_current_table", lambda: json.dumps(changed(("current_source", "path_sha256", str(ORIGINAL_DIR / "table.py")), delete=True)).encode()),
            ("wrong_current_table_hash", lambda: json.dumps(changed(("current_source", "path_sha256", str(ORIGINAL_DIR / "table.py")), zero64)).encode()),
            ("extra_current_file", lambda: json.dumps(changed(("current_source", "path_sha256", "extra.py"), zero64)).encode()),
            ("wrong_current_snapshot", lambda: json.dumps(changed(("current_source", "snapshot"), CORRECTION_SNAPSHOT)).encode()),
            ("wrong_current_task", lambda: json.dumps(changed(("current_source", "source_task_id"), FAILED_DIR.name)).encode()),
            ("competing_current_task_map", lambda: json.dumps(changed(("current_task_source_sha256",), old_binding["current_task_source_sha256"])).encode()),
            ("competing_task_source_map", lambda: json.dumps(changed(("task_source_sha256",), old_binding["task_source_sha256"])).encode()),
            ("stale_49_as_review_count", lambda: json.dumps(changed(("correction_preflight", "declared_input_count"), 49)).encode()),
            ("original_62_as_correction_count", lambda: json.dumps(changed(("correction_preflight", "declared_input_count"), 62)).encode()),
            ("stale_49_as_original_count", lambda: json.dumps(changed(("recorded_source_execution", "prior_handoff_declared_inputs"), 49)).encode()),
            ("correction_27_as_original_count", lambda: json.dumps(changed(("recorded_source_execution", "prior_handoff_declared_inputs"), 27)).encode()),
            ("wrong_correction_verified_count", lambda: json.dumps(changed(("correction_preflight", "verified_input_count"), 62)).encode()),
            ("wrong_correction_authority", lambda: json.dumps(changed(("correction_preflight", "authority_commit"), AUTHORITY)).encode()),
            ("wrong_correction_claim", lambda: json.dumps(changed(("correction_preflight", "published_claim_commit"), CLAIM)).encode()),
            ("wrong_execution_snapshot", lambda: json.dumps(changed(("recorded_source_execution", "archived_source_snapshot"), CORRECTION_SNAPSHOT)).encode()),
            ("wrong_execution_receipt_hash", lambda: json.dumps(changed(("recorded_source_execution", "receipt", "sha256"), zero64)).encode()),
            ("wrong_execution_report_hash", lambda: json.dumps(changed(("recorded_source_execution", "report", "sha256"), zero64)).encode()),
            ("promote_failed_review", lambda: json.dumps(changed(("independent_review", "overall_verdict"), "passed")).encode()),
            ("remove_failed_review_finding", lambda: json.dumps(changed(("independent_review", "finding"), delete=True)).encode()),
            ("invent_resolved_model", lambda: json.dumps(changed(("recorded_source_execution", "inference_as_recorded", "resolved_model_id"), "gpt-5.6-sol")).encode()),
            ("invent_model_verified", lambda: json.dumps(changed(("recorded_source_execution", "inference_as_recorded", "model_verified"), True)).encode()),
            ("invent_hard_memory_guard", lambda: json.dumps(changed(("recorded_source_execution", "hard_memory_guard_claim"), True)).encode()),
            ("missing_failed_predecessor", lambda: json.dumps(changed(("failed_predecessor",), delete=True)).encode()),
            ("reconstructed_failed_receipt", lambda: json.dumps(changed(("failed_predecessor", "first_per_case_receipt"), "reconstructed.json")).encode()),
            ("wrong_dependency_hash", lambda: json.dumps(changed(("dependency_bindings", "files", "harness/rho.py", "sha256"), zero64)).encode()),
            ("duplicate_top_task_id", lambda: binding_raw.replace(b"{", b'{"task_id":"duplicate",', 1)),
            ("duplicate_current_snapshot", lambda: binding_raw.replace(b'"current_source": {', b'"current_source": {"snapshot":"duplicate",', 1)),
            ("duplicate_correction_count", lambda: binding_raw.replace(b'"correction_preflight": {', b'"correction_preflight": {"declared_input_count":49,', 1)),
        ]
        need(len(controls_spec) == EXPECTED_CONTROL_COUNT, "control count definition")
        for ordinal, (name, factory) in enumerate(controls_spec, start=1):
            control_start = time.monotonic()
            row: dict[str, Any] = {
                "ordinal": ordinal,
                "name": name,
                "started_at_UTC": utc_now(),
            }
            data: bytes | None = None
            candidate: Any = None
            try:
                data = factory()
                row["serialized_input_bytes"] = len(data)
                need(len(data) <= CONTROL_CAP, "serialized control exceeds 1 MiB")
                candidate = strict_json_bytes(data)
                validate_candidate(candidate)
                raise ValueError("malformed candidate was accepted")
            except BaseException as exc:
                if str(exc) == "malformed candidate was accepted":
                    row["status"] = "failed"
                    row["error"] = str(exc)
                else:
                    row["status"] = "passed"
                    row["rejection"] = f"{type(exc).__name__}: {str(exc)[:500]}"
            finally:
                elapsed = time.monotonic() - control_start
                row["ended_at_UTC"] = utc_now()
                row["wall_seconds"] = elapsed
                if elapsed > CONTROL_SECONDS:
                    row["status"] = "failed"
                    row["error"] = f"control exceeded {CONTROL_SECONDS}s"
                controls.append(row)
                del data
                del candidate

    except BaseException as exc:
        setup_error = f"{type(exc).__name__}: {str(exc)[:4000]}"
        comparisons.append({"name": "checker_setup", "status": "failed", "error": setup_error})

    ru_self = resource.getrusage(resource.RUSAGE_SELF)
    ru_children = resource.getrusage(resource.RUSAGE_CHILDREN)
    rss_unit = "bytes" if platform.system() == "Darwin" else "KiB"
    self_rss_bytes = normalized_rss_bytes(ru_self.ru_maxrss, rss_unit)
    child_rss_bytes = normalized_rss_bytes(ru_children.ru_maxrss, rss_unit)
    wall_seconds = time.monotonic() - wall_start
    self_cpu_seconds = time.process_time() - cpu_start
    children_cpu_seconds = ru_children.ru_utime + ru_children.ru_stime
    failed_comparisons = sum(row["status"] != "passed" for row in comparisons)
    failed_controls = sum(row["status"] != "passed" for row in controls)
    resource_ok = (
        max(self_rss_bytes, child_rss_bytes) <= RSS_CAP_BYTES
        and wall_seconds <= AGGREGATE_SECONDS
        and self_cpu_seconds + children_cpu_seconds <= AGGREGATE_SECONDS
    )
    if not resource_ok:
        failed_comparisons += 1

    receipt = {
        "schema": "crypto.autoresearch.binding_review_checks.v1",
        "task_id": TASK,
        "producer_task_id": PRODUCER_TASK,
        "argv": sys.argv,
        "repo": str(repo),
        "claim_commit": args.claim_commit,
        "started_at_UTC": started_at,
        "ended_at_UTC": utc_now(),
        "input_count": 42,
        "input_total_bytes": total_input_bytes,
        "input_cap_bytes": INPUT_CAP,
        "metadata_source_comparisons": comparisons,
        "metadata_source_comparison_count": len(comparisons),
        "metadata_source_comparisons_passed": len(comparisons) - failed_comparisons,
        "metadata_source_comparisons_failed": failed_comparisons,
        "malformed_control_count": len(controls),
        "malformed_controls": controls,
        "malformed_controls_passed": len(controls) - failed_controls,
        "malformed_controls_failed": failed_controls,
        "maximum_malformed_controls_all_attempts": 128,
        "maximum_controls_per_complete_suite": 48,
        "reserved_final_suite_capacity": 42,
        "per_control_seconds": CONTROL_SECONDS,
        "maximum_serialized_control_bytes": CONTROL_CAP,
        "scientific_runs": 0,
        "solver_module_imports": 0,
        "solver_executions": 0,
        "maximum_workers_used": 1,
        "watchdog_seconds_outer": 180,
        "wall_seconds": wall_seconds,
        "self_cpu_seconds": self_cpu_seconds,
        "children_cpu_seconds": children_cpu_seconds,
        "self_peak_rss_raw": ru_self.ru_maxrss,
        "children_peak_rss_raw": ru_children.ru_maxrss,
        "rss_units": rss_unit,
        "self_peak_rss_bytes": self_rss_bytes,
        "children_peak_rss_bytes": child_rss_bytes,
        "rss_cap_bytes": RSS_CAP_BYTES,
        "resource_bounds_held": resource_ok,
        "hard_memory_guard_claim": False,
        "rlimit_as_attempted": False,
        "setup_error": setup_error,
        "checker_sha256": sha_path(Path(__file__)),
        "receipt_self_hash": None,
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    summary = {
        "metadata_source_comparisons": len(comparisons),
        "metadata_source_comparisons_failed": failed_comparisons,
        "malformed_controls": len(controls),
        "malformed_controls_failed": failed_controls,
        "resource_bounds_held": resource_ok,
        "receipt": str(target),
    }
    print(json.dumps(summary, sort_keys=True))
    return 1 if failed_comparisons or failed_controls or not resource_ok else 0


if __name__ == "__main__":
    raise SystemExit(main())
