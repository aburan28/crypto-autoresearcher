#!/usr/bin/env python3
"""Fixed zero-run definition checks for TASK-20260908-e4c260.

The default command runs a predetermined suite of static, arithmetic,
serialization, and abstract-index/mock cases.  It does not generate curves,
search fixtures or candidates, execute a solver, construct a scientific null
or control panel, invoke a future runner, or create a RUN record.

An ``expected_finding`` case passes when the named source inconsistency is
reproduced.  Such a pass is a check on this review, not a PASS verdict for the
experiment.  ``--verify-bindings`` is administrative: it hashes declared
inputs and compares exact Git bytes, and executes no numerical case.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import signal
import struct
import subprocess
import textwrap
import time
from fractions import Fraction
from pathlib import Path
from typing import Callable

import yaml


ROOT = Path(__file__).resolve().parents[5]
TASK_ID = "TASK-20260908-e4c260"
AUTHORITY_COMMIT = "4c9989fb423c37a5e3ccfb1daec7b25ddcd21aaf"
CLAIM_COMMIT = "9821978ea00383ee17a36fa090e4b68b45653437"
SOURCE_SNAPSHOT = "d550f353ee5b28bd49c0a2e26e8f26e5bb3461ae"
HANDOFF_REL = "ledger/handoffs/TASK-20260908-e4c260.yaml"
HANDOFF = ROOT / HANDOFF_REL
CORRECTIONS_REL = (
    "coordination/experiment-reserve/BATCH-635652/corrections/"
    "TASK-20260908-92d6dd"
)
CORRECTIONS = ROOT / CORRECTIONS_REL
EXPERIMENT_IDS = (
    "EXP-ECDLP-184fc4",
    "EXP-ECDLP-1e6502",
    "EXP-ECDLP-2c3d20",
    "EXP-ECDLP-709063",
)
ORIGINAL_2C = ROOT / "experiments/EXP-ECDLP-2c3d20/specification.yaml"
SNAPSHOT_PATHS = tuple(
    [f"{CORRECTIONS_REL}/{experiment_id}.yaml" for experiment_id in EXPERIMENT_IDS]
    + [
        f"{CORRECTIONS_REL}/checks.py",
        f"{CORRECTIONS_REL}/check-receipt.json",
        f"{CORRECTIONS_REL}/readiness.md",
        "coordination/experiment-reserve/BATCH-635652/archives/"
        "TASK-20260908-b1f673/snapshot.json",
    ]
)


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys, including duplicate scalar-null keys."""


def _construct_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict:
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)

DOCS: dict[str, dict] = {}
TEXTS: dict[str, str] = {}
RESULTS: list[dict] = []


def load_yaml(path: Path) -> dict:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def contract(experiment_id: str) -> dict:
    return DOCS[experiment_id]["protocol_amendment"]


def case(name: str, kind: str, function: Callable[[], str]) -> None:
    if len(RESULTS) >= 56:
        raise AssertionError("fixed case declaration exceeded 56")
    row = {"name": name, "kind": kind, "status": "started"}
    RESULTS.append(row)
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    signal.alarm(10)
    try:
        detail = function()
        row.update(status="passed", detail=str(detail))
    except BaseException as exc:  # preserve every failed attempt in stdout
        row.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    finally:
        signal.alarm(0)
        row.update(
            wall_seconds=time.perf_counter() - started_wall,
            cpu_seconds=time.process_time() - started_cpu,
        )
    print(
        f"{row['status'].upper()} {len(RESULTS):02d} {kind} {name} "
        f"{row['wall_seconds']:.6f}s "
        f"{row.get('detail', row.get('error', ''))}"
    )


def parse_contract(experiment_id: str) -> str:
    path = CORRECTIONS / f"{experiment_id}.yaml"
    text = path.read_text(encoding="utf-8")
    doc = yaml.load(text, Loader=UniqueKeyLoader)
    assert list(doc) == ["protocol_amendment"]
    TEXTS[experiment_id] = text
    DOCS[experiment_id] = doc
    return f"unique-key YAML parsed for {experiment_id}"


def prospective_flags(experiment_id: str) -> str:
    item = contract(experiment_id)
    assert item["experiment_id"] == experiment_id
    assert item["approved_by"] is None
    assert item["execution_authorized"] is False
    assert item["evidence_eligible"] is False
    assert item["scientific_runs"] == 0
    return "unapproved, unauthorized, evidence-ineligible, zero scientific runs"


def canonical_decimal(value: int) -> str:
    if type(value) is not int or value < 0:
        raise ValueError("canonical unsigned integer required")
    return str(value)


def cell_tag(exp: str, kind: str, bits: int, stratum: str, replicate: int) -> str:
    kinds = {
        "EXP-ECDLP-184fc4": {"primary", "control-2q"},
        "EXP-ECDLP-1e6502": {"ordinary", "anomalous"},
    }
    if exp not in kinds or kind not in kinds[exp] or stratum not in {"A", "B"}:
        raise ValueError("tag field outside frozen domain")
    return (
        f"{exp}|{kind}|bits={canonical_decimal(bits)}|stratum={stratum}"
        f"|replicate={canonical_decimal(replicate)}"
    )


def bounded_map(value: int, modulus: int) -> int | None:
    if not 1 <= modulus <= 2**256 or not 0 <= value < 2**256:
        raise ValueError("bounded-map domain")
    limit = modulus * (2**256 // modulus)
    return value % modulus if value < limit else None


def bounded_draw(
    modulus: int, prefix: str, digest: Callable[[int], int] | None = None
) -> tuple[int, int]:
    for counter in range(4096):
        value = (
            digest(counter)
            if digest is not None
            else int.from_bytes(
                hashlib.sha256(
                    f"{prefix}|counter={canonical_decimal(counter)}".encode()
                ).digest(),
                "big",
            )
        )
        mapped = bounded_map(value, modulus)
        if mapped is not None:
            return mapped, counter + 1
    raise ValueError("digest_rejection_exhausted")


def sparse_certificate(
    universe: int, chooser: Callable[[int, int], int]
) -> list[int]:
    if type(universe) is not int or not 1 <= universe <= 2**256:
        raise ValueError("certificate universe")
    sparse: dict[int, int] = {}
    emitted: list[int] = []
    for index in range(min(1000, universe)):
        offset = chooser(index, universe - index)
        if not 0 <= offset < universe - index:
            raise ValueError("certificate offset")
        position = index + offset
        emitted.append(sparse.get(position, position))
        sparse[position] = sparse.get(index, index)
        sparse.pop(index, None)
    return emitted


def ols_slope(xs: list[float], ys: list[float]) -> float:
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    return sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sum(
        (x - xbar) ** 2 for x in xs
    )


def slope_route(true_gamma: Fraction, null_gammas: list[Fraction]) -> bool:
    if len(null_gammas) != 64:
        return False
    mean = sum(null_gammas) / 64
    variance = sum((value - mean) ** 2 for value in null_gammas) / 63
    ordered = sorted(null_gammas)
    median = (ordered[31] + ordered[32]) / 2
    upper_rank_numerator = 1 + sum(value >= true_gamma for value in null_gammas)
    return (
        upper_rank_numerator == 1
        and variance > 0
        and true_gamma > Fraction(-1, 4)
        and median < 0
        and true_gamma - mean > 0
        and (true_gamma - mean) ** 2 >= 4 * variance
    )


def tested_grid_label(values: tuple[int | None, ...]) -> str:
    if len(values) != 4 or any(value is None for value in values):
        return "NONMONOTONE_OR_INCONCLUSIVE"
    signs = [value >= 0 for value in values]
    if not any(signs):
        return "ALL_TESTED_RUNGS_BSGS_LOWER"
    if all(signs):
        return "ALL_TESTED_RUNGS_BSGS_NOT_LOWER"
    first_nonnegative = signs.index(True)
    if all(signs[first_nonnegative:]):
        return f"TESTED_GRID_SIGN_CHANGE:{first_nonnegative - 1}:{first_nonnegative}"
    return "NONMONOTONE_OR_INCONCLUSIVE"


class MockAdditiveGroup:
    def __init__(self, modulus: int):
        self.modulus = modulus

    def add(self, left: int | None, right: int | None) -> int | None:
        if left is None:
            return right
        if right is None:
            return left
        return (left + right) % self.modulus


def independent_ltr(k: int, point: int, modulus: int = 101) -> tuple[int | None, int]:
    if k < 0:
        raise ValueError("nonnegative scalar required")
    if k == 0:
        return None, 0
    result = point
    calls = 0
    for digit in bin(k)[3:]:
        result = (result + result) % modulus
        calls += 1
        if digit == "1":
            result = (result + point) % modulus
            calls += 1
    return result, calls


def supplied_ltr(k: int, point: int) -> tuple[int | None, int]:
    snippet = contract("EXP-ECDLP-709063")["rho_baseline"][
        "prospective_scalar_amendment"
    ]["replacement_python"]
    wrapper = (
        "def invoke(E, Point, k_arg, point_arg):\n"
        "    total_ops = 0\n"
        + textwrap.indent(snippet, "    ")
        + "    answer = _count_mul(k_arg, point_arg)\n"
        + "    return answer, total_ops\n"
    )
    namespace: dict = {}
    exec(wrapper, namespace)
    return namespace["invoke"](MockAdditiveGroup(101), object, k, point)


def scalar_case(k: int) -> str:
    expected_result, expected_calls = independent_ltr(k, 7)
    actual_result, actual_calls = supplied_ltr(k, 7)
    formula_calls = 0 if k == 0 else k.bit_length() - 1 + k.bit_count() - 1
    assert (actual_result, actual_calls) == (expected_result, expected_calls)
    assert expected_calls == formula_calls
    expected_math = None if k == 0 else (7 * k) % 101
    assert expected_result == expected_math
    return f"k={k}, result={expected_result}, charged calls={expected_calls}"


def negative_scalar_case() -> str:
    for implementation in (independent_ltr, lambda k, p: supplied_ltr(k, p)):
        try:
            implementation(-1, 7)
        except ValueError as exc:
            assert str(exc) == "nonnegative scalar required"
        else:
            raise AssertionError("negative scalar was accepted")
    return "independent and supplied routines reject k=-1"


def run_cases() -> None:
    for experiment_id in EXPERIMENT_IDS:
        case(
            f"parse_{experiment_id}",
            "static",
            lambda experiment_id=experiment_id: parse_contract(experiment_id),
        )
    for experiment_id in EXPERIMENT_IDS:
        case(
            f"flags_{experiment_id}",
            "static",
            lambda experiment_id=experiment_id: prospective_flags(experiment_id),
        )

    def check_184_counts() -> str:
        effective = contract("EXP-ECDLP-184fc4")["effective_contract"]
        counts = effective["exact_cell_accounting"]
        assert 525 + 14 + 9 + 16 + 3 == effective["frozen_library"]["member_count"] == 567
        assert 7 * 2 * 3 == counts["primary_curve_bundles"] == 42
        assert 42 * 567 == counts["observed_member_spectra"] == 23814
        assert 23814 * 64 == counts["permutation_null_spectra"] == 1524096
        assert counts["control_curve_bundles"] == counts["run_artifacts"] == 42
        return "567 members; 42 primary/control bundles; exact observed/null totals"

    def check_184_actual_tags() -> str:
        primary = cell_tag("EXP-ECDLP-184fc4", "primary", 12, "A", 20260905)
        control = cell_tag("EXP-ECDLP-184fc4", "control-2q", 12, "A", 20260905)
        assert primary == "EXP-ECDLP-184fc4|primary|bits=12|stratum=A|replicate=20260905"
        assert len(
            {
                primary,
                control,
                cell_tag("EXP-ECDLP-184fc4", "primary", 14, "A", 20260905),
                cell_tag("EXP-ECDLP-184fc4", "primary", 12, "B", 20260905),
                cell_tag("EXP-ECDLP-184fc4", "primary", 12, "A", 20260906),
            }
        ) == 5
        return "kind, bit, stratum and replicate produce distinct actual-value bytes"

    def check_184_null_tags() -> str:
        base = "EXP-ECDLP-184fc4|null|bits=12|stratum=A|replicate=20260905|r="
        tags = [base + str(index) for index in range(64)]
        assert len(set(tags)) == 64
        assert tags[0].endswith("|r=0") and tags[-1].endswith("|r=63")
        source = contract("EXP-ECDLP-184fc4")["effective_contract"][
            "canonical_hash_schedules"
        ]["null_tag"]
        assert '"|r=" + dec(r)' in source
        return "64 actual r values are uniquely serialized in one cell"

    def check_rejection_boundaries() -> str:
        limit = 3 * (2**256 // 3)
        assert bounded_map(limit - 1, 3) == 2
        assert bounded_map(limit, 3) is None
        assert bounded_draw(1, "fixed", lambda _: 2**256 - 1) == (0, 1)
        assert bounded_draw(3, "fixed", lambda c: 2**256 - 1 if c == 0 else 4) == (1, 2)
        return "accept/reject edge, n=1 consumption and counter advance hold"

    def check_rejection_exhaustion() -> str:
        try:
            bounded_draw(3, "fixed", lambda _: 2**256 - 1)
        except ValueError as exc:
            assert str(exc) == "digest_rejection_exhausted"
        else:
            raise AssertionError("4096 rejected digests silently produced a draw")
        text = contract("EXP-ECDLP-184fc4")["effective_contract"][
            "canonical_hash_schedules"
        ]["certificate_check"]
        assert "preserve partial indices" in text and "do not shrink m" in text
        return "4096-cap exhaustion is total and cannot shrink certificate coverage"

    def check_sparse_certificate() -> str:
        three = sparse_certificate(3, lambda _i, remaining: remaining - 1)
        seven = sparse_certificate(7, lambda i, remaining: (2 * i + 1) % remaining)
        thousand = sparse_certificate(1001, lambda _i, _remaining: 0)
        assert three == [2, 0, 1]
        assert sorted(seven) == list(range(7))
        assert len(thousand) == len(set(thousand)) == 1000
        assert min(thousand) >= 0 and max(thousand) < 1001
        return "sparse partial Fisher-Yates emits exact distinct in-range samples"

    def check_184_bootstrap_sharing() -> str:
        schedule = contract("EXP-ECDLP-184fc4")["effective_contract"][
            "slope_definitions"
        ]["bootstrap_rng_schedule"]
        assert "canonical_member_id" in schedule["analysis_key"]
        assert "stratum=<A_or_B>" in schedule["analysis_key"]
        assert "shared_outputs=full_ladder,terminal" in schedule["analysis_key"]
        assert "Different member or stratum keys never share streams" in schedule["sharing"]
        assert "entire interval is null" in schedule["missing"]
        return "member/stratum separation, declared output sharing and missing branch hold"

    def check_184_zero_dispersion() -> str:
        rule = contract("EXP-ECDLP-184fc4")["effective_contract"][
            "permutation_null_and_inference"
        ]["zero_dispersion_and_ratio_rules"]
        observed, nulls = Fraction(2), [Fraction(1)] * 64
        median = (sorted(nulls)[31] + sorted(nulls)[32]) / 2
        rank = Fraction(1 + sum(value >= observed for value in nulls), 65)
        effect = None if len(set(nulls)) == 1 else observed - median
        assert rank == Fraction(1, 65) and effect is None
        assert "cannot satisfy a decision threshold" in rule
        assert "strictly positive finite median" in rule
        return "finite rank survives ties while zero-scale effect is null and ineligible"

    def find_fixed_schedule_rank_gap() -> str:
        # Abstract randomization group counterexample.  In each 66-element
        # orbit, identity plus the 64 fixed shifts 1..64 are used.  A uniform
        # base state satisfies the assignment-exchangeability premise, yet the
        # nominal minimum rank occurs at two states rather than at most 66/65.
        values = [66 - index for index in range(66)]
        numerators = [
            1
            + sum(
                values[(state + shift) % 66] >= values[state]
                for shift in range(1, 65)
            )
            for state in range(66)
        ]
        minimum_events = sum(value == 1 for value in numerators)
        assert minimum_events == 2
        assert Fraction(minimum_events, 66) > Fraction(1, 65)
        return "expected_finding: fixed transforms give Pr(rank=1/65)=1/33"

    def find_missing_sha_probability_model() -> str:
        text = TEXTS["EXP-ECDLP-184fc4"].lower()
        joint = contract("EXP-ECDLP-184fc4")["effective_contract"][
            "permutation_null_and_inference"
        ]["joint_null_required"]
        joint_lower = joint.lower()
        assert "joint assignment" in joint_lower and "uniform over all n! permutations" in joint_lower
        assert "sha-256 prf" not in text and "random-oracle" not in text and "random oracle" not in text
        return "expected_finding: assignment null is stated but fixed SHA sampler model is absent"

    case("184_exact_counts", "arithmetic", check_184_counts)
    case("184_actual_value_cell_tags", "serialization", check_184_actual_tags)
    case("184_actual_value_null_tags", "serialization", check_184_null_tags)
    case("184_unbiased_range_boundaries", "arithmetic", check_rejection_boundaries)
    case("184_digest_exhaustion_branch", "mock", check_rejection_exhaustion)
    case("184_sparse_certificate_distinctness", "abstract_index", check_sparse_certificate)
    case("184_bootstrap_sharing_and_missing", "static", check_184_bootstrap_sharing)
    case("184_zero_dispersion_and_ratio", "mock", check_184_zero_dispersion)
    case("184_fixed_schedule_rank_counterexample", "expected_finding", find_fixed_schedule_rank_gap)
    case("184_missing_sha_probability_model", "expected_finding", find_missing_sha_probability_model)

    def check_1e_counts() -> str:
        counts = contract("EXP-ECDLP-1e6502")["effective_contract"]["exact_cell_accounting"]
        assert counts["precision_2_spectra_per_bundle"] == 6 + 6 * 16 == 102
        assert counts["precision_3_spectra_per_bundle"] == 8 + 8 * 16 == 136
        assert counts["observed_nonanomalous_spectra"] == 36 * 238 == 8568
        assert counts["permutation_null_spectra"] == 8568 * 64 == 548352
        assert counts["anomalous_scalar_instances_target"] == 24 * 20 == 480
        return "102/136 precision sets; 8568 observed; 548352 null; 480 recoveries"

    def check_1e_tags_and_key() -> str:
        ordinary = cell_tag("EXP-ECDLP-1e6502", "ordinary", 10, "A", 20260905)
        anomalous = cell_tag("EXP-ECDLP-1e6502", "anomalous", 10, "A", 20260905)
        assert ordinary != anomalous
        spectral = contract("EXP-ECDLP-1e6502")["effective_contract"][
            "spectral_null_and_delta_thresholds"
        ]
        assert "permutation_null" in spectral and None not in spectral
        null_source = contract("EXP-ECDLP-1e6502")["effective_contract"][
            "canonical_hash_schedules"
        ]["null_tag"]
        assert '"|precision=" + dec(precision)' in null_source
        return "ordinary/anomalous tags separate and permutation_null is a stable string key"

    def check_1e_pair_domain() -> str:
        effective = contract("EXP-ECDLP-1e6502")["effective_contract"]
        schedule = effective["blocking_pair_schedules"]
        sc5 = next(
            item
            for item in effective["five_blocking_self_checks"]
            if item["id"] == "SC5_anomalous_recovery"
        )
        assert "including O, equality and inverse pairs" in schedule["domain"]
        assert "exactly n^2 pairs" in schedule["smallest_rung"]
        assert "Retain all duplicates and exact10000 rows" in schedule["larger_rungs"]
        assert "SC1 and SC2 use the identical ordinary schedule" in schedule["sharing"]
        assert "bits10,stratumA,replicate20260905" in sc5["exact_test"]
        assert "coverage_inconclusive" in sc5["exact_test"]
        return "full ordered pairs, sharing, duplicates and fixed refusal/missing branch hold"

    def check_1e_sibling_hash() -> str:
        binding = contract("EXP-ECDLP-1e6502")["effective_contract"][
            "spectral_null_and_delta_thresholds"
        ]["sibling_definition_binding"]
        sibling_path = ROOT / binding["path"]
        assert hashlib.sha256(sibling_path.read_bytes()).hexdigest() == binding["sha256"]
        sibling = load_yaml(sibling_path)["protocol_amendment"]
        for dotted in binding["fields"]:
            cursor = sibling
            for key in dotted.split("."):
                cursor = cursor[key]
        return "sibling path/hash and both named field paths resolve exactly"

    def find_1e_overbroad_sibling_binding() -> str:
        local = contract("EXP-ECDLP-1e6502")["effective_contract"]
        binding = local["spectral_null_and_delta_thresholds"]["sibling_definition_binding"]
        assert "effective_contract.permutation_null_and_inference" in binding["fields"]
        sibling = contract("EXP-ECDLP-184fc4")["effective_contract"][
            "permutation_null_and_inference"
        ]
        assert "all567member" in sibling["stream"]
        assert "42 cells" in sibling["joint_null_required"]
        assert "all 42 cells" in sibling["global_statistic"]
        assert local["exact_cell_accounting"]["nonanomalous_curve_bundles"] == 36
        assert local["exact_cell_accounting"]["precision_2_spectra_per_bundle"] == 102
        assert local["exact_cell_accounting"]["precision_3_spectra_per_bundle"] == 136
        local_null = local["canonical_hash_schedules"]["null_tag"]
        sibling_null = contract("EXP-ECDLP-184fc4")["effective_contract"][
            "canonical_hash_schedules"
        ]["null_tag"]
        assert "precision" in local_null and "precision" not in sibling_null
        return "expected_finding: whole sibling block conflicts with local 36-cell precision domains"

    case("1e_exact_counts", "arithmetic", check_1e_counts)
    case("1e_actual_tags_and_stable_yaml_key", "serialization", check_1e_tags_and_key)
    case("1e_pair_domain_sharing_refusal", "static", check_1e_pair_domain)
    case("1e_sibling_hash_and_field_resolution", "static", check_1e_sibling_hash)
    case("1e_overbroad_sibling_binding", "expected_finding", find_1e_overbroad_sibling_binding)

    def check_2c_counts() -> str:
        counts = contract("EXP-ECDLP-2c3d20")["exact_cell_accounting"]
        expected = {
            "primary_curve_bundles": 42,
            "primary_true_maps": 168,
            "primary_null_maps": 10752,
            "true_lumped_matrices": 6720,
            "null_lumped_matrices": 430080,
            "lumped_slope_trajectories_true": 960,
            "lumped_slope_trajectories_null": 61440,
        }
        assert all(type(counts[key]) is int and counts[key] == value for key, value in expected.items())
        return "all seven typed map/matrix/slope totals recompute"

    def check_2c_inventory() -> str:
        rows = contract("EXP-ECDLP-2c3d20")["null_inference_and_decisions"][
            "statistic_inventory"
        ]
        by_key = {row["key"]: row for row in rows}
        assert len(rows) == 16 and len(by_key) == 16
        assert by_key["sigma_center_slope"] == {
            "key": "sigma_center_slope",
            "scope": "seven_rung_partition_trajectory",
            "direction": "upper",
            "candidate_eligible": True,
        }
        assert by_key["itinerary_summary_slope"]["candidate_eligible"] is False
        return "16-key inventory restores only sigma_center_slope trajectory candidacy"

    def check_2c_original_counterexample_route() -> str:
        true_gamma = Fraction(0)
        null_gammas = [Fraction(-49, 100) - Fraction(2 * u, 6300) for u in range(64)]
        slope_eligible = slope_route(true_gamma, null_gammas)
        top_scalar_nulls = [Fraction(1)] * 64
        top_scalar_rank = 1 + sum(value >= Fraction(1) for value in top_scalar_nulls)
        top_scalar_scale = max(top_scalar_nulls) - min(top_scalar_nulls)
        scalar_eligible = top_scalar_rank == 1 and top_scalar_scale > 0
        assert slope_eligible and not scalar_eligible
        rule = contract("EXP-ECDLP-2c3d20")["null_inference_and_decisions"][
            "review_candidate"
        ]
        assert "EITHER" in rule and "does not inherit" in rule
        return "flat true/decaying null slope triggers while tied top-rung scalar route fails"

    def check_2c_slope_failure_branches() -> str:
        varying = [Fraction(-49, 100) - Fraction(2 * u, 6300) for u in range(64)]
        assert not slope_route(Fraction(-1, 4), varying)
        assert not slope_route(Fraction(0), [Fraction(-1, 2)] * 64)
        assert not slope_route(Fraction(1), [Fraction(u, 100) for u in range(64)])
        source = contract("EXP-ECDLP-2c3d20")["null_inference_and_decisions"][
            "slope_review_candidate"
        ]
        assert "allsevenfrozen bit rungs" in source["identity"]
        assert "SAME null index" in source["matched_null"]
        assert "allsevenrungs" in source["matched_null"]
        assert "BOTH strata" in source["replication"] and "SAME at leasttwo" in source["replication"]
        return "strict threshold, zero scale, nondecay, rung/index and replication gates hold"

    def find_2c_abscissa_mismatch() -> str:
        original = ORIGINAL_2C.read_text(encoding="utf-8")
        successor = contract("EXP-ECDLP-2c3d20")["slopes"]["definition"]
        assert "slope gamma against log p" in original
        assert "lambda_2 slope above -0.25" in original
        assert "x=ln(N)" in successor
        assert "ln(p)" not in successor and "log(p)" not in successor
        return "expected_finding: immutable question uses log(p), successor uses ln(N)"

    def find_2c_threshold_flip() -> str:
        bits = [12, 14, 16, 18, 20, 22, 24]
        p_values = [2**bit for bit in bits]
        # Fixed Hasse-compatible abstract orders at the positive boundary:
        # |N-(p+1)| = 2*sqrt(p)-1 <= 2*sqrt(p).  No curve is generated or
        # claimed to realize these pairs.
        n_values = [p + 2 * math.isqrt(p) for p in p_values]
        y_values = [-0.2499 * math.log(p) for p in p_values]
        gamma_p = ols_slope([math.log(p) for p in p_values], y_values)
        gamma_n = ols_slope([math.log(n) for n in n_values], y_values)
        assert gamma_p > -0.25 and gamma_n <= -0.25
        return f"expected_finding: same y gives gamma_p={gamma_p:.9f}, gamma_N={gamma_n:.9f}"

    def check_2c_descriptive_costs() -> str:
        inventory = contract("EXP-ECDLP-2c3d20")["null_inference_and_decisions"]
        descriptive = inventory["descriptive_field_inventory"]
        for key in (
            "uniform_rejection_draws",
            "label_evaluations_per_accepted_start",
            "localized_search_term",
            "fully_charged_modeled_search",
        ):
            row = next(item for item in inventory["statistic_inventory"] if item["key"] == key)
            assert row["candidate_eligible"] is False
        assert "payload/workspace/RSS/cost fields" in descriptive
        return "conditioning, localized-search and fully charged cost outputs stay descriptive"

    case("2c_exact_counts", "arithmetic", check_2c_counts)
    case("2c_statistic_inventory", "static", check_2c_inventory)
    case("2c_original_slope_route_independent", "abstract_index", check_2c_original_counterexample_route)
    case("2c_slope_failure_and_replication_branches", "abstract_index", check_2c_slope_failure_branches)
    case("2c_original_abscissa_mismatch", "expected_finding", find_2c_abscissa_mismatch)
    case("2c_logp_logn_threshold_flip", "expected_finding", find_2c_threshold_flip)
    case("2c_cost_and_itinerary_scope", "static", check_2c_descriptive_costs)

    def check_709_ast() -> str:
        snippet = contract("EXP-ECDLP-709063")["rho_baseline"][
            "prospective_scalar_amendment"
        ]["replacement_python"]
        ast.parse("def outer():\n    total_ops = 0\n" + textwrap.indent(snippet, "    "))
        assert "for digit in bin(k_val)[3:]" in snippet
        return "supplied replacement parses and skips the leading one"

    def check_709_encodings() -> str:
        amendment = contract("EXP-ECDLP-709063")
        typed = amendment["stage_accounting_and_memory_conformance"]["typed_encodings"]
        domains = amendment["portable_fixed_physical_table"]["representation_domains"]
        assert struct.calcsize("<BII") == 9 and struct.calcsize("<IIII") == 16
        assert "logical_point,hash_preimage,physical_slot" in domains
        assert "O=(0,0,0)" in typed["point"]
        assert "state0empty,1affine,2O" in typed["baby_table_key"]
        assert "O=single0x00" in typed["hash_preimage"]
        return "logical 9-byte, hash-preimage and physical 16-byte O domains separate"

    def check_709_detached_digest() -> str:
        payload = {"z": 2, "a": [True, None, "x"]}
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        sidecar = hashlib.sha256(encoded).hexdigest().encode("ascii") + b"\n"
        custody = contract("EXP-ECDLP-709063")["shared_instance_set"][
            "manifest_hash_custody"
        ]
        assert encoded == b'{"a":[true,null,"x"],"z":2}\n'
        assert len(sidecar) == 65 and sidecar[-1:] == b"\n"
        assert "separate shared-instance-manifest.sha256" in custody
        assert "sidecar contains no self-hash" in custody.lower()
        return "canonical JSON+LF has a detached 64-hex+LF digest"

    def check_709_capacities_and_counts() -> str:
        amendment = contract("EXP-ECDLP-709063")
        rows = amendment["portable_fixed_physical_table"]["exact_capacities"]
        assert [
            (row["budget_bytes"], row["slots"], row["usable_entries"])
            for row in rows
        ] == [(8, 0, 0), (4096, 256, 179), (32768, 2048, 1433), (262144, 16384, 11468)]
        counts = amendment["exact_cell_accounting"]
        assert counts["total_algorithm_rows"] == 16 + 256 + 48 + 48 == 368
        assert counts["total_representation_control_records"] == 8
        return "physical capacities, 368 algorithm rows and 8 controls recompute"

    def check_709_bsgs_actual_cost() -> str:
        order, capacity, scalar = 101, 7, 37
        scalar_cost = lambda k: 0 if k == 0 else k.bit_length() - 1 + k.bit_count() - 1
        giant_index = scalar // capacity
        full = (capacity - 1) + scalar_cost(capacity) + giant_index + scalar_cost(scalar)
        quotient, remainder = divmod(order, capacity)
        giant_sum = capacity * quotient * (quotient - 1) // 2 + quotient * remainder
        assert (giant_index, full) == (5, 22)
        assert giant_sum == sum(k // capacity for k in range(2, order))
        return "N=101,E=7,k=37 gives ell=5, B_full_actual=22 and exact giant sum"

    def check_709_grid_vocabulary() -> str:
        amendment = contract("EXP-ECDLP-709063")
        detailed = amendment["metrics_and_decisions"]
        artifacts = "\n".join(amendment["required_artifacts_for_future_execution"])
        assert "tested-rung sign-change pair" in amendment["objective"]
        assert "finite tested-grid calibration" in amendment["proof_search_map"]["method_ceiling"]
        assert "tested-grid classification" in amendment["frontier"]["sota_delta"]
        assert "tested-grid classification labels" in artifacts
        assert "No\n      crossover_bits_less_than,crossover_bits_greater_than" in TEXTS["EXP-ECDLP-709063"]
        return "objective, ceiling, frontier and artifact all use finite tested-grid vocabulary"

    case("709_scalar_negative", "mock", negative_scalar_case)
    case("709_scalar_k0", "mock", lambda: scalar_case(0))
    case("709_scalar_k1", "mock", lambda: scalar_case(1))
    case("709_scalar_k2", "mock", lambda: scalar_case(2))
    case("709_scalar_k13", "mock", lambda: scalar_case(13))
    case("709_scalar_k31", "mock", lambda: scalar_case(31))
    case("709_replacement_ast", "static", check_709_ast)
    case("709_representation_domains", "serialization", check_709_encodings)
    case("709_detached_manifest_digest", "serialization", check_709_detached_digest)
    case("709_capacities_and_counts", "arithmetic", check_709_capacities_and_counts)
    case("709_fully_charged_bsgs_formula", "arithmetic", check_709_bsgs_actual_cost)
    case(
        "709_all_negative_grid",
        "mock",
        lambda: (
            tested_grid_label((-4, -3, -2, -1))
            == "ALL_TESTED_RUNGS_BSGS_LOWER"
            or (_ for _ in ()).throw(AssertionError())
        ) and "all negative is tested-grid BSGS lower",
    )
    case(
        "709_all_nonnegative_grid",
        "mock",
        lambda: (
            tested_grid_label((0, 1, 2, 3))
            == "ALL_TESTED_RUNGS_BSGS_NOT_LOWER"
            or (_ for _ in ()).throw(AssertionError())
        ) and "all nonnegative is tested-grid BSGS not lower",
    )
    case(
        "709_adjacent_sign_pair",
        "mock",
        lambda: (
            tested_grid_label((-2, -1, 0, 1)) == "TESTED_GRID_SIGN_CHANGE:1:2"
            or (_ for _ in ()).throw(AssertionError())
        ) and "one monotone adjacent sign pair is identified",
    )
    case(
        "709_nonmonotonic_grid",
        "mock",
        lambda: (
            tested_grid_label((-1, 1, -1, 1)) == "NONMONOTONE_OR_INCONCLUSIVE"
            or (_ for _ in ()).throw(AssertionError())
        ) and "multiple reversals remain inconclusive",
    )
    case(
        "709_missing_grid",
        "mock",
        lambda: (
            tested_grid_label((-1, -1, None, 1)) == "NONMONOTONE_OR_INCONCLUSIVE"
            or (_ for _ in ()).throw(AssertionError())
        ) and "missing rung remains inconclusive",
    )
    case("709_grid_artifact_vocabulary", "static", check_709_grid_vocabulary)

    assert len(RESULTS) == 47, len(RESULTS)
    total = sum(row["wall_seconds"] for row in RESULTS)
    maximum = max(row["wall_seconds"] for row in RESULTS)
    failures = sum(row["status"] != "passed" for row in RESULTS)
    print(
        f"SUMMARY fixed_cases={len(RESULTS)} failures={failures} "
        f"scientific_runs=0 reruns=0 total_case_seconds={total:.6f} "
        f"maximum_case_seconds={maximum:.6f}"
    )
    if failures:
        raise SystemExit(1)


def verify_bindings() -> None:
    handoff_bytes = HANDOFF.read_bytes()
    handoff = yaml.load(handoff_bytes, Loader=UniqueKeyLoader)["handoff"]
    hash_failures: list[str] = []
    for binding in handoff["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            hash_failures.append(f"missing:{binding['path']}")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != binding["sha256"]:
            hash_failures.append(f"hash:{binding['path']}")

    snapshot_failures: list[str] = []
    for relative in SNAPSHOT_PATHS:
        committed = subprocess.run(
            ["git", "show", f"{SOURCE_SNAPSHOT}:{relative}"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        if committed != (ROOT / relative).read_bytes():
            snapshot_failures.append(relative)

    authority_handoff = subprocess.run(
        ["git", "show", f"{AUTHORITY_COMMIT}:{HANDOFF_REL}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    authority_ancestor = (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", AUTHORITY_COMMIT, "HEAD"],
            cwd=ROOT,
        ).returncode
        == 0
    )
    claim_parent = subprocess.run(
        ["git", "show", "-s", "--format=%P", CLAIM_COMMIT],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    assert not hash_failures, hash_failures
    assert not snapshot_failures, snapshot_failures
    assert authority_handoff == handoff_bytes
    assert authority_ancestor
    assert claim_parent == AUTHORITY_COMMIT
    print(
        "ADMIN "
        f"declared_hash_comparisons={len(handoff['source_bindings'])} "
        "declared_hash_failures=0 "
        f"snapshot_byte_comparisons={len(SNAPSHOT_PATHS)} "
        "snapshot_byte_failures=0 authority_handoff_byte_match=true "
        "authority_is_ancestor=true claim_parent_matches_authority=true "
        "scientific_runs=0"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-bindings", action="store_true")
    args = parser.parse_args()
    if args.verify_bindings:
        verify_bindings()
    else:
        run_cases()


if __name__ == "__main__":
    main()
