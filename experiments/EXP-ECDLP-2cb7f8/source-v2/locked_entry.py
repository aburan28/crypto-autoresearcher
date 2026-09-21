"""Additive entry wrapper for EXP-ECDLP-2cb7f8, source-v2 (engineering only).

Authorized by DEC-20260908-195f0f (`coordination/pending-ideas/BATCH-855d5d/
integration/partial-disposition.json`, `engineering_successor`). This file is
NEW and additive: it does not modify, monkeypatch, or bypass
`experiments/EXP-ECDLP-2cb7f8/source/run.py`'s own CLI refusal (`main()`
still exits 2 with `UNRESOLVED_CANONICAL_RUNNER_INTERFACE`), and it imports
the archived `run_case` only for wiring -- **no scientific execution occurs
in this task**. `run_locked_case` below is dead code with respect to this
task: it is defined so a future, separately authorized run-activation
amendment has a concrete integration point, but nothing in
`tests/test_finite_yaml_locked_v1.py` calls it, and `maximum_scientific_runs`
for this task's authorization is 0 (DEC-20260908-195f0f
`engineering_authorization.maximum_scientific_runs`).

`validate_recovery_case_inventory` implements the ONE synthetic, purely
metadata-level check DEC-20260908-195f0f's `metric_interpretation.
required_checks` actually authorizes today: that the twelve named
`recovery_case_count` decision-grammar cases are present, unique, and
identically ordered across the B and I arms. It evaluates none of the arms'
scientific fields; `tests/test_finite_yaml_locked_v1.py` exercises it only
against the frozen inventory below and deliberately mutated copies.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT_ID = "EXP-ECDLP-2cb7f8"

# The exact twelve case IDs from DEC-20260908-195f0f's
# metric_interpretation.cases, in the frozen order. This is a name list, not
# a scientific measurement (partial-disposition.json
# `inventory_size_semantics`).
RECOVERY_CASE_IDS: tuple[str, ...] = (
    "c2_nonzero_c3_nonzero",
    "c2_nonzero_c3_zero",
    "c2_zero_h_degree_2",
    "c2_zero_h_degree_1",
    "c2_zero_h_degree_0",
    "root_y_two_nonzero",
    "root_y_zero",
    "root_y_absent",
    "residual_constant",
    "residual_nonconstant",
    "O_present",
    "O_absent",
)


class RecoveryInventoryError(ValueError):
    """Raised by `validate_recovery_case_inventory`; a metadata-shape
    refusal, never a scientific finding."""


def validate_recovery_case_inventory(cases: list[str]) -> None:
    """Refuse a `recovery_case_count` inventory that is reordered, has a
    deleted/added case, or contains a duplicate ID -- all pure metadata
    checks, exactly DEC-20260908-195f0f's `required_checks` first two
    bullets. Does not evaluate any scientific field or section.
    """
    if not isinstance(cases, list) or not all(isinstance(item, str) for item in cases):
        raise RecoveryInventoryError("recovery_case_count inventory must be a list of case-ID strings")
    if len(set(cases)) != len(cases):
        seen: set[str] = set()
        duplicates = sorted({item for item in cases if item in seen or seen.add(item)})
        raise RecoveryInventoryError(f"recovery_case_count inventory contains duplicate IDs: {duplicates}")
    if tuple(cases) != RECOVERY_CASE_IDS:
        missing = [case for case in RECOVERY_CASE_IDS if case not in cases]
        extra = [case for case in cases if case not in RECOVERY_CASE_IDS]
        reordered = missing == [] and extra == [] and tuple(cases) != RECOVERY_CASE_IDS
        raise RecoveryInventoryError(
            "recovery_case_count inventory does not match the frozen twelve-case order "
            f"(missing={missing}, extra={extra}, reordered_only={reordered})"
        )


def validate_recovery_case_arms(arm_b: list[str], arm_i: list[str]) -> None:
    """B and I must expose the identical ordered inventory (partial-
    disposition.json `metric_interpretation.sharing`). Each arm is validated
    on its own first so a caller sees the specific arm's defect."""
    validate_recovery_case_inventory(arm_b)
    validate_recovery_case_inventory(arm_i)
    if arm_b != arm_i:
        raise RecoveryInventoryError("B and I recovery_case_count inventories are not identical")


def _import_archived_kernel():
    """Import the archived, immutable `run.py` kernel by exact file path, so
    this wrapper never silently resolves a differently-named or shadowed
    module. Import only -- this function does not call anything in the
    kernel, and nothing in this task calls `_import_archived_kernel` either.
    """
    import importlib.util

    kernel_path = REPO_ROOT / "experiments" / EXPERIMENT_ID / "source" / "run.py"
    package_dir = kernel_path.parent
    if str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))
    spec = importlib.util.spec_from_file_location("exp_ecdlp_2cb7f8_run", kernel_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load archived kernel: {kernel_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_locked_case(
    config: dict[str, Any],
    directory: Path,
    manifest_context: dict[str, Any],
) -> dict[str, Any]:
    """Future admitted call site ONLY. Not invoked anywhere in this task
    (`maximum_scientific_runs: 0`; see module docstring). Present so a
    separately published run-activation amendment has one exact, reviewed
    call site rather than inventing its own.

    A caller reaching this function is responsible for everything
    `experiments/EXP-ECDLP-2cb7f8/source/run.py`'s own `run_case` docstring
    already declares out of scope for the instrument: mkdir/no-clobber,
    process-limit enforcement, canonical locked-plan verification, immutable
    manifest/log creation, actual runtime provenance, and exact directory
    binding. This wrapper adds none of the instrument's own gates and
    removes none of them -- `run_case` will itself raise `PermissionError` if
    any of its six required `manifest_context` gates is not `True`.
    """
    kernel = _import_archived_kernel()
    return kernel.run_case(config, directory, manifest_context)
