"""Independent fixed definition checks for TASK-20260908-1ef7aa.

This checker reads only handoff-declared repository sources and writes only its
declared receipt.  It performs no fixture generation, scientific runner call,
Sage/PARI invocation, timing panel, key/signature/nonce/lock operation, or RUN
allocation.  Every parameterized scope or component check is counted as its
own fixed case before execution.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import hashlib
import json
import resource
import signal
import time

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
TASK_ID = "TASK-20260908-1ef7aa"
HANDOFF_PATH = ROOT / "ledger/handoffs/TASK-20260908-1ef7aa.yaml"
SUCCESSOR_PATH = ROOT / (
    "coordination/experiment-reserve/BATCH-45b4d5/corrections/"
    "TASK-20260908-83e89d/EXP-ECDLP-1b1b99.yaml"
)
PREDECESSOR_PATH = ROOT / (
    "coordination/experiment-reserve/BATCH-45b4d5/corrections/"
    "TASK-20260907-fe3f53/EXP-ECDLP-1b1b99.yaml"
)
ORIGINAL_PATH = ROOT / "experiments/EXP-ECDLP-1b1b99/specification.yaml"
AMENDMENT_PATH = ROOT / (
    "experiments/EXP-ECDLP-1b1b99/amendments/DEC-20260908-166ad3.yaml"
)
RUNTIME_PATH = ROOT / (
    "coordination/experiment-reserve/BATCH-45b4d5/bindings/"
    "DEC-20260908-166ad3/runtime-binding.json"
)
PUBLIC_KEY_PATH = ROOT / (
    "coordination/experiment-reserve/BATCH-45b4d5/bindings/"
    "DEC-20260908-166ad3/launch-public.pem"
)
POLICIES_PATH = ROOT / "orchestration/model-policies.yaml"
BINDINGS_PATH = ROOT / "orchestration/model-bindings.yaml"
RECEIPT_PATH = HERE / "check-receipt.json"

MAX_CASES = 160
PER_CASE_SECONDS = 10
RESULTS: list[dict[str, object]] = []


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


HANDOFF = load_yaml(HANDOFF_PATH)["handoff"]
SUCCESSOR = load_yaml(SUCCESSOR_PATH)
PREDECESSOR = load_yaml(PREDECESSOR_PATH)
ORIGINAL = load_yaml(ORIGINAL_PATH)["experiment"]
AMENDMENT = load_yaml(AMENDMENT_PATH)["protocol_amendment"]
RUNTIME = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
POLICIES = load_yaml(POLICIES_PATH)
BINDINGS = load_yaml(BINDINGS_PATH)
E = SUCCESSOR["effective_contract"]
P = PREDECESSOR["effective_contract"]
C = E["cost_contract"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def med_exact(values):
    if len(values) not in (6, 7):
        raise ValueError("median cardinality")
    if any(v is None for v in values):
        raise ValueError("unresolved median")
    exact = [Fraction(v) for v in values]
    if any(v < 0 for v in exact):
        raise ValueError("negative median cost")
    exact.sort()
    if len(exact) == 7:
        return exact[3]
    return (exact[2] + exact[3]) / 2


def normalize(cost: int, repetitions: int) -> Fraction:
    if type(cost) is not int or cost < 0:
        raise ValueError("cost")
    if type(repetitions) is not int or not 1 <= repetitions <= 100:
        raise ValueError("repetitions")
    return Fraction(cost, repetitions)


def split_integer(cost: int, count: int) -> list[int]:
    if type(cost) is not int or cost < 0:
        raise ValueError("cost")
    if type(count) is not int or count < 1:
        raise ValueError("count")
    quotient, remainder = divmod(cost, count)
    return [quotient + int(index < remainder) for index in range(count)]


def score_endpoint(setup: int, blocks: list[tuple[int, int]]) -> Fraction:
    return Fraction(setup) + med_exact([normalize(c, n) for c, n in blocks])


def winner(scores: dict[int, Fraction]) -> int:
    if set(scores) != set(range(2, 8)):
        raise ValueError("candidate coverage")
    return min(scores, key=lambda arm: (scores[arm], arm))


def ratio_of_totals(scalar, transport) -> Fraction:
    if len(scalar) != 2 or len(transport) != 2:
        raise ValueError("endpoint coverage")
    if any(value is None or value < 0 for value in scalar + transport):
        raise ValueError("unresolved")
    denominator = sum(transport)
    if denominator <= 0:
        raise ValueError("denominator")
    return Fraction(sum(scalar), denominator)


def q_star(values: dict[int, Fraction | None]):
    for q in (1, 16, 256, 4096):
        value = values.get(q)
        if value is None:
            return "unresolved"
        if value >= 1:
            return q
    return "greater_than_4096"


def raw_shape_accepts(scope: str, indices: dict[str, object]) -> bool:
    variant = C["raw_cost_tensor"]["scope_variants"][scope]
    keys = set(indices)
    return (
        set(variant["required_indices"]) <= keys
        and not (set(variant["forbidden_indices"]) & keys)
    )


def case(name: str, check, classification: str = "hold") -> None:
    # Count before invoking the fixed object, including a failed assertion.
    if len(RESULTS) >= MAX_CASES:
        raise RuntimeError("fixed-case ceiling reached before invocation")
    row: dict[str, object] = {
        "ordinal": len(RESULTS) + 1,
        "name": name,
        "classification": classification,
        "status": "started",
    }
    RESULTS.append(row)
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    signal.alarm(PER_CASE_SECONDS)
    try:
        outcome = check()
        if outcome is not True:
            raise AssertionError(f"returned {outcome!r}")
        row["status"] = "passed"
    except BaseException as exc:  # retain each failed attempt truthfully
        row["status"] = "failed"
        row["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        signal.alarm(0)
        row["wall_seconds"] = time.perf_counter() - start_wall
        row["cpu_seconds"] = time.process_time() - start_cpu


def run() -> None:
    unchanged_sections = [
        "identity",
        "objective",
        "mechanism",
        "predictions",
        "test_boundary",
        "claims_prohibited",
        "input_selection",
        "kernel_and_class_model",
        "map_conventions",
        "query_generation",
        "rng",
        "evaluator_custody",
        "controls",
        "certificate_admission",
        "runner",
        "resource_and_cancellation",
        "artifact_custody",
        "overlap_and_pareto",
    ]
    for section in unchanged_sections:
        case(
            f"unchanged predecessor section: {section}",
            lambda section=section: E[section] == P[section],
        )

    case(
        "original six-fixture boundary retained",
        lambda: E["test_boundary"]["source_fixtures"] == 6,
    )
    case(
        "original two measurement seeds retained in timing matrix",
        lambda: E["timing_matrix"]["required_values"]["seed_values"]
        == ORIGINAL["replication"]["seeds"],
    )
    case(
        "original q ladder retained",
        lambda: E["test_boundary"]["q_values"] == [1, 16, 256, 4096],
    )
    case(
        "approved amendment binds successor predecessor hash",
        lambda: AMENDMENT["effective_contract"]["sha256"]
        == sha256(PREDECESSOR_PATH),
    )
    case(
        "runtime binding copied without file-list drift",
        lambda: E["arms"]["pinned_library_dependency"]["installed_file_bindings"]
        == RUNTIME["runtime"]["file_bindings"],
    )
    case(
        "runtime scalar callable retained",
        lambda: E["arms"]["pinned_library_dependency"]["definition"]["callable"]
        == RUNTIME["scalar_arm_7"]["callable"],
    )
    case(
        "public trust verification argv retained",
        lambda: E["authorization_and_lock"]["trust_root"]["verification_argv"]
        == RUNTIME["trust_root"]["verification_argv"],
    )
    case(
        "public key bytes match approved binding",
        lambda: sha256(PUBLIC_KEY_PATH)
        == E["authorization_and_lock"]["trust_root"]["public_key_sha256"],
    )
    case(
        "review policy requests xhigh independent session",
        lambda: POLICIES["policies"]["review-adversarial"]["reasoning_effort"]
        == "xhigh"
        and POLICIES["policies"]["review-adversarial"][
            "independent_session_required"
        ]
        is True,
    )
    case(
        "native openai review binding names gpt-5.6-sol",
        lambda: BINDINGS["bindings"]["openai"]["review-adversarial"]["model"]
        == "gpt-5.6-sol",
    )
    case(
        "handoff forbids fallback and degradation",
        lambda: HANDOFF["inference"]["fallback_allowed"] is False
        and HANDOFF["inference"]["degraded_allowed"] is False,
    )

    cardinalities = E["timing_matrix"]["cardinalities"]
    cardinality_checks = {
        "main endpoint-arm workloads": (
            6 * 4 * 3 * 2 * 4 * 7,
            cardinalities["endpoint_arm_workloads_before_blocks"],
        ),
        "main timing block rows": (
            6 * 4 * 3 * 2 * 4 * 7 * 7,
            cardinalities["required_main_timing_block_rows"],
        ),
        "selection endpoint-arm workloads": (
            9 * 8 * 6,
            cardinalities["baseline_selection_endpoint_arm_workloads"],
        ),
        "selection timing block rows": (
            9 * 8 * 6 * 7,
            cardinalities["baseline_selection_timing_block_rows"],
        ),
        "confirmation primary cells": (
            6 * 2 * 3,
            cardinalities["confirmation_class_coordinate_primary_cells_at_q4096"],
        ),
        "class-coordinate q cells": (
            6 * 2 * 3 * 4,
            cardinalities["class_coordinate_q_panel_cells"],
        ),
        "top control rows": (
            6 * 3 * 2 * 4 * 2 * 7,
            E["controls"]["level"]["top_curve"]["required_timing_block_rows"],
        ),
        "identity control rows": (
            6 * 3 * 2 * 4 * 2 * 7,
            E["controls"]["identity_transport"]["required_timing_block_rows"],
        ),
        "dual-composition assertions": (
            6 * 4 * 3 * (129 + 129),
            E["controls"]["composition"][
                "dual_composition_assertion_count_when_panel_complete"
            ],
        ),
    }
    for label, (expected, observed) in cardinality_checks.items():
        case(
            f"cardinality: {label}",
            lambda expected=expected, observed=observed: expected == observed,
        )

    case(
        "fixed scalar candidate set is arms 2 through 7",
        lambda: E["baseline_selection"]["candidates"] == list(range(2, 8)),
    )
    case(
        "nine interval-coordinate strata pool eight endpoints",
        lambda: E["baseline_selection"]["stratum"]["count"] == 9
        and E["baseline_selection"]["stratum"]["members_per_stratum"][
            "total_endpoints"
        ]
        == 8,
    )
    case(
        "success threshold is exact six fifths",
        lambda: Fraction(
            E["analysis_and_decision"]["success_gate"][
                "all_36_ratios_at_least_exact"
            ]["numerator"],
            E["analysis_and_decision"]["success_gate"][
                "all_36_ratios_at_least_exact"
            ]["denominator"],
        )
        == Fraction(6, 5),
    )
    case(
        "negative threshold is exact one",
        lambda: Fraction(
            E["analysis_and_decision"]["scoped_negative_gate"][
                "all_36_ratios_at_most_exact"
            ]["numerator"],
            E["analysis_and_decision"]["scoped_negative_gate"][
                "all_36_ratios_at_most_exact"
            ]["denominator"],
        )
        == 1,
    )

    case(
        "Med7 is fourth exact order statistic",
        lambda: med_exact([9, 1, 8, 2, 7, 3, 6]) == 6,
    )
    case(
        "Med6 is mean of central exact values",
        lambda: med_exact([1, 1, 1, 2, 2, 2]) == Fraction(3, 2),
    )
    case(
        "Med6 retains rational precision",
        lambda: med_exact([Fraction(1, 3)] * 3 + [Fraction(2, 3)] * 3)
        == Fraction(1, 2),
    )
    case(
        "normalized selection workload has no second q division",
        lambda: normalize(102_000_000, 34) == 3_000_000,
    )
    case(
        "normalized selector can reject adaptive-total misranking",
        lambda: 102_000_000 > 100_100_000
        and normalize(102_000_000, 34) < normalize(100_100_000, 1),
    )
    case(
        "exact rational tie chooses lowest arm",
        lambda: winner({arm: Fraction(7, 3) for arm in range(2, 8)}) == 2,
    )
    case(
        "near tie is not rounded",
        lambda: winner(
            {
                2: Fraction(10**20 + 1, 10**20),
                3: Fraction(1),
                4: Fraction(2),
                5: Fraction(3),
                6: Fraction(4),
                7: Fraction(5),
            }
        )
        == 3,
    )
    case(
        "ratio of endpoint totals differs from mean of endpoint ratios",
        lambda: ratio_of_totals([1, 9], [1, 3]) == Fraction(5, 2)
        and (Fraction(1, 1) + Fraction(9, 3)) / 2 == 2,
    )
    case(
        "zero transport denominator is unresolved",
        lambda: _raises(lambda: ratio_of_totals([1, 1], [0, 0])),
    )
    case(
        "integer remainder split conserves ten nanoseconds",
        lambda: split_integer(10, 3) == [4, 3, 3],
    )
    case(
        "global initialization split conserves 101 nanoseconds over 72 targets",
        lambda: sum(split_integer(101, 72)) == 101,
    )
    case(
        "shared view weights reconcile per view rather than globally",
        lambda: sum([Fraction(1, 12)] * 12) == 1
        and sum([Fraction(1, 12)] * 24) == 2,
    )
    case(
        "selection score differs from actual adaptive expenditure",
        lambda: score_endpoint(2, [(102_000_000, 34)] * 7) == 3_000_002
        and sum([102_000_000] * 7) != 3_000_000,
    )
    case(
        "common omission keeps setup fixed and uses Med6",
        lambda: Fraction(5) + med_exact([1, 1, 1, 2, 2, 2])
        == Fraction(13, 2),
    )
    case(
        "one unfavorable cell defeats favorable global summary",
        lambda: not all(value >= Fraction(6, 5) for value in [1] + [2] * 35),
    )
    case(
        "q-star can occur at first rung",
        lambda: q_star({1: Fraction(1), 16: 2, 256: 3, 4096: 4}) == 1,
    )
    case(
        "q-star can occur at q256 only after resolved lower ratios",
        lambda: q_star({1: Fraction(1, 2), 16: Fraction(3, 4), 256: 1, 4096: 2})
        == 256,
    )
    case(
        "q-star no crossing returns greater-than-4096",
        lambda: q_star({q: Fraction(1, 2) for q in (1, 16, 256, 4096)})
        == "greater_than_4096",
    )
    case(
        "q-star cannot skip unresolved earlier rung",
        lambda: q_star({1: None, 16: 2, 256: 2, 4096: 2}) == "unresolved",
    )
    case(
        "q-star no-crossing branch is unresolved if final rung is missing",
        lambda: q_star({1: Fraction(1, 2), 16: Fraction(1, 2), 256: Fraction(1, 2), 4096: None})
        == "unresolved",
    )

    expected_scopes = {
        "global": [],
        "interval": ["interval"],
        "fixture": ["fixture"],
        "kernel": ["fixture", "kernel"],
        "class": ["fixture", "class"],
        "endpoint_coordinate": ["fixture", "endpoint", "coordinate"],
        "selection_stratum": ["interval", "coordinate", "stratum"],
        "arm_workload": [
            "fixture",
            "endpoint",
            "coordinate",
            "plane",
            "seed",
            "q",
            "arm",
        ],
        "timing_block": [
            "fixture",
            "endpoint",
            "coordinate",
            "plane",
            "seed",
            "q",
            "arm",
            "block",
        ],
        "block_repetition": [
            "fixture",
            "endpoint",
            "coordinate",
            "plane",
            "seed",
            "q",
            "arm",
            "block",
            "repetition",
        ],
    }
    for scope, expected in expected_scopes.items():
        variant = C["raw_cost_tensor"]["scope_variants"][scope]
        case(
            f"typed scope indices: {scope}",
            lambda variant=variant, expected=expected: variant["required_indices"]
            == expected
            and not (set(expected) & set(variant["forbidden_indices"])),
        )

    expected_component_scopes = {
        "construct_supplied_public_source_curve": {"fixture"},
        "nonsingularity_check": {"fixture"},
        "read_public_N_and_r": {"fixture"},
        "read_prime_and_divisibility_certificates": {"fixture"},
        "read_m": {"fixture"},
        "discovery_all_candidates": {"interval"},
        "point_count_and_factor": {"interval"},
        "level_source_certificate": {"fixture"},
        "eigenvalue_and_sign_selection": {"fixture"},
        "kernel_search": {"kernel"},
        "map_construction": {"kernel"},
        "exact_dual_construction": {"kernel"},
        "class_multiplicity_certificate": {"class"},
        "within_pair_isomorphism": {"class"},
        "level_and_multiplicity_certificate": {"fixture", "class"},
        "coordinate_normalization": {"endpoint_coordinate"},
        "map_conjugation": {"endpoint_coordinate"},
        "global_transport_initialization": {"global"},
        "global_public_source_initialization": {"global"},
        "global_library_initialization": {"global"},
        "baseline_selection_stratum_overhead": {"selection_stratum"},
        "all_six_algorithm_selection_trials": {"selection_stratum"},
        "selected_algorithm_setup": {"arm_workload"},
        "library_internal_setup": {"arm_workload"},
        "table_setup": {"arm_workload"},
        "input_output_setup_conversion": {"arm_workload"},
        "transport_warmup": {"arm_workload"},
        "scalar_warmup": {"arm_workload"},
        "warmup_verification": {"arm_workload"},
        "psi_evaluation": {"block_repetition"},
        "iota_evaluation": {"block_repetition"},
        "phi_evaluation": {"block_repetition"},
        "scalar_multiplication": {"block_repetition"},
        "output_verification": {"block_repetition"},
        "every_per_point_table": {"block_repetition"},
        "library_input_conversion": {"block_repetition"},
        "library_output_conversion": {"block_repetition"},
        "library_scalar_conversion": {"block_repetition"},
        "query_serialization": {"block_repetition"},
        "query_generation": {"scaffolding"},
        "verifier_private_join": {"scaffolding"},
        "label_permutation_reaggregation": {"scaffolding"},
        "nonprimary_oracle_arm_measurements": {"scaffolding"},
        "top_level_control": {"scaffolding"},
        "identity_transport_control": {"scaffolding"},
        "reporting_and_artifact_publication": {"scaffolding"},
    }
    rows = C["component_crosswalk"]["rows"]
    by_component = {row["component"]: row for row in rows}
    case(
        "component registry and crosswalk have identical unique keysets",
        lambda: len(by_component) == len(rows)
        and set(by_component)
        == set(C["component_registry"]["canonical_components"])
        == set(expected_component_scopes),
    )
    for component, scopes in expected_component_scopes.items():
        case(
            f"component scope crosswalk: {component}",
            lambda component=component, scopes=scopes: set(
                by_component[component]["allowed_scopes"]
            )
            == scopes,
        )

    # Worked definition breaks: each check passes only when the named gap is
    # present in the frozen successor.  These are not implementation results.
    allocation = C["allocation_ledger"]
    case(
        "BREAK COST-SCENARIO-1: actual-only edge has no admissible scenario grammar",
        lambda: "actual_only_scaffolding" in allocation["strategy_views"]
        and isinstance(allocation["scenario"], str)
        and "fixed(q,seed)" in allocation["scenario"]
        and "actual_campaign" not in allocation["scenario"]
        and "scenario_variants" not in allocation,
        "break",
    )
    case(
        "BREAK COST-TARGET-2: allocation target has no closed serialized type",
        lambda: isinstance(allocation["target"], str)
        and "target_schema" not in allocation
        and "target_variants" not in allocation,
        "break",
    )
    case(
        "BREAK COST-PLANE-3: required plane index has no declared domain",
        lambda: "plane" in C["raw_cost_tensor"]["scope_variants"][
            "arm_workload"
        ]["required_indices"]
        and "plane_values" not in E["timing_matrix"]["required_values"]
        and "plane_domain" not in C["raw_cost_tensor"],
        "break",
    )
    case(
        "BREAK COST-PHASE-4: required phase has no closed type or component mapping",
        lambda: "phase" in C["raw_cost_tensor"]["common_required"]
        and "phase" not in C["raw_cost_tensor"]["common_types"]
        and all("allowed_phases" not in row for row in rows),
        "break",
    )
    case(
        "BREAK COST-STRATUM-5: redundant stratum index has no identity rule",
        lambda: E["baseline_selection"]["stratum"]["key"]
        == ["prime_interval_id", "coordinate_u"]
        and "stratum" in C["raw_cost_tensor"]["scope_variants"][
            "selection_stratum"
        ]["required_indices"]
        and "stratum_ids" not in E["baseline_selection"]["stratum"],
        "break",
    )
    case(
        "BREAK COST-ALIAS-6: two plane aliases both satisfy the structural row shape",
        lambda: raw_shape_accepts(
            "timing_block",
            {
                "fixture": "I0F0",
                "endpoint": "K0",
                "coordinate": 1,
                "plane": "main",
                "seed": 606103,
                "q": 4096,
                "arm": 1,
                "block": 0,
            },
        )
        and raw_shape_accepts(
            "timing_block",
            {
                "fixture": "I0F0",
                "endpoint": "K0",
                "coordinate": 1,
                "plane": "MAIN",
                "seed": 606103,
                "q": 4096,
                "arm": 1,
                "block": 0,
            },
        ),
        "break",
    )
    case(
        "BREAK MANIFEST-XREF-7: manifest section names conflict with governing minimum",
        lambda: set(E["artifact_custody"]["manifest_required_sections"])
        == {
            "run",
            "code",
            "inference",
            "environment",
            "input",
            "timing",
            "resource",
            "result",
            "artifact",
        }
        and {"inputs", "resources", "artifacts"}.isdisjoint(
            E["artifact_custody"]["manifest_required_sections"]
        ),
        "break",
    )
    case(
        "BREAK COST-UNAVAILABLE-8: unavailable RSS/count reasons lack named fields",
        lambda: "process_group_peak_RSS_unavailable_reason"
        not in C["raw_cost_tensor"]["common_required"]
        and "operation_counts_unavailable_reason"
        not in C["raw_cost_tensor"]["common_required"],
        "break",
    )


def _raises(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def administrative_source_verification():
    rows = []
    for binding in HANDOFF["source_bindings"]:
        path = ROOT / binding["path"]
        actual = sha256(path) if path.is_file() else "MISSING"
        rows.append(
            {
                "path": binding["path"],
                "expected_sha256": binding["sha256"],
                "actual_sha256": actual,
                "matches": actual == binding["sha256"],
            }
        )
    return rows


if __name__ == "__main__":
    overall_wall = time.perf_counter()
    overall_cpu = time.process_time()
    source_rows = administrative_source_verification()
    run()
    wall_seconds = time.perf_counter() - overall_wall
    cpu_seconds = time.process_time() - overall_cpu
    failed = sum(row["status"] != "passed" for row in RESULTS)
    receipt = {
        "schema": "crypto.autoresearch.validator_definition_checks.v1",
        "task_id": TASK_ID,
        "source_snapshot": "a081734c139ecd93a5b7442993b20f47bb7767de",
        "authority_commit": "458e1f891eb2936255366eef2ac67a5af5ed43cd",
        "published_claim_commit": "85cb3cd29b3b097764d3ab39a632c05bbefc84ea",
        "suite_invocations": 1,
        "actual_case_attempts_including_failures_and_reruns": len(RESULTS),
        "passed": len(RESULTS) - failed,
        "failed": failed,
        "failed_attempts": failed,
        "reruns": 0,
        "cases": RESULTS,
        "wall_seconds": wall_seconds,
        "cpu_seconds": cpu_seconds,
        "maximum_rss_native": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "rss_units": "bytes_on_Darwin",
        "workers": 1,
        "memory_limit_gib": 2,
        "per_case_seconds": PER_CASE_SECONDS,
        "aggregate_executed_check_wall_cpu_seconds_limit": 1800,
        "maximum_total_fixed_cases": MAX_CASES,
        "reserved_final_suite_used": True,
        "scientific_runs": 0,
        "scientific_fixture_searches": 0,
        "scientific_controls": 0,
        "scientific_timing_panels": 0,
        "sage_or_pari_invocations": 0,
        "real_keys_signatures_nonces_locks_or_run_ids": 0,
        "source_verification": source_rows,
        "source_binding_count": len(source_rows),
        "source_binding_matches": sum(row["matches"] for row in source_rows),
        "source_binding_mismatches": sum(not row["matches"] for row in source_rows),
        "contract_sha256": sha256(SUCCESSOR_PATH),
        "checker_sha256": sha256(Path(__file__)),
        "expected_break_ids": [
            "COST-SCENARIO-1",
            "COST-TARGET-2",
            "COST-PLANE-3",
            "COST-PHASE-4",
            "COST-STRATUM-5",
            "COST-ALIAS-6",
            "MANIFEST-XREF-7",
            "COST-UNAVAILABLE-8",
        ],
        "model_assignment": {
            "requested_policy": "review-adversarial",
            "resolved_model_id": "gpt-5.6-sol",
            "reasoning_effort": "xhigh",
            "independent_session": True,
            "fallback_used": False,
            "degraded": False,
            "bedrock_used": False,
            "model_probe_claimed": False,
        },
        "scope": (
            "Fixed arithmetic and static definition/source checks only; the "
            "eight BREAK cases detect missing or conflicting prospective "
            "definitions and are not implementation or scientific results."
        ),
    }
    RECEIPT_PATH.write_text(
        json.dumps(receipt, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    raise SystemExit(1 if failed or any(not row["matches"] for row in source_rows) else 0)
