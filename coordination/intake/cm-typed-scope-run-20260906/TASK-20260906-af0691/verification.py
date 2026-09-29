#!/usr/bin/env python3
"""Independent deterministic verifier for TASK-20260906-af0691.

This checker derives the finite predicates directly from the frozen fixtures.
It does not import or execute the producer's evaluate.py.  It also checks the
committed snapshot, receipt hashes, raw rows, certificates, controls, metrics,
environment, command, resource accounting, and declared completion witnesses.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


TASK_ID = "TASK-20260906-af0691"
EXPERIMENT_ID = "EXP-ENDO-c6c7a7"
RUN_ID = "RUN-ENDO-c6c7a7-single"
PRODUCER_TASK_ID = "TASK-20260906-f0e20a"
SNAPSHOT_TASK_ID = "TASK-20260906-7ab598"
SNAPSHOT_COMMIT = "12d9e2b328bfc6c4310db04e7ec48736afc29e31"
SNAPSHOT_PARENT = "d48709b077ee0fd371700921d4be66795747ac03"

BASE = Path("experiments/EXP-ENDO-c6c7a7")
RUN = BASE / "runs/RUN-ENDO-c6c7a7-single"
SPEC = BASE / "specification.yaml"
FIXTURES = BASE / "fixtures.json"
ORACLE = BASE / "oracle-key.json"
PRODUCER = BASE / "implementation/evaluate.py"
MANIFEST = RUN / "manifest.yaml"
COMMAND = RUN / "command.txt"
ENVIRONMENT = RUN / "environment.json"
STDOUT = RUN / "stdout.log"
STDERR = RUN / "stderr.log"
RAW = RUN / "raw-result.json"
METRICS = RUN / "metrics.json"
CERTIFICATES = RUN / "certificates.json"
EXECUTION_REPORT = RUN / "execution-report.yaml"
RESOURCE_USAGE = RUN / "resource-usage.json"
SNAPSHOT = Path(
    "coordination/intake/cm-typed-scope-run-20260906/archives/"
    "TASK-20260906-7ab598/snapshot.md"
)

RUN_ARTIFACTS = [
    MANIFEST,
    COMMAND,
    ENVIRONMENT,
    STDOUT,
    STDERR,
    RAW,
    METRICS,
    CERTIFICATES,
    EXECUTION_REPORT,
    RESOURCE_USAGE,
]
SNAPSHOT_PATHS = [SNAPSHOT, PRODUCER, *RUN_ARTIFACTS]

EXPECTED_LABELS = {
    "V1": "certified",
    "V2": "certified",
    "V3": "certified",
    "V4": "certified",
    "N1": "contradicted",
    "N2": "contradicted",
    "N3": "contradicted",
    "N4": "contradicted",
    "U1": "underdeclared",
    "U2": "underdeclared",
    "U3": "underdeclared",
    "U4": "underdeclared",
}
EXPECTED_COMMAND = (
    "/usr/bin/python3 experiments/EXP-ENDO-c6c7a7/implementation/evaluate.py "
    "--fixtures experiments/EXP-ENDO-c6c7a7/fixtures.json "
    "--oracle experiments/EXP-ENDO-c6c7a7/oracle-key.json "
    "--out-dir /workspace/experiments/EXP-ENDO-c6c7a7/runs/"
    "RUN-ENDO-c6c7a7-single --seed 0"
)
TRANSFER_LIMIT = (
    "Toy finite additive spaces F_2/F_5 of dimension at most 2. "
    "No elliptic curve, no cryptographic parameter, no transfer."
)


class Verification:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def check(
        self,
        category: str,
        name: str,
        holds: bool,
        *,
        expected: Any = None,
        observed: Any = None,
        detail: str | None = None,
    ) -> bool:
        row: dict[str, Any] = {
            "category": category,
            "name": name,
            "status": "pass" if holds else "fail",
        }
        if expected is not None or observed is not None:
            row["expected"] = expected
            row["observed"] = observed
        if detail is not None:
            row["detail"] = detail
        self.checks.append(row)
        return holds

    def warning(
        self,
        category: str,
        name: str,
        *,
        expected: Any = None,
        observed: Any = None,
        detail: str,
    ) -> None:
        self.checks.append(
            {
                "category": category,
                "name": name,
                "status": "warning",
                "expected": expected,
                "observed": observed,
                "detail": detail,
            }
        )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def as_points(rows: list[list[int]]) -> list[tuple[int, ...]]:
    return [tuple(int(v) for v in row) for row in rows]


def add(u: tuple[int, ...], v: tuple[int, ...], p: int) -> tuple[int, ...]:
    return tuple((a + b) % p for a, b in zip(u, v))


def scale(a: int, v: tuple[int, ...], p: int) -> tuple[int, ...]:
    return tuple((a * x) % p for x in v)


def affine(
    matrix: tuple[tuple[int, ...], ...],
    offset: tuple[int, ...],
    point: tuple[int, ...],
    p: int,
) -> tuple[int, ...]:
    return tuple(
        (sum(matrix[i][j] * point[j] for j in range(len(point))) + offset[i]) % p
        for i in range(len(point))
    )


def independent_completion(spec: dict[str, Any]) -> dict[str, Any]:
    p = int(spec["p"])
    dimension = int(spec["dimension"])
    matrix = tuple(tuple(int(v) % p for v in row) for row in spec["A"])
    offset = tuple(int(v) % p for v in spec["b"])
    if p not in (2, 5):
        raise ValueError(f"unsupported frozen field F_{p}")
    if len(matrix) != dimension or any(len(row) != dimension for row in matrix):
        raise ValueError("matrix shape differs from declared dimension")
    if len(offset) != dimension:
        raise ValueError("offset shape differs from declared dimension")

    domain_spec = spec["C"]
    if domain_spec["kind"] == "full":
        domain = list(itertools.product(range(p), repeat=dimension))
    elif domain_spec["kind"] == "line":
        generator = tuple(int(v) % p for v in domain_spec["generator"])
        if len(generator) != dimension or all(v == 0 for v in generator):
            raise ValueError("line generator must be a nonzero vector of declared dimension")
        domain = [scale(t, generator, p) for t in range(p)]
        if len(set(domain)) != p:
            raise ValueError("line completion does not enumerate p distinct points")
    else:
        raise ValueError(f"unsupported domain kind {domain_spec['kind']!r}")

    zero = (0,) * dimension
    image = [affine(matrix, offset, x, p) for x in domain]
    domain_set = set(domain)
    image_set = set(image)
    origin = affine(matrix, offset, zero, p) == zero
    additive_failures: list[dict[str, Any]] = []
    for x in domain:
        for y in domain:
            lhs = affine(matrix, offset, add(x, y, p), p)
            rhs = add(affine(matrix, offset, x, p), affine(matrix, offset, y, p), p)
            if lhs != rhs:
                additive_failures.append(
                    {
                        "x": list(x),
                        "y": list(y),
                        "f_x_plus_y": list(lhs),
                        "fx_plus_fy": list(rhs),
                    }
                )
    invariance_failures = [
        {"x": list(x), "f_x": list(y)}
        for x, y in zip(domain, image)
        if y not in domain_set
    ]
    candidates = [
        lam
        for lam in range(p)
        if all(affine(matrix, offset, x, p) == scale(lam, x, p) for x in domain)
    ]
    nonzero = [lam for lam in candidates if lam]
    invariant = not invariance_failures
    permutation = image_set == domain_set
    label = "certified" if invariant and nonzero else "contradicted"
    weaker: list[str] = []
    if origin:
        weaker.append("origin_preserving")
    if not additive_failures:
        weaker.append("additive")
    if invariant:
        weaker.append("invariant")
    if permutation:
        weaker.append("permutation_of_C")
    if 0 in candidates:
        weaker.append("zero_scalar")
    if nonzero:
        weaker.append("nonzero_scalar_restriction")

    return {
        "p": p,
        "dimension": dimension,
        "field": f"F_{p}",
        "domain_kind": domain_spec["kind"],
        "domain_points": [list(x) for x in domain],
        "image_points": [list(x) for x in image],
        "origin_preserving": origin,
        "additive": not additive_failures,
        "additive_failures": additive_failures,
        "invariant": invariant,
        "invariance_failures": invariance_failures,
        "scalar_candidates_including_zero": candidates,
        "nonzero_scalar_candidates": nonzero,
        "permutation": permutation,
        "weaker_true_properties": weaker,
        "label": label,
        "map_f": {"A": [list(row) for row in matrix], "b": list(offset)},
        "matrix": matrix,
        "offset": offset,
        "domain_tuples": domain,
    }


def validate_failure_witnesses(
    verifier: Verification,
    card_id: str,
    completion_index: int,
    derived: dict[str, Any],
    observed: dict[str, Any],
) -> list[str]:
    prefix = f"{card_id}.completion[{completion_index}]"
    issues: list[str] = []
    expected_keys: set[str] = set()
    if not derived["origin_preserving"]:
        expected_keys.add("origin")
    if not derived["additive"]:
        expected_keys.add("additivity")
    if not derived["invariant"]:
        expected_keys.add("invariance")
    if not derived["permutation"]:
        expected_keys.add("permutation")
    if not derived["nonzero_scalar_candidates"]:
        expected_keys.add("nonzero_scalar")
    actual_keys = set(observed)
    if not verifier.check(
        "witness",
        f"{prefix}.failure_witness_key_set",
        actual_keys == expected_keys,
        expected=sorted(expected_keys),
        observed=sorted(actual_keys),
    ):
        issues.append("failure witness key mismatch")

    p = derived["p"]
    matrix = derived["matrix"]
    offset = derived["offset"]
    domain = derived["domain_tuples"]
    zero = (0,) * derived["dimension"]
    if "origin" in observed:
        expected_f0 = list(affine(matrix, offset, zero, p))
        ok = observed["origin"] == {"f_0": expected_f0} and expected_f0 != list(zero)
        if not verifier.check(
            "witness", f"{prefix}.origin_witness", ok,
            expected={"f_0": expected_f0}, observed=observed["origin"],
        ):
            issues.append("invalid origin witness")

    if "additivity" in observed:
        row = observed["additivity"]
        try:
            x = tuple(row["x"])
            y = tuple(row["y"])
            lhs = affine(matrix, offset, add(x, y, p), p)
            rhs = add(affine(matrix, offset, x, p), affine(matrix, offset, y, p), p)
            ok = (
                x in set(domain)
                and y in set(domain)
                and lhs != rhs
                and row["f_x_plus_y"] == list(lhs)
                and row["fx_plus_fy"] == list(rhs)
            )
        except (KeyError, TypeError, ValueError):
            ok = False
        if not verifier.check("witness", f"{prefix}.additivity_witness", ok):
            issues.append("invalid additivity witness")

    if "invariance" in observed:
        ok = observed["invariance"] == derived["invariance_failures"]
        if not verifier.check(
            "witness", f"{prefix}.invariance_witnesses_complete", ok,
            expected=derived["invariance_failures"], observed=observed["invariance"],
        ):
            issues.append("invalid or incomplete invariance witness list")

    if "permutation" in observed:
        expected = {
            "image_size": len(set(map(tuple, derived["image_points"]))),
            "domain_size": len(set(map(tuple, derived["domain_points"]))),
            "invariant": derived["invariant"],
        }
        ok = observed["permutation"] == expected and not derived["permutation"]
        if not verifier.check(
            "witness", f"{prefix}.permutation_witness", ok,
            expected=expected, observed=observed["permutation"],
        ):
            issues.append("invalid permutation witness")

    if "nonzero_scalar" in observed:
        rows = observed["nonzero_scalar"]
        expected_lambdas = set(range(1, p))
        seen: set[int] = set()
        valid = isinstance(rows, list)
        if valid:
            for row in rows:
                try:
                    lam = int(row["lambda"])
                    x = tuple(row["x"])
                    fx = affine(matrix, offset, x, p)
                    lx = scale(lam, x, p)
                    valid = valid and (
                        lam in expected_lambdas
                        and lam not in seen
                        and x in set(domain)
                        and x != zero
                        and fx != lx
                        and row["f_x"] == list(fx)
                        and row["lambda_x"] == list(lx)
                    )
                    seen.add(lam)
                except (KeyError, TypeError, ValueError):
                    valid = False
        valid = valid and seen == expected_lambdas
        if not verifier.check(
            "witness", f"{prefix}.nonzero_scalar_witnesses_complete", valid,
            expected=sorted(expected_lambdas), observed=sorted(seen),
        ):
            issues.append("invalid or incomplete nonzero-scalar witnesses")
    return issues


def obligation_checks(derived: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, bool]]:
    d = derived
    return {
        "V1": {
            "restriction_scalar_is_2": d["V1"][0]["nonzero_scalar_candidates"] == [2],
            "inverse_scalar_3": (2 * 3) % 5 == 1,
            "permutation_of_C": d["V1"][0]["permutation"],
        },
        "V2": {
            "line_restriction_scalar_is_2": d["V2"][0]["nonzero_scalar_candidates"] == [2],
            "ambient_action_is_not_one_scalar": d["V2"][0]["matrix"] != ((2, 0), (0, 2)),
            "permutation_of_declared_line": d["V2"][0]["permutation"],
        },
        "V3": {
            "line_restriction_scalar_is_2": d["V3"][0]["nonzero_scalar_candidates"] == [2],
            "ambient_matrix_is_nondiagonal": d["V3"][0]["matrix"][0][1] != 0,
        },
        "V4": {
            "restriction_is_identity": d["V4"][0]["nonzero_scalar_candidates"] == [1],
            "ambient_kernel_witness_e2": affine(
                d["V4"][0]["matrix"], d["V4"][0]["offset"], (0, 1), 5
            ) == (0, 0),
            "kernel_witness_not_in_C": [0, 1] not in d["V4"][0]["domain_points"],
        },
        "N1": {
            "e1_maps_to_e2": affine(d["N1"][0]["matrix"], d["N1"][0]["offset"], (1, 0), 5)
            == (0, 1),
            "e2_outside_C": [0, 1] not in d["N1"][0]["domain_points"],
            "noninvariant": not d["N1"][0]["invariant"],
        },
        "N2": {
            "zero_scalar_is_exact": d["N2"][0]["scalar_candidates_including_zero"] == [0],
            "additive": d["N2"][0]["additive"],
            "nonzero_scalar_rejected": not d["N2"][0]["nonzero_scalar_candidates"],
            "not_permutation": not d["N2"][0]["permutation"],
        },
        "N3": {
            "f0_is_1": affine(d["N3"][0]["matrix"], d["N3"][0]["offset"], (0,), 5) == (1,),
            "not_origin_preserving": not d["N3"][0]["origin_preserving"],
            "not_scalar": not d["N3"][0]["scalar_candidates_including_zero"],
            "still_permutation": d["N3"][0]["permutation"],
        },
        "N4": {
            "e1_scalar_2": affine(d["N4"][0]["matrix"], d["N4"][0]["offset"], (1, 0), 5)
            == (2, 0),
            "e2_scalar_3": affine(d["N4"][0]["matrix"], d["N4"][0]["offset"], (0, 1), 5)
            == (0, 3),
            "no_whole_space_scalar": not d["N4"][0]["scalar_candidates_including_zero"],
            "whole_space_is_permuted": d["N4"][0]["permutation"],
        },
        "U1": {
            "first_line_certified": d["U1"][0]["label"] == "certified",
            "second_line_contradicted": d["U1"][1]["label"] == "contradicted",
            "same_ambient_map": d["U1"][0]["matrix"] == d["U1"][1]["matrix"],
        },
        "U2": {
            "nonzero_completion_certified": d["U2"][0]["label"] == "certified",
            "zero_completion_contradicted": d["U2"][1]["label"] == "contradicted",
            "zero_completion_is_additive": d["U2"][1]["additive"],
        },
        "U3": {
            "zero_offset_certified": d["U3"][0]["label"] == "certified",
            "nonzero_offset_contradicted": d["U3"][1]["label"] == "contradicted",
            "both_affine_maps_are_permutations": d["U3"][0]["permutation"] and d["U3"][1]["permutation"],
        },
        "U4": {
            "F2_completion_certified": d["U4"][0]["p"] == 2 and d["U4"][0]["label"] == "certified",
            "F5_completion_contradicted": d["U4"][1]["p"] == 5 and d["U4"][1]["label"] == "contradicted",
            "integer_3_changes_mod_characteristic": 3 % 2 == 1 and 3 % 5 == 3,
        },
    }


def verify(repo: Path) -> dict[str, Any]:
    v = Verification()
    required_inputs = [SPEC, FIXTURES, ORACLE, PRODUCER, *RUN_ARTIFACTS, SNAPSHOT]
    for path in required_inputs:
        v.check("artifact", f"exists:{path}", (repo / path).is_file())
    if not all((repo / path).is_file() for path in required_inputs):
        return finalize(v, {}, {}, {}, {}, [], ["One or more required inputs are missing."])

    specification = load_yaml(repo / SPEC)["experiment"]
    fixtures = load_json(repo / FIXTURES)
    oracle = load_json(repo / ORACLE)
    manifest = load_yaml(repo / MANIFEST)["run"]
    environment = load_json(repo / ENVIRONMENT)
    raw = load_json(repo / RAW)
    metrics = load_json(repo / METRICS)
    certificates_document = load_json(repo / CERTIFICATES)
    execution_report = load_yaml(repo / EXECUTION_REPORT)["execution_report"]
    resources = load_json(repo / RESOURCE_USAGE)

    # Snapshot/Git custody.
    expected_paths = sorted(str(path) for path in SNAPSHOT_PATHS)
    cat = git(repo, "cat-file", "-e", f"{SNAPSHOT_COMMIT}^{{commit}}", check=False)
    v.check("custody", "snapshot_commit_exists", cat.returncode == 0, observed=SNAPSHOT_COMMIT)
    ancestor = git(repo, "merge-base", "--is-ancestor", SNAPSHOT_COMMIT, "HEAD", check=False)
    v.check("custody", "snapshot_commit_reachable_from_HEAD", ancestor.returncode == 0)
    parent = git(repo, "rev-parse", f"{SNAPSHOT_COMMIT}^").stdout.decode().strip()
    v.check(
        "custody", "snapshot_parent", parent == SNAPSHOT_PARENT,
        expected=SNAPSHOT_PARENT, observed=parent,
    )
    changed = sorted(
        line for line in git(
            repo, "diff-tree", "--no-commit-id", "--name-only", "-r", SNAPSHOT_COMMIT
        ).stdout.decode().splitlines() if line
    )
    v.check(
        "custody", "snapshot_exact_path_set", changed == expected_paths,
        expected=expected_paths, observed=changed,
    )
    current_tree_mismatches: list[str] = []
    for relative in SNAPSHOT_PATHS:
        committed = git(repo, "show", f"{SNAPSHOT_COMMIT}:{relative}").stdout
        current = (repo / relative).read_bytes()
        same = committed == current
        v.check(
            "custody", f"snapshot_bytes_current:{relative}", same,
            expected=sha256_bytes(committed), observed=sha256_bytes(current),
        )
        if not same:
            current_tree_mismatches.append(str(relative))

    # Manifest source and artifact hash bindings.
    manifest_source_hashes = manifest["code"]["source_sha256"]
    for relative in [PRODUCER, SPEC, FIXTURES, ORACLE]:
        observed_hash = sha256(repo / relative)
        expected_hash = manifest_source_hashes.get(str(relative))
        v.check(
            "hash", f"manifest_source_sha256:{relative}", observed_hash == expected_hash,
            expected=expected_hash, observed=observed_hash,
        )
    manifest_artifact_hashes = manifest["artifacts"]["sha256"]
    for relative in RUN_ARTIFACTS:
        if relative == MANIFEST:
            continue
        expected_hash = manifest_artifact_hashes.get(relative.name)
        observed_hash = sha256(repo / relative)
        v.check(
            "hash", f"manifest_artifact_sha256:{relative.name}", observed_hash == expected_hash,
            expected=expected_hash, observed=observed_hash,
        )

    v.check("manifest", "run_id", manifest["id"] == RUN_ID, expected=RUN_ID, observed=manifest["id"])
    v.check(
        "manifest", "experiment_id", manifest["experiment_id"] == EXPERIMENT_ID,
        expected=EXPERIMENT_ID, observed=manifest["experiment_id"],
    )
    v.check(
        "manifest", "producer_task_id", manifest["task_id"] == PRODUCER_TASK_ID,
        expected=PRODUCER_TASK_ID, observed=manifest["task_id"],
    )
    v.check("manifest", "status", manifest["status"] == "completed_valid", observed=manifest["status"])
    v.check(
        "manifest", "implementation_commit_is_snapshot_parent",
        manifest["code"]["commit"] == SNAPSHOT_PARENT,
        expected=SNAPSHOT_PARENT, observed=manifest["code"]["commit"],
    )
    command_text = (repo / COMMAND).read_text(encoding="utf-8").rstrip("\n")
    v.check(
        "manifest", "command_artifact_exact", command_text == EXPECTED_COMMAND,
        expected=EXPECTED_COMMAND, observed=command_text,
    )
    v.check(
        "manifest", "manifest_command_matches_artifact",
        manifest["code"]["command"] == command_text,
        expected=command_text, observed=manifest["code"]["command"],
    )
    v.check("manifest", "seed_is_zero", manifest["inputs"]["seed"] == 0, observed=manifest["inputs"]["seed"])
    v.check("manifest", "raw_seed_is_zero", raw["seed"] == 0, observed=raw["seed"])
    v.check("manifest", "metrics_seed_is_zero", metrics["seed"] == 0, observed=metrics["seed"])
    expected_environment = {
        "operating_system": manifest["environment"]["operating_system"],
        "architecture": manifest["environment"]["architecture"],
        "python_version": manifest["environment"]["python_version"],
        "python_implementation": manifest["environment"]["python_implementation"],
        "sage_version": manifest["environment"]["sage_version"],
        "dependencies": manifest["environment"]["dependencies"],
        "hostname": manifest["environment"]["hostname"],
        "cpu_count": manifest["environment"]["cpu_count"],
    }
    v.check(
        "manifest", "environment_artifact_matches_manifest",
        environment == expected_environment, expected=expected_environment, observed=environment,
    )
    inference = manifest["inference"]
    inference_expected = {
        "requested_policy": "executor-implementation",
        "canonical_policy": "executor-implementation",
        "backend": None,
        "provider": None,
        "resolved_model_id": None,
        "model_provenance": "not-applicable",
        "model_verified": True,
        "requested_reasoning_effort": None,
        "reasoning_effort": None,
        "fallback_used": False,
        "fallback_reason": None,
        "degraded_requirements": [],
        "independent_session": False,
        "adapter_version": "1.1.0",
        "config_digest": None,
    }
    inference_core = {key: inference.get(key) for key in inference_expected}
    v.check(
        "manifest", "deterministic_inference_block", inference_core == inference_expected,
        expected=inference_expected, observed=inference_core,
        detail="model_verified=true denotes the repository deterministic_block sentinel; no model id exists to probe",
    )
    v.check(
        "manifest", "deterministic_inference_note",
        "No model" in inference.get("note", "") and "exact finite predicates" in inference.get("note", ""),
        observed=inference.get("note"),
    )

    # Independent finite derivation from fixtures, without using producer code.
    cards = fixtures["cards"]
    card_ids = [card["id"] for card in cards]
    v.check(
        "coverage", "fixture_card_ids_exact", card_ids == list(EXPECTED_LABELS),
        expected=list(EXPECTED_LABELS), observed=card_ids,
    )
    derived_by_card: dict[str, list[dict[str, Any]]] = {}
    derived_card_labels: dict[str, str] = {}
    card_results: list[dict[str, Any]] = []
    raw_cards_by_id = {row["card_id"]: row for row in raw["cards"]}
    raw_rows_by_key = {(row["card_id"], row["completion_index"]): row for row in raw["raw_rows"]}
    v.check(
        "coverage", "raw_card_count_and_uniqueness",
        len(raw["cards"]) == len(raw_cards_by_id) == 12,
        expected=12, observed={"rows": len(raw["cards"]), "unique": len(raw_cards_by_id)},
    )
    v.check(
        "coverage", "raw_completion_count_and_uniqueness",
        len(raw["raw_rows"]) == len(raw_rows_by_key) == 16,
        expected=16, observed={"rows": len(raw["raw_rows"]), "unique": len(raw_rows_by_key)},
    )

    for card in cards:
        card_id = card["id"]
        completions = [independent_completion(c) for c in card["completions"]]
        derived_by_card[card_id] = completions
        completion_labels = [c["label"] for c in completions]
        opposite = len(set(completion_labels)) > 1
        card_label = "underdeclared" if len(completions) > 1 and opposite else completion_labels[0]
        derived_card_labels[card_id] = card_label
        expected_missing = card.get("missing") or card.get("statement", {}).get("missing_premise")
        observed_card = raw_cards_by_id.get(card_id, {})
        per_card_issues: list[str] = []
        for i, derived in enumerate(completions):
            observed_completion = observed_card.get("completions", [{}] * len(completions))[i]
            directly_comparable = {
                key: derived[key]
                for key in [
                    "p", "dimension", "field", "domain_kind", "domain_points", "image_points",
                    "origin_preserving", "additive", "invariant",
                    "scalar_candidates_including_zero", "nonzero_scalar_candidates",
                    "permutation", "weaker_true_properties", "label", "map_f",
                ]
            }
            observed_comparable = {key: observed_completion.get(key) for key in directly_comparable}
            if not v.check(
                "predicate", f"{card_id}.completion[{i}].derived_fields",
                observed_comparable == directly_comparable,
                expected=directly_comparable, observed=observed_comparable,
            ):
                per_card_issues.append(f"completion {i} derived field mismatch")
            per_card_issues.extend(
                validate_failure_witnesses(
                    v, card_id, i, derived, observed_completion.get("failure_witnesses", {})
                )
            )
            flat = raw_rows_by_key.get((card_id, i), {})
            expected_flat = {
                "card_id": card_id,
                "completion_index": i,
                "field": derived["field"],
                "domain_points": derived["domain_points"],
                "image_points": derived["image_points"],
                "origin_preserving": derived["origin_preserving"],
                "additive": derived["additive"],
                "invariant": derived["invariant"],
                "scalar_candidates_including_zero": derived["scalar_candidates_including_zero"],
                "nonzero_scalar_candidates": derived["nonzero_scalar_candidates"],
                "permutation": derived["permutation"],
                "failure_witnesses": observed_completion.get("failure_witnesses", {}),
                "label": derived["label"],
                "missing_datum": expected_missing,
                "card_label": card_label,
            }
            if not v.check(
                "raw", f"{card_id}.completion[{i}].flat_raw_row",
                flat == expected_flat, expected=expected_flat, observed=flat,
            ):
                per_card_issues.append(f"completion {i} flat raw row mismatch")
        expected_card_summary = {
            "missing_datum": expected_missing,
            "completion_labels": completion_labels,
            "opposite_completion_outcomes": opposite,
            "label": card_label,
        }
        observed_card_summary = {
            key: observed_card.get(key) for key in expected_card_summary
        }
        if not v.check(
            "classification", f"{card_id}.card_summary",
            observed_card_summary == expected_card_summary,
            expected=expected_card_summary, observed=observed_card_summary,
        ):
            per_card_issues.append("card summary mismatch")
        v.check(
            "classification", f"{card_id}.oracle_label",
            card_label == EXPECTED_LABELS[card_id],
            expected=EXPECTED_LABELS[card_id], observed=card_label,
        )
        card_results.append(
            {
                "card_id": card_id,
                "derived_label": card_label,
                "derived_completion_labels": completion_labels,
                "opposite_completion_outcomes": opposite,
                "missing_datum": expected_missing,
                "completion_predicates": [
                    {
                        key: c[key]
                        for key in [
                            "p", "dimension", "domain_kind", "domain_points", "image_points",
                            "origin_preserving", "additive", "invariant",
                            "scalar_candidates_including_zero", "nonzero_scalar_candidates",
                            "permutation", "weaker_true_properties", "label",
                        ]
                    }
                    for c in completions
                ],
                "issues": per_card_issues,
            }
        )

    # Oracle completeness and the semantic truth of every obligation.
    oracle_entries = oracle["entries"]
    oracle_by_id = {row["card_id"]: row for row in oracle_entries}
    v.check(
        "oracle", "oracle_card_ids_exact",
        len(oracle_entries) == len(oracle_by_id) == 12 and list(oracle_by_id) == list(EXPECTED_LABELS),
        expected=list(EXPECTED_LABELS), observed=list(oracle_by_id),
    )
    for card_id, label in EXPECTED_LABELS.items():
        row = oracle_by_id.get(card_id, {})
        v.check(
            "oracle", f"{card_id}.oracle_expected_label", row.get("label") == label,
            expected=label, observed=row.get("label"),
        )
        v.check(
            "oracle", f"{card_id}.oracle_obligation_present",
            isinstance(row.get("obligation"), str) and bool(row["obligation"].strip()),
            observed=row.get("obligation"),
        )
    semantic_obligations = obligation_checks(derived_by_card)
    for card_id, obligations in semantic_obligations.items():
        for name, holds in obligations.items():
            v.check("oracle_obligation", f"{card_id}.{name}", holds)

    # Certificate completeness and agreement with independent derivation.
    certificates = certificates_document["certificates"]
    certificates_by_id = {row["card_id"]: row for row in certificates}
    required_certificate_fields = set(specification["execution_semantics"]["certificate_fields"])
    v.check(
        "certificate", "certificate_count_and_ids",
        len(certificates) == len(certificates_by_id) == 12 and list(certificates_by_id) == list(EXPECTED_LABELS),
        expected=list(EXPECTED_LABELS), observed=list(certificates_by_id),
    )
    for card in cards:
        card_id = card["id"]
        cert = certificates_by_id.get(card_id, {})
        derived = derived_by_card[card_id]
        first = derived[0]
        missing = card.get("missing") or card.get("statement", {}).get("missing_premise")
        v.check(
            "certificate", f"{card_id}.required_fields",
            required_certificate_fields <= set(cert),
            expected=sorted(required_certificate_fields), observed=sorted(set(cert)),
        )
        expected_scalar = {
            "including_zero": first["scalar_candidates_including_zero"],
            "nonzero": first["nonzero_scalar_candidates"],
        }
        basic_expected = {
            "card_id": card_id,
            "exact_question": fixtures["question"],
            "field_and_characteristic": first["field"],
            "ambient_object": f"{first['field']}^{first['dimension']}" if first["dimension"] > 1 else first["field"],
            "domain_C": {"kind": first["domain_kind"], "points": first["domain_points"]},
            "map_f": first["map_f"],
            "origin_and_additivity": {
                "origin_preserving": first["origin_preserving"],
                "additive": first["additive"],
            },
            "invariance_witness": {
                "invariant": first["invariant"],
                "failure_witnesses": raw_cards_by_id[card_id]["completions"][0]["failure_witnesses"].get("invariance", []),
            },
            "scalar_candidate_and_witness": expected_scalar,
            "nonzero_check": bool(first["nonzero_scalar_candidates"]),
            "label": derived_card_labels[card_id],
            "transfer_limits": TRANSFER_LIMIT,
            "weaker_true_properties": first["weaker_true_properties"],
        }
        observed_basic = {key: cert.get(key) for key in basic_expected}
        v.check(
            "certificate", f"{card_id}.basic_content",
            observed_basic == basic_expected, expected=basic_expected, observed=observed_basic,
        )
        expected_counter = (
            missing
            if derived_card_labels[card_id] == "underdeclared"
            else raw_cards_by_id[card_id]["completions"][0]["failure_witnesses"]
        )
        v.check(
            "certificate", f"{card_id}.counterexample_or_missing_premise",
            cert.get("counterexample_or_missing_premise") == expected_counter,
            expected=expected_counter, observed=cert.get("counterexample_or_missing_premise"),
        )
        if derived_card_labels[card_id] == "underdeclared":
            expected_two = []
            for i, completion in enumerate(derived):
                raw_completion = raw_cards_by_id[card_id]["completions"][i]
                expected_two.append(
                    {
                        "completion_index": i,
                        "field": completion["field"],
                        "domain_points": completion["domain_points"],
                        "image_points": completion["image_points"],
                        "label": completion["label"],
                        "nonzero_scalar_candidates": completion["nonzero_scalar_candidates"],
                        "invariant": completion["invariant"],
                        "permutation": completion["permutation"],
                        "failure_witnesses": raw_completion["failure_witnesses"],
                    }
                )
            v.check(
                "certificate", f"{card_id}.two_opposite_completions",
                cert.get("two_completions_if_underdeclared") == expected_two,
                expected=expected_two, observed=cert.get("two_completions_if_underdeclared"),
            )
            v.check(
                "certificate", f"{card_id}.all_completion_fields",
                cert.get("all_completion_fields") == [c["field"] for c in derived],
            )
            v.check(
                "certificate", f"{card_id}.all_completion_domains",
                cert.get("all_completion_domains") == [c["domain_points"] for c in derived],
            )
            v.check(
                "certificate", f"{card_id}.all_completion_maps",
                cert.get("all_completion_maps") == [c["map_f"] for c in derived],
            )
        else:
            v.check(
                "certificate", f"{card_id}.no_underdeclared_completion_block",
                cert.get("two_completions_if_underdeclared") is None,
                observed=cert.get("two_completions_if_underdeclared"),
            )

    # Independently recomputed metrics and exact reconciliation.
    frozen_prediction_formula = specification["preregistered_prediction"]["formula"]
    reported_prediction_formula = metrics["predicted_formula"]
    formula_semantically_equal = all(
        phrase in reported_prediction_formula.lower()
        for phrase in ("12/12", "zero false certifications", "4 positive", "4 underdeclared")
    )
    v.check(
        "metric", "predicted_formula_semantic_content",
        formula_semantically_equal,
        expected=frozen_prediction_formula,
        observed=reported_prediction_formula,
    )
    if frozen_prediction_formula != reported_prediction_formula:
        v.warning(
            "metadata",
            "predicted_formula_literal_copy",
            expected=frozen_prediction_formula,
            observed=reported_prediction_formula,
            detail=(
                "The metrics artifact adds spaces before 'positive' and "
                "'underdeclared' and omits the final word 'controls'. The numerical "
                "counts and semantic prediction are unchanged."
            ),
        )
    recomputed_metrics = {
        "complete_correct_certificates": sum(
            derived_card_labels[cid] == EXPECTED_LABELS[cid] for cid in EXPECTED_LABELS
        ),
        "oracle_label_matches": {
            cid: derived_card_labels[cid] == oracle_by_id[cid]["label"] for cid in EXPECTED_LABELS
        },
        "false_certifications_negative_controls": sum(
            derived_card_labels[cid] == "certified" for cid in ["N1", "N2", "N3", "N4"]
        ),
        "negative_control_ids": ["N1", "N2", "N3", "N4"],
        "positive_retention_valid_controls": sum(
            derived_card_labels[cid] == "certified" for cid in ["V1", "V2", "V3", "V4"]
        ),
        "positive_control_ids": ["V1", "V2", "V3", "V4"],
        "underdeclared_preservation": sum(
            derived_card_labels[cid] == "underdeclared"
            and len(set(c["label"] for c in derived_by_card[cid])) == 2
            for cid in ["U1", "U2", "U3", "U4"]
        ),
        "underdeclared_ids": ["U1", "U2", "U3", "U4"],
        "unsupported_strengthenings": sum(
            1
            for cid, label in derived_card_labels.items()
            if (label == "certified" and not (
                derived_by_card[cid][0]["invariant"]
                and derived_by_card[cid][0]["nonzero_scalar_candidates"]
            ))
            or (label == "underdeclared" and len(set(c["label"] for c in derived_by_card[cid])) < 2)
        ),
        "card_count": len(cards),
        "completion_count": sum(len(row) for row in derived_by_card.values()),
        "predicted_formula": reported_prediction_formula,
        "oracle_compared_after_raw": True,
        "seed": 0,
    }
    v.check(
        "metric", "metrics_json_exact_recomputation",
        metrics == recomputed_metrics, expected=recomputed_metrics, observed=metrics,
    )
    manifest_metric_expected = {
        key: recomputed_metrics[key]
        for key in [
            "complete_correct_certificates", "false_certifications_negative_controls",
            "positive_retention_valid_controls", "underdeclared_preservation",
            "unsupported_strengthenings", "card_count", "completion_count",
            "oracle_compared_after_raw",
        ]
    }
    v.check(
        "metric", "manifest_metrics_exact_recomputation",
        manifest["result"]["metrics"] == manifest_metric_expected,
        expected=manifest_metric_expected, observed=manifest["result"]["metrics"],
    )

    # Resource and execution-report consistency (not a remeasurement).
    manifest_resources = manifest["resources"]
    manifest_resource_values = {
        "wall_seconds": manifest["timing"]["wall_seconds"],
        "cpu_seconds": manifest_resources["cpu_seconds"],
        "peak_rss_bytes": manifest_resources["peak_rss_bytes"],
        "budget_wall_clock_seconds": manifest_resources["budget_wall_clock_seconds"],
        "budget_eval_process_wall_seconds": manifest_resources["budget_eval_process_wall_seconds"],
        "budget_cpu_seconds": manifest_resources["budget_cpu_seconds"],
        "budget_memory_gb": manifest_resources["budget_memory_gb"],
        "within_budget": manifest_resources["within_budget"],
    }
    resource_pairs = {
        key: (value, resources[key])
        for key, value in manifest_resource_values.items()
    }
    v.check(
        "resource", "resource_usage_matches_manifest",
        all(a == b for a, b in resource_pairs.values()),
        expected={k: a for k, (a, _) in resource_pairs.items()},
        observed={k: b for k, (_, b) in resource_pairs.items()},
    )
    independently_within = (
        0 <= resources["wall_seconds"] <= resources["budget_eval_process_wall_seconds"]
        and resources["wall_seconds"] <= resources["budget_wall_clock_seconds"]
        and 0 <= resources["cpu_seconds"] <= resources["budget_cpu_seconds"]
        and 0 <= resources["peak_rss_bytes"] <= resources["budget_memory_gb"] * (1024 ** 3)
        and resources["timeout"] is False
        and resources["exit_code"] == 0
    )
    v.check("resource", "resource_budget_arithmetic", independently_within)
    v.check("resource", "stderr_empty", (repo / STDERR).read_bytes() == b"")
    v.check(
        "report", "execution_report_ids",
        execution_report["experiment_id"] == EXPERIMENT_ID
        and execution_report["task_id"] == PRODUCER_TASK_ID
        and execution_report["implementation_commit"] == SNAPSHOT_PARENT,
    )
    v.check(
        "report", "execution_report_run_coverage",
        execution_report["runs"] == {"completed": [RUN_ID], "invalid": [], "failed": []},
        observed=execution_report["runs"],
    )
    v.check(
        "report", "execution_report_artifact_paths",
        execution_report["artifact_paths"] == [str(PRODUCER), *[str(p) for p in RUN_ARTIFACTS]],
        expected=[str(PRODUCER), *[str(p) for p in RUN_ARTIFACTS]],
        observed=execution_report["artifact_paths"],
    )
    run_dirs = sorted(str(path.relative_to(repo)) for path in (repo / BASE / "runs").iterdir() if path.is_dir())
    v.check(
        "coverage", "single_run_directory",
        run_dirs == [str(RUN)], expected=[str(RUN)], observed=run_dirs,
    )
    v.check(
        "coverage", "specification_required_artifacts_exact",
        specification["required_artifacts"] == [str(PRODUCER), *[str(p) for p in RUN_ARTIFACTS]],
        expected=[str(PRODUCER), *[str(p) for p in RUN_ARTIFACTS]],
        observed=specification["required_artifacts"],
    )

    limitations = [
        "The verifier does not rerun evaluate.py or any scientific experiment; it independently derives all finite predicates from fixtures.json.",
        "Original launch dirty-tree state, wall time, CPU time, and peak RSS cannot be remeasured from frozen artifacts; validation checks their internal consistency, bounds, and snapshot custody.",
        "Serialized outputs cannot alone prove temporal ordering. The committed producer source places oracle loading after raw-card construction, and the receipt flags that order, but original runtime chronology is not independently observable.",
        "The finite F_2/F_5 fixtures are toy controls and license no elliptic-curve, cryptographic-parameter, asymptotic, or hypothesis-status conclusion.",
    ]
    return finalize(
        v,
        recomputed_metrics,
        derived_card_labels,
        semantic_obligations,
        {
            "snapshot_commit": SNAPSHOT_COMMIT,
            "snapshot_parent": parent,
            "snapshot_paths": changed,
            "current_tree_mismatches": current_tree_mismatches,
        },
        card_results,
        limitations,
    )


def finalize(
    verifier: Verification,
    metrics: dict[str, Any],
    labels: dict[str, str],
    obligations: dict[str, Any],
    custody: dict[str, Any],
    cards: list[dict[str, Any]],
    limitations: list[str],
) -> dict[str, Any]:
    failed = [row for row in verifier.checks if row["status"] == "fail"]
    warnings = [row for row in verifier.checks if row["status"] == "warning"]
    passed = [row for row in verifier.checks if row["status"] == "pass"]
    by_category: dict[str, dict[str, int]] = {}
    for row in verifier.checks:
        counts = by_category.setdefault(
            row["category"], {"pass": 0, "fail": 0, "warning": 0}
        )
        counts[row["status"]] += 1
    return {
        "schema": "cm.typed_scope.independent_verification.v1",
        "task_id": TASK_ID,
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "checker_independence": {
            "implementation": "independently authored exact finite-field enumeration and artifact checker",
            "producer_module_imported": False,
            "producer_program_executed": False,
            "producer_source_read_for_source-aware_validation": True,
            "blind_rederivation_claimed": False,
        },
        "summary": {
            "status": "pass" if not failed else "fail",
            "checks_total": len(verifier.checks),
            "checks_passed": len(passed),
            "checks_failed": len(failed),
            "checks_warned": len(warnings),
            "by_category": by_category,
        },
        "custody": custody,
        "recomputed_metrics": metrics,
        "derived_card_labels": labels,
        "oracle_obligation_checks": obligations,
        "card_results": cards,
        "checks": verifier.checks,
        "discrepancies": [*failed, *warnings],
        "limitations": limitations,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run all checks and print the summary without creating an artifact.",
    )
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    result = verify(repo)
    if args.check_only:
        print(json.dumps(result["summary"], indent=2))
    else:
        if args.output is None:
            parser.error("--output is required unless --check-only is used")
        output = args.output if args.output.is_absolute() else repo / args.output
        with output.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
        print(json.dumps(result["summary"], sort_keys=True))
    return 0 if result["summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
