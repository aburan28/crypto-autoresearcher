"""Additive entry wrapper for EXP-ECDLP-abf981, source-v2 (engineering only).

Authorized by DEC-20260908-195f0f (`coordination/pending-ideas/BATCH-855d5d/
integration/partial-disposition.json`, `engineering_successor`). This file is
NEW and additive: it does not modify, monkeypatch, or bypass
`experiments/EXP-ECDLP-abf981/source/run_model_comparison.py`'s own CLI
refusal (its `main()` still prints `locked_runner_integration_unresolved`
and exits 2 for a scientific `--cell`/`--run-dir` invocation; only
`--mechanical-check`, which performs zero scientific runs, executes). This
wrapper imports the archived kernel's `finite_payload` and
`scientific_artifact_data` only for wiring -- **no scientific execution
occurs in this task**. `run_locked_models_cell` is dead code with respect to
this task: it exists so a future, separately authorized run-activation
amendment has one concrete, reviewed call site, but nothing in
`tests/test_finite_yaml_locked_v1.py` calls it, and
`maximum_scientific_runs` for this task's authorization is 0
(DEC-20260908-195f0f `engineering_authorization.maximum_scientific_runs`).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT_ID = "EXP-ECDLP-abf981"


def _import_archived_kernel():
    """Import the archived, immutable `run_model_comparison.py` kernel by
    exact file path. Import only -- this function does not call anything in
    the kernel, and nothing in this task calls `_import_archived_kernel`
    either.
    """
    import importlib.util

    kernel_path = REPO_ROOT / "experiments" / EXPERIMENT_ID / "source" / "run_model_comparison.py"
    package_dir = kernel_path.parent
    if str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))
    spec = importlib.util.spec_from_file_location("exp_ecdlp_abf981_models", kernel_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load archived kernel: {kernel_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_locked_models_cell(
    cell: str,
    run_dir: Path,
    manifest_context: dict[str, Any],
) -> dict[str, Any]:
    """Future admitted call site ONLY. Not invoked anywhere in this task
    (`maximum_scientific_runs: 0`; see module docstring).

    Mirrors exactly the sequence `experiments/EXP-ECDLP-abf981/source/
    run_model_comparison.py` already declares as the future admitted
    wrapper's responsibility: read the frozen specification by its pinned
    SHA-256 (`read_frozen_spec`), run the complete instrument body
    (`finite_payload`) into a caller-owned payload dict so a mid-run failure
    preserves the last object, then serialize with `scientific_artifact_data`
    and write via `emit_scientific_artifacts` into the exclusively-created
    run directory this wrapper's own caller (a verified `execute_locked`
    launch) is responsible for creating.

    This wrapper adds none of the kernel's own gates and removes none of
    them; a caller must still supply `manifest_context` sufficient for a
    future amendment to interpret, since the archived kernel itself performs
    no gate check inside `finite_payload` (unlike EXP-ECDLP-2cb7f8's
    `run_case`, which gates itself). That asymmetry is a genuine,
    disclosed difference between the two archived instruments, not
    something this wrapper papers over.
    """
    kernel = _import_archived_kernel()
    spec = kernel.read_frozen_spec(str(REPO_ROOT / "experiments" / EXPERIMENT_ID / "specification.yaml"))
    payload: dict[str, Any] = {"manifest_context": manifest_context}
    kernel.finite_payload(spec, cell, payload)
    artifact_data = kernel.scientific_artifact_data(payload)
    written = kernel.emit_scientific_artifacts(str(run_dir), payload)
    return {"payload": payload, "artifact_data_names": sorted(artifact_data), "written": written}
