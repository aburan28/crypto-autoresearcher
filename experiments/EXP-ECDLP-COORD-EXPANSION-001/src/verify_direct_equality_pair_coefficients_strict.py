#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
BASE_PATH = SCRIPT_PATH.with_name(
    "verify_direct_equality_pair_coefficients.py"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "coefficient_base_verifier_for_strict", BASE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load coefficient verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()


def file_hash(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            state.update(block)
    return state.hexdigest()


def expected_keys(
    typed: dict[str, Any], families: list[str]
) -> list[tuple[str, str]]:
    return [
        (instance["curve"]["id"], family)
        for instance in typed["instances"]
        for family in families
    ]


def recorded_cut_valid(cut: dict[str, Any]) -> bool:
    return (
        cut["coordinate_digest_matches_v1"]
        and cut["basis_dimension"] == 3 * cut["degree"]
        and all(target["matches_v1"] for target in cut["targets"].values())
        and all(
            (
                not witness["present"]
                or (
                    witness["residual_zero"]
                    and witness["affine_output_matches"]
                    and witness["mutated_target_residual_nonzero"]
                )
            )
            for witness in cut["witness_checks"].values()
        )
        and cut["coefficient_mutation_control"]["digest_changed"]
        and cut["coefficient_mutation_control"]["evaluation_changed"]
    )


def envelope(
    raw: dict[str, Any], typed: dict[str, Any]
) -> dict[str, bool]:
    expected = expected_keys(typed, raw["config"]["families"])
    actual = [
        (row["curve_id"], row["family"]) for row in raw["rows"]
    ]
    rows_exact = actual == expected and len(actual) == len(set(actual))
    cuts_exact = rows_exact and all(
        [cut["cut"] for cut in row["cuts"]] == [2, 3]
        and row["valid"]
        == all(recorded_cut_valid(cut) for cut in row["cuts"])
        for row in raw["rows"]
    )
    summary = raw["summary"]
    summary_exact = rows_exact and (
        summary["family_rows"] == len(raw["rows"])
        and summary["all_exports_valid"]
        == all(row["valid"] for row in raw["rows"])
        and summary["coefficient_chunks_emitted"]
        == sum(
            len(cut["chunks"]) for row in raw["rows"] for cut in row["cuts"]
        )
        and summary["coefficient_field_elements"]
        == sum(
            cut["coefficient_field_elements"]
            for row in raw["rows"]
            for cut in row["cuts"]
        )
    )
    return {
        "expected_row_sequence_exact": rows_exact,
        "cuts_and_recorded_validity_exact": cuts_exact,
        "summary_totals_exact": summary_exact,
    }


def mutation_suite(
    raw: dict[str, Any], typed: dict[str, Any]
) -> dict[str, bool]:
    candidates: dict[str, dict[str, Any]] = {}
    dropped = copy.deepcopy(raw)
    dropped["rows"].pop()
    candidates["dropped_row"] = dropped
    duplicate = copy.deepcopy(raw)
    duplicate["rows"].append(copy.deepcopy(duplicate["rows"][0]))
    candidates["duplicate_row"] = duplicate
    total = copy.deepcopy(raw)
    total["summary"]["coefficient_chunks_emitted"] += 1
    candidates["summary_total"] = total
    missing_cut = copy.deepcopy(raw)
    missing_cut["rows"][0]["cuts"].pop()
    candidates["missing_cut"] = missing_cut
    row_valid = copy.deepcopy(raw)
    row_valid["rows"][0]["valid"] = False
    candidates["row_validity"] = row_valid
    mutation = copy.deepcopy(raw)
    mutation["rows"][0]["cuts"][0]["coefficient_mutation_control"][
        "digest_changed"
    ] = False
    candidates["mutation_control"] = mutation
    return {
        name: not all(envelope(candidate, typed).values())
        for name, candidate in candidates.items()
    }


def verify(
    raw_path: Path,
    typed_override: Path | None,
    v1_override: Path | None,
    v2_override: Path | None,
) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    typed_path = typed_override or Path(raw["config"]["typed_input"])
    v1_path = v1_override or Path(raw["config"]["v1_input"])
    v2_path = v2_override or Path(raw["config"]["v2_input"])
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    base = BASE.verify(raw_path, typed_path, v1_path, v2_path)
    checks = envelope(raw, typed)
    mutations = mutation_suite(raw, typed)
    valid = base["valid"] and all(checks.values()) and all(mutations.values())
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "direct-equality-pair-v3-coefficients-strict-verifier"
        ),
        "raw_result_sha256": file_hash(raw_path),
        "base_verifier_sha256": file_hash(BASE_PATH),
        "strict_verifier_sha256": file_hash(SCRIPT_PATH),
        "typed_input_sha256": file_hash(typed_path),
        "v1_input_sha256": file_hash(v1_path),
        "v2_input_sha256": file_hash(v2_path),
        "base_coefficient_reconstruction_valid": base["valid"],
        "envelope_checks": checks,
        "mutation_rejections": mutations,
        "valid": valid,
        "boundary": (
            "Closed fixed-fixture coefficient envelope. It does not "
            "establish factor minimality or a succinct index."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--typed-input", type=Path)
    parser.add_argument("--v1-input", type=Path)
    parser.add_argument("--v2-input", type=Path)
    args = parser.parse_args()
    receipt = verify(
        args.raw_result,
        args.typed_input,
        args.v1_input,
        args.v2_input,
    )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
