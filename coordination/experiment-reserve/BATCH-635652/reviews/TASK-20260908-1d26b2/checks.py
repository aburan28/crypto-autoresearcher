#!/usr/bin/env python3
"""Bounded zero-run contract checks for TASK-20260908-1d26b2.

The default mode evaluates 39 predetermined static, arithmetic, serialization,
and abstract-mock cases.  It never generates a curve, invokes a solver, builds
an experimental fixture, or executes a null/control/timing panel.  A PASS for
an ``expected_finding`` case means that the named definition problem was
reproduced; it is not a PASS verdict on the experiment contract.

``--verify-bindings`` is an administrative custody check.  It performs file
hash and Git byte comparisons and executes no numerical case.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import struct
import subprocess
import textwrap
import time
from pathlib import Path
from typing import Callable

import yaml


ROOT = Path(__file__).resolve().parents[5]
TASK_ID = "TASK-20260908-1d26b2"
AUTHORITY_COMMIT = "f8f1a99e5b7f50357a1bdc695e06a117122df65f"
SOURCE_SNAPSHOT = "cc43ef3c03100b0c34e2f552818ebd44262b7f63"
HANDOFF = ROOT / "ledger/handoffs/TASK-20260908-1d26b2.yaml"
CORRECTIONS = (
    ROOT
    / "coordination/experiment-reserve/BATCH-635652/corrections/TASK-20260908-395101"
)
EXPERIMENT_IDS = (
    "EXP-ECDLP-184fc4",
    "EXP-ECDLP-1e6502",
    "EXP-ECDLP-2c3d20",
    "EXP-ECDLP-709063",
)
ORIGINAL_2C = ROOT / "experiments/EXP-ECDLP-2c3d20/specification.yaml"
SNAPSHOT_PATHS = tuple(
    [
        f"coordination/experiment-reserve/BATCH-635652/corrections/"
        f"TASK-20260908-395101/{experiment_id}.yaml"
        for experiment_id in EXPERIMENT_IDS
    ]
    + [
        "coordination/experiment-reserve/BATCH-635652/corrections/"
        "TASK-20260908-395101/readiness.md",
        "coordination/experiment-reserve/BATCH-635652/archives/"
        "TASK-20260908-583bf9/snapshot.json",
    ]
)


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_mapping(
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
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
)


DOCS: dict[str, dict] = {}
TEXTS: dict[str, str] = {}
RESULTS: list[tuple[str, str, float, str]] = []


def load_yaml(path: Path) -> dict:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def case(name: str, kind: str, function: Callable[[], str]) -> None:
    started = time.perf_counter()
    detail = function()
    elapsed = time.perf_counter() - started
    if elapsed > 10.0:
        raise AssertionError(f"{name}: elapsed {elapsed:.6f}s exceeds 10 seconds")
    RESULTS.append((name, kind, elapsed, str(detail)))
    print(f"PASS {len(RESULTS):02d} {kind} {name} {elapsed:.6f}s {detail}")


def parse_contract(experiment_id: str) -> str:
    path = CORRECTIONS / f"{experiment_id}.yaml"
    text = path.read_text(encoding="utf-8")
    doc = yaml.load(text, Loader=UniqueKeyLoader)
    assert list(doc) == ["protocol_amendment"]
    TEXTS[experiment_id] = text
    DOCS[experiment_id] = doc
    return f"unique-key YAML parsed: {experiment_id}"


def contract(experiment_id: str) -> dict:
    return DOCS[experiment_id]["protocol_amendment"]


def prospective_flags(experiment_id: str) -> str:
    p = contract(experiment_id)
    assert p["experiment_id"] == experiment_id
    assert p["approved_by"] is None
    assert p["execution_authorized"] is False
    assert p["evidence_eligible"] is False
    assert p["scientific_runs"] == 0
    return f"prospective/unapproved/unauthorized/zero-run: {experiment_id}"


def check_184_counts() -> str:
    p = contract("EXP-ECDLP-184fc4")["effective_contract"]
    c = p["exact_cell_accounting"]
    assert 525 + 14 + 9 + 16 + 3 == p["frozen_library"]["member_count"] == 567
    assert 7 * 2 * 3 == c["primary_curve_bundles"] == 42
    assert 42 * 567 == c["observed_member_spectra"] == 23814
    assert 23814 * 64 == c["permutation_null_spectra"] == 1524096
    return "567 members, 42 bundles, 23814 observed, 1524096 null spectra"


def check_184_bootstrap_key_and_sharing() -> str:
    p = contract("EXP-ECDLP-184fc4")["effective_contract"]
    schedule = p["slope_definitions"]["bootstrap_rng_schedule"]
    key_a = (
        "EXP-ECDLP-184fc4|slope-bootstrap-v3|member=x_residue:m=2:j=0|"
        "stratum=A|replicate_pool=20260905,20260906,20260907|"
        "shared_outputs=full_ladder,terminal"
    )
    key_b = key_a.replace("member=x_residue:m=2:j=0", "member=x_residue:m=2:j=1")
    key_c = key_a.replace("stratum=A", "stratum=B")
    assert len({key_a, key_b, key_c}) == 3
    assert "canonical_member_id" in schedule["analysis_key"]
    assert "shared_outputs=full_ladder,terminal" in schedule["analysis_key"]
    assert "Different member or stratum keys never share streams" in schedule["sharing"]
    assert "Null trajectories are not bootstrapped" in schedule["sharing"]
    return "member/stratum streams separate; full/terminal triples intentionally shared"


def check_184_rejection_accept_boundary() -> str:
    modulus = 3
    limit = modulus * ((1 << 256) // modulus)
    value = limit - 1
    assert value < limit and value % modulus == 2
    return "V=R-1 accepted and maps to replicate-pool index 2"


def check_184_rejection_reject_boundary() -> str:
    modulus = 3
    limit = modulus * ((1 << 256) // modulus)
    value = limit
    assert value >= limit
    return "V=R rejected before modulo selection"


def check_184_undefined_ratio() -> str:
    null_median = 0.0
    ratio = None if null_median <= 0 else 9.0 / null_median
    assert ratio is None
    rule = contract("EXP-ECDLP-184fc4")["effective_contract"][
        "permutation_null_and_inference"
    ]["zero_dispersion_and_ratio_rules"]
    assert "strictly positive finite median" in rule
    return "nonpositive null median reaches typed null ratio branch"


def find_184_incomplete_hash_domains() -> str:
    p = contract("EXP-ECDLP-184fc4")["effective_contract"]
    generation = p["deterministic_curve_generation"]
    null_stream = p["permutation_null_and_inference"]["stream"]
    assert '"EXP-ECDLP-184fc4|primary|bits|stratum|replicate"' in generation[
        "primary_algorithm"
    ]
    assert "decimal(" not in generation["primary_algorithm"]
    assert '"EXP-ECDLP-184fc4|null|bits|stratum|replicate|r"' in null_stream
    assert "domain-separated certificate stream" in generation["certificates"]
    assert "certificate|" not in generation["certificates"]
    return (
        "expected_finding: cell placeholders lack canonical substitution and the "
        "certificate stream has no domain/counter schedule"
    )


def check_1e_counts() -> str:
    p = contract("EXP-ECDLP-1e6502")["effective_contract"]
    c = p["exact_cell_accounting"]
    assert 6 + 96 == c["precision_2_spectra_per_bundle"] == 102
    assert 8 + 128 == c["precision_3_spectra_per_bundle"] == 136
    assert 36 * (102 + 136) == c["observed_nonanomalous_spectra"] == 8568
    assert 8568 * 64 == c["permutation_null_spectra"] == 548352
    assert 24 * 20 == c["anomalous_scalar_instances_target"] == 480
    return "102/136 member sets, 8568 observed, 548352 null, 480 recoveries"


def check_1e_pair_domain() -> str:
    schedule = contract("EXP-ECDLP-1e6502")["effective_contract"][
        "blocking_pair_schedules"
    ]
    assert "including O, equality and inverse pairs" in schedule["domain"]
    assert "exactly n^2 pairs" in schedule["smallest_rung"]
    assert "Retain all duplicates and exact10000 rows" in schedule["larger_rungs"]
    return "full ordered-pair domain retains O/equal/inverse cases and duplicates"


def check_1e_pair_rejection_accept_boundary() -> str:
    modulus = 7
    limit = modulus * ((1 << 256) // modulus)
    value = limit - 1
    assert value < limit and 0 <= value % modulus < modulus
    return "n=7, V=M-1 accepted with in-range index"


def check_1e_pair_rejection_reject_boundary() -> str:
    modulus = 7
    limit = modulus * ((1 << 256) // modulus)
    value = limit
    assert value >= limit
    return "n=7, V=M rejected before index selection"


def check_1e_pair_sharing_and_refusal() -> str:
    p = contract("EXP-ECDLP-1e6502")["effective_contract"]
    schedule = p["blocking_pair_schedules"]
    sc5 = next(
        row for row in p["five_blocking_self_checks"] if row["id"] == "SC5_anomalous_recovery"
    )
    assert "SC1 and SC2 use the identical ordinary schedule" in schedule["sharing"]
    assert "Both precisions use the same group indices" in schedule["sharing"]
    assert "distinct anomalous-tag/kind schedule" in schedule["sharing"]
    assert "bits10,stratumA,replicate20260905" in sc5["exact_test"]
    assert "coverage_inconclusive" in sc5["exact_test"]
    return "ordinary sharing, anomalous separation, and fixed refusal fixture hold"


def find_1e_incomplete_hash_domains() -> str:
    p = contract("EXP-ECDLP-1e6502")["effective_contract"]
    generation = p["deterministic_curve_generation"]
    spectral = p["spectral_null_and_delta_thresholds"]
    # The source spells this mapping key as bare ``null:``, which YAML resolves
    # to the null scalar rather than to the string identifier "null".
    assert "null" not in spectral and None in spectral
    null_stream = spectral[None]
    assert '"EXP-ECDLP-1e6502|ordinary|bits|stratum|replicate"' in generation[
        "nonanomalous"
    ]
    assert '"EXP-ECDLP-1e6502|anomalous|bits|stratum|replicate"' in generation[
        "anomalous"
    ]
    assert "decimal(" not in generation["nonanomalous"]
    assert '"EXP-ECDLP-1e6502|null|bits|stratum|replicate|precision|r"' in null_stream
    assert "domain-separated indices" in generation["log_domain"]
    return (
        "expected_finding: ordinary/anomalous/null cell placeholders and log-"
        "certificate indices lack one canonical serialization schedule; the "
        "bare null mapping key parses as the null scalar"
    )


def check_2c_counts() -> str:
    c = contract("EXP-ECDLP-2c3d20")["exact_cell_accounting"]
    expected = {
        "primary_curve_bundles": 42,
        "primary_true_maps": 168,
        "primary_null_maps": 10752,
        "true_lumped_matrices": 6720,
        "null_lumped_matrices": 430080,
        "lumped_slope_trajectories_true": 960,
        "lumped_slope_trajectories_null": 61440,
    }
    assert all(type(c[key]) is int and c[key] == value for key, value in expected.items())
    return "seven declared map/matrix/slope totals are typed exact integers"


def check_2c_inventory() -> str:
    inventory = contract("EXP-ECDLP-2c3d20")["null_inference_and_decisions"][
        "statistic_inventory"
    ]
    eligible = {row["key"]: row["direction"] for row in inventory if row["candidate_eligible"]}
    assert len(inventory) == 16
    assert eligible == {
        "sigma_center": "upper",
        "A_point": "lower",
        "A_class_mean": "lower",
        "A_class_median": "lower",
        "A_min_size32": "lower",
        "class_spectrum_max": "upper",
    }
    return "16-key inventory and six eligible scalar directions are explicit"


def check_2c_zero_dispersion_ineligible() -> str:
    rule = contract("EXP-ECDLP-2c3d20")["itinerary_statistics"]["class_spectrum"]
    observed = 6.0
    null_value = 5.0
    sample_scale = 0.0
    eligible = sample_scale > 0.0
    assert observed != null_value and eligible is False
    assert "candidate eligibility are false" in rule
    assert "No categorical infinity" in rule
    return "separated zero-dispersion null remains numerically null and ineligible"


def check_2c_identity_anti_pooling() -> str:
    p = contract("EXP-ECDLP-2c3d20")["null_inference_and_decisions"]
    candidate = p["review_candidate"]
    identity = p["statistic_identity"]
    assert "BOTH bits22 and24" in candidate
    assert "BOTH strata" in candidate
    assert "SAME at-least-two" in candidate
    assert "literal word tuple w" in identity
    assert "no choice of replacement word/depth" in identity
    return "rung/stratum/replicate/r/depth/literal-word identity cannot be pooled"


def find_2c_slope_suppression() -> str:
    original_text = ORIGINAL_2C.read_text(encoding="utf-8")
    inventory = contract("EXP-ECDLP-2c3d20")["null_inference_and_decisions"][
        "statistic_inventory"
    ]
    rows = {row["key"]: row for row in inventory}
    assert "lambda_2(Q_g) per partition per cell, true and null, and its slope" in original_text
    assert "lambda_2 slope above -0.25 on the true walk with the null decaying" in original_text
    assert rows["sigma_center_slope"]["direction"] == "upper"
    assert rows["sigma_center_slope"]["candidate_eligible"] is False
    assert rows["itinerary_summary_slope"]["candidate_eligible"] is False
    return (
        "expected_finding: a primary original slope and explicit slope falsifier "
        "cannot trigger review under the successor inventory"
    )


def check_709_encodings() -> str:
    p = contract("EXP-ECDLP-709063")
    domains = p["portable_fixed_physical_table"]["representation_domains"]
    typed = p["stage_accounting_and_memory_conformance"]["typed_encodings"]
    assert struct.calcsize("<BII") == 9
    assert struct.calcsize("<IIII") == 16
    assert "logical_point,hash_preimage,physical_slot" in domains
    assert "O=(0,0,0)" in typed["point"]
    assert "state0empty,1affine,2O" in typed["baby_table_key"]
    assert "O=single0x00" in typed["hash_preimage"]
    return "logical 9-byte, hash-preimage, and physical 16-byte O domains separate"


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
    return "canonical JSON+LF and detached 64-hex+LF sidecar are total"


def scalar_ltr(k: int, base: int = 7, modulus: int = 101) -> tuple[int, int]:
    if k < 0:
        raise ValueError("nonnegative scalar required")
    if k == 0:
        return 0, 0
    result = base
    calls = 0
    for digit in bin(k)[3:]:
        result = (result + result) % modulus
        calls += 1
        if digit == "1":
            result = (result + base) % modulus
            calls += 1
    return result, calls


def check_scalar_case(k: int) -> str:
    result, calls = scalar_ltr(k)
    expected_calls = 0 if k == 0 else k.bit_length() - 1 + k.bit_count() - 1
    assert result == (k * 7) % 101
    assert calls == expected_calls
    return f"k={k}, result={result} in Z/101Z, charged calls={calls}"


def check_scalar_negative() -> str:
    try:
        scalar_ltr(-1)
    except ValueError as exc:
        assert str(exc) == "nonnegative scalar required"
        return "k=-1 raises the specified protocol-domain error"
    raise AssertionError("negative scalar unexpectedly accepted")


def check_709_replacement_ast() -> str:
    snippet = contract("EXP-ECDLP-709063")["rho_baseline"][
        "prospective_scalar_amendment"
    ]["replacement_python"]
    wrapped = "def outer():\n    total_ops = 0\n" + textwrap.indent(snippet, "    ")
    ast.parse(wrapped)
    assert "for digit in bin(k_val)[3:]" in snippet
    assert "if k_val < 0" in snippet and "if k_val == 0" in snippet
    return "supplied nested replacement parses and uses the declared leading-one loop"


def check_709_bsgs_formula() -> str:
    n, capacity, known_scalar = 101, 7, 37
    scalar_cost = lambda k: 0 if k == 0 else k.bit_length() - 1 + k.bit_count() - 1
    giant_index = known_scalar // capacity
    full = (capacity - 1) + scalar_cost(capacity) + giant_index + scalar_cost(known_scalar)
    q, r = divmod(n, capacity)
    giant_num = capacity * q * (q - 1) // 2 + q * r
    assert (giant_index, full) == (5, 22)
    assert giant_num == sum(k // capacity for k in range(2, n))
    return "N=101,E=7,k=37 gives ell=5 and fully charged BSGS value 22"


def classify_signs(values: tuple[int, int, int, int]) -> str:
    if all(value < 0 for value in values):
        return "ALL_TESTED_RUNGS_BSGS_LOWER"
    if all(value >= 0 for value in values):
        return "ALL_TESTED_RUNGS_BSGS_NOT_LOWER"
    changes = [i for i in range(3) if values[i] < 0 <= values[i + 1]]
    if len(changes) == 1 and all(v < 0 for v in values[: changes[0] + 1]) and all(
        v >= 0 for v in values[changes[0] + 1 :]
    ):
        return "TESTED_GRID_SIGN_CHANGE"
    return "NONMONOTONE_OR_INCONCLUSIVE"


def check_709_nonmonotonic_labels() -> str:
    signs = (-1, 1, -1, 1)
    assert classify_signs(signs) == "NONMONOTONE_OR_INCONCLUSIVE"
    rule = contract("EXP-ECDLP-709063")["metrics_and_decisions"]["measured_crossover"]
    assert "Reverse/multiple changes" in rule
    return "- + - + signs map only to NONMONOTONE_OR_INCONCLUSIVE"


def check_709_all_negative_label() -> str:
    signs = (-4, -3, -2, -1)
    assert classify_signs(signs) == "ALL_TESTED_RUNGS_BSGS_LOWER"
    rule = contract("EXP-ECDLP-709063")["metrics_and_decisions"]["measured_crossover"]
    assert "with no bound on an unmeasured crossover bit size" in rule
    return "all-negative signs state only BSGS-lower on the tested grid"


def find_709_stale_bound_claims() -> str:
    p = contract("EXP-ECDLP-709063")
    detailed = p["metrics_and_decisions"]
    artifacts = "\n".join(p["required_artifacts_for_future_execution"])
    assert "explicit directional bound" in p["objective"]
    assert "directional bound" in p["proof_search_map"]["method_ceiling"]
    assert "bracket/bound" in p["frontier"]["sota_delta"]
    assert "brackets/bounds" in artifacts
    assert "no bound on an unmeasured crossover bit size" in detailed["measured_crossover"]
    assert "lower/upper bound beyond the tested grid" in detailed["no_interpolation"]
    return (
        "expected_finding: headline/method/frontier/artifact prose still promises "
        "a bound that the executable tested-grid rule forbids"
    )


def check_709_rows_and_capacities() -> str:
    p = contract("EXP-ECDLP-709063")
    capacities = p["portable_fixed_physical_table"]["exact_capacities"]
    assert [(x["slots"], x["usable_entries"]) for x in capacities] == [
        (0, 0),
        (256, 179),
        (2048, 1433),
        (16384, 11468),
    ]
    c = p["exact_cell_accounting"]
    assert 16 + 256 + 48 + 48 == c["total_algorithm_rows"] == 368
    assert c["total_representation_control_records"] == 8
    return "capacities and 368 algorithm plus 8 representation-control rows hold"


def verify_bindings() -> None:
    handoff_bytes = HANDOFF.read_bytes()
    handoff = yaml.load(handoff_bytes, Loader=UniqueKeyLoader)["handoff"]
    failures: list[str] = []
    for binding in handoff["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            failures.append(f"missing:{binding['path']}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != binding["sha256"]:
            failures.append(f"hash:{binding['path']}")

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
        ["git", "show", f"{AUTHORITY_COMMIT}:ledger/handoffs/{TASK_ID}.yaml"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", AUTHORITY_COMMIT, "HEAD"],
        cwd=ROOT,
    ).returncode == 0
    assert not failures, failures
    assert not snapshot_failures, snapshot_failures
    assert authority_handoff == handoff_bytes
    assert ancestor
    print(
        "ADMIN "
        f"declared_hash_comparisons={len(handoff['source_bindings'])} "
        "declared_hash_failures=0 "
        f"snapshot_byte_comparisons={len(SNAPSHOT_PATHS)} "
        "snapshot_byte_failures=0 authority_handoff_byte_match=true "
        "authority_is_ancestor=true scientific_runs=0"
    )


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
    case("184_exact_counts", "arithmetic", check_184_counts)
    case("184_bootstrap_key_and_sharing", "static", check_184_bootstrap_key_and_sharing)
    case("184_rejection_accept_boundary", "arithmetic", check_184_rejection_accept_boundary)
    case("184_rejection_reject_boundary", "arithmetic", check_184_rejection_reject_boundary)
    case("184_undefined_ratio", "mock", check_184_undefined_ratio)
    case("184_incomplete_hash_domains", "expected_finding", find_184_incomplete_hash_domains)
    case("1e_exact_counts", "arithmetic", check_1e_counts)
    case("1e_complete_pair_domain", "static", check_1e_pair_domain)
    case("1e_pair_rejection_accept_boundary", "arithmetic", check_1e_pair_rejection_accept_boundary)
    case("1e_pair_rejection_reject_boundary", "arithmetic", check_1e_pair_rejection_reject_boundary)
    case("1e_pair_sharing_and_refusal", "static", check_1e_pair_sharing_and_refusal)
    case("1e_incomplete_hash_domains", "expected_finding", find_1e_incomplete_hash_domains)
    case("2c_exact_counts", "arithmetic", check_2c_counts)
    case("2c_statistic_inventory", "static", check_2c_inventory)
    case("2c_zero_dispersion_ineligible", "mock", check_2c_zero_dispersion_ineligible)
    case("2c_identity_anti_pooling", "static", check_2c_identity_anti_pooling)
    case("2c_original_slope_suppression", "expected_finding", find_2c_slope_suppression)
    case("709_representation_domains", "serialization", check_709_encodings)
    case("709_detached_manifest_digest", "serialization", check_709_detached_digest)
    case("709_scalar_negative", "mock", check_scalar_negative)
    case("709_scalar_k0", "mock", lambda: check_scalar_case(0))
    case("709_scalar_k1", "mock", lambda: check_scalar_case(1))
    case("709_scalar_k2", "mock", lambda: check_scalar_case(2))
    case("709_scalar_k13", "mock", lambda: check_scalar_case(13))
    case("709_scalar_k31", "mock", lambda: check_scalar_case(31))
    case("709_replacement_ast", "static", check_709_replacement_ast)
    case("709_bsgs_formula", "arithmetic", check_709_bsgs_formula)
    case("709_nonmonotonic_signs", "mock", check_709_nonmonotonic_labels)
    case("709_all_negative_signs", "mock", check_709_all_negative_label)
    case("709_stale_bound_claims", "expected_finding", find_709_stale_bound_claims)
    case("709_rows_and_capacities", "arithmetic", check_709_rows_and_capacities)
    assert len(RESULTS) == 39
    total = sum(row[2] for row in RESULTS)
    maximum = max(row[2] for row in RESULTS)
    print(
        "SUMMARY fixed_cases=39 failures=0 scientific_runs=0 "
        f"total_case_seconds={total:.6f} maximum_case_seconds={maximum:.6f}"
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
