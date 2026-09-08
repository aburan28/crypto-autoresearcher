"""Guarded FUTURE scientific entry point for EXP-AUXIN-684adf.

This module implements NOTHING that executes now. It exists to hold the
orchestration shape (how crt.py, reference.py, fixtures.py, and
cost_model.py would be wired together for the one authorized scientific
run) behind a refusal gate that this implementation-only handoff
(TASK-20260907-58fcbe, maximum_runs=0) can never open.

Per the handoff's `implementation_requirements.driver_py` and the
specification's `execution_gate`:

    "Scientific execution requires canonical archival and committed
    Coordinator approval, an implementation-only handoff followed by an
    independent implementation review, and a separate scientific executor
    handoff with a genuine launch lock bound to the exact approved bytes."

Binding guarantees of this file:

  * No execution on import. Importing this module only defines functions,
    dataclasses, and constants; it performs no arithmetic, no file I/O, no
    fixture evaluation, and calls no function in crt.py, reference.py,
    fixtures.py, or cost_model.py.
  * No fixture-evaluation self-test on import. There is no module-level
    `if True:` smoke test, no doctest execution, nothing invoked as a side
    effect of `import driver`.
  * `run_calibration(...)` is the single prospective entry point for the
    later authorized scientific run. It is guarded by `preflight_guard(...)`,
    which MUST return `GuardResult(ok=True, ...)` before any cell is
    evaluated. This implementation handoff cannot itself produce a
    passing guard result: the required `GuardContext` fields
    (`spec_binding`, `source_hashes`, `independent_review_receipt`,
    `launch_lock`) do not exist yet, by design, at the time this file is
    written. Calling `run_calibration` today, with the honest empty
    context this task can supply, will refuse.
  * The one-worker / 4-GiB budget is enforced in the guard, not merely
    documented: `preflight_guard` rejects any requested worker count > 1
    or memory ceiling > 4 GiB before considering any other condition.
  * `run_calibration` describes, in its refusal path, exactly which
    planned artifacts (`required_artifacts` in the specification) it would
    write in a later authorized run; it does not write any of them now.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

MAX_WORKERS_ALLOWED = 1
MAX_MEMORY_BYTES_ALLOWED = 4 * 1024 * 1024 * 1024  # 4 GiB, per specification budget.memory_limit_bytes

REQUIRED_ARTIFACTS: Sequence[str] = (
    "manifest.yaml",
    "command.txt",
    "environment.json",
    "stdout.log",
    "stderr.log",
    "raw-result.json",
    "source-bindings.json",
    "launch-binding.json",
    "fixtures.jsonl",
    "truth.jsonl",
    "cases.jsonl",
    "reference-results.jsonl",
    "counterexamples.jsonl",
    "control-summary.json",
    "cost-frontier.json",
    "telemetry.json",
    "artifact-sha256.json",
    "execution-report.yaml",
)
EXACT_ARTIFACT_COUNT = 18


@dataclass(frozen=True)
class GuardContext:
    """Everything the guard needs to decide whether a scientific invocation
    may proceed. Every field defaults to a value that makes the guard
    refuse, so that an incompletely-constructed context is never
    accidentally permissive.
    """

    approved_spec_sha256: Optional[str] = None
    actual_spec_sha256: Optional[str] = None

    executing_source_hashes: Optional[Dict[str, str]] = None  # {"crt.py": sha256, ...}
    reviewed_source_hashes: Optional[Dict[str, str]] = None

    independent_review_receipt_id: Optional[str] = None
    independent_review_verdict: Optional[str] = None  # must be an explicit "approved"-equivalent value

    launch_lock_id: Optional[str] = None
    launch_lock_bound_run_id: Optional[str] = None
    launch_lock_bound_task_id: Optional[str] = None
    launch_lock_genuine: bool = False  # never default true

    requested_run_count: int = 0
    authorized_run_count: int = 1  # per specification budget.maximum_runs for the future scientific run

    requested_worker_count: int = 1
    requested_memory_bytes: int = MAX_MEMORY_BYTES_ALLOWED


@dataclass(frozen=True)
class GuardResult:
    ok: bool
    reasons: List[str] = field(default_factory=list)


def preflight_guard(ctx: GuardContext) -> GuardResult:
    """Evaluate every required precondition. Returns ok=True only if every
    check passes; otherwise lists every failing reason (not just the
    first), so a refusal is fully diagnosable without a retry loop.
    """
    reasons: List[str] = []

    if ctx.requested_worker_count > MAX_WORKERS_ALLOWED:
        reasons.append(
            f"requested_worker_count={ctx.requested_worker_count} exceeds "
            f"maximum_workers={MAX_WORKERS_ALLOWED}"
        )
    if ctx.requested_memory_bytes > MAX_MEMORY_BYTES_ALLOWED:
        reasons.append(
            f"requested_memory_bytes={ctx.requested_memory_bytes} exceeds "
            f"memory_limit_bytes={MAX_MEMORY_BYTES_ALLOWED}"
        )

    if ctx.approved_spec_sha256 is None or ctx.actual_spec_sha256 is None:
        reasons.append("missing approved or actual specification hash binding")
    elif ctx.approved_spec_sha256 != ctx.actual_spec_sha256:
        reasons.append("approved specification hash does not match the executing specification bytes")

    if not ctx.executing_source_hashes:
        reasons.append("missing executing source hash binding for crt.py/reference.py/fixtures.py/cost_model.py")
    if not ctx.reviewed_source_hashes:
        reasons.append("missing independently-reviewed source hash binding")
    if (
        ctx.executing_source_hashes
        and ctx.reviewed_source_hashes
        and ctx.executing_source_hashes != ctx.reviewed_source_hashes
    ):
        reasons.append("executing source hashes do not match the independently-reviewed source hashes")

    if ctx.independent_review_receipt_id is None:
        reasons.append("missing independent implementation review receipt")
    if ctx.independent_review_verdict not in ("approved", "passed"):
        reasons.append(
            f"independent review verdict {ctx.independent_review_verdict!r} is not an accepted approval value"
        )

    if not ctx.launch_lock_genuine:
        reasons.append("launch lock is not marked genuine")
    if ctx.launch_lock_id is None or ctx.launch_lock_bound_run_id is None or ctx.launch_lock_bound_task_id is None:
        reasons.append("launch lock is not bound to an allocated run/task identity")

    if ctx.requested_run_count > ctx.authorized_run_count:
        reasons.append(
            f"requested_run_count={ctx.requested_run_count} exceeds "
            f"authorized_run_count={ctx.authorized_run_count}"
        )
    if ctx.requested_run_count <= 0:
        reasons.append("requested_run_count must be a positive integer to run anything")

    return GuardResult(ok=(len(reasons) == 0), reasons=reasons)


class ScientificExecutionRefused(RuntimeError):
    """Raised by run_calibration whenever preflight_guard does not pass.
    This is the expected outcome of calling run_calibration under this
    implementation-only handoff, since no GuardContext produced here can
    be genuinely complete."""


def run_calibration(ctx: GuardContext, run_directory: Optional[str] = None) -> None:
    """The guarded FUTURE scientific entry point.

    This function's only executable behavior available to THIS task is
    refusal: it calls `preflight_guard` and raises
    `ScientificExecutionRefused` listing every unmet precondition. It is
    documented here, not implemented as a working pipeline, because
    implementing the working pipeline body would require deciding what "one
    scientific run" concretely writes -- and per this handoff, no fixture
    evaluation, CRT fold, reference enumeration, or artifact write may occur
    now, not even as a smoke test.

    A later, separately authorized scientific executor handoff supplies:
      * an allocated RUN_ID and run_directory
        (experiments/EXP-AUXIN-684adf/runs/<RUN_ID>/),
      * a genuine launch lock bound to the exact approved spec/code/review
        bytes,
      * the independent implementation review receipt for crt.py,
        reference.py, fixtures.py, cost_model.py, and this file,
      * and only then may extend this function (in a new, superseding
        version of this file under that later task's own write_scope) to
        actually call fixtures.py's generators, crt.py's combiner,
        reference.py's independent verifier, and cost_model.py's proxies
        for every one of the 26546 declared cases, and to write exactly the
        18 artifacts named in REQUIRED_ARTIFACTS to that run_directory.

    Calling this function now will always raise, because no complete,
    honest GuardContext exists yet -- which is the intended, safe behavior.
    """
    result = preflight_guard(ctx)
    if not result.ok:
        raise ScientificExecutionRefused(
            "Scientific execution refused by preflight guard. This "
            "implementation-only handoff (TASK-20260907-58fcbe, "
            "maximum_runs=0) authorizes zero scientific invocations; a "
            "later scientific handoff must supply its own allocated run "
            "identity and genuine launch lock. Unmet preconditions: "
            + "; ".join(result.reasons)
        )
    # Unreachable under this handoff: no code path below this line may run
    # until a later, separately authorized scientific handoff supplies a
    # GuardContext that genuinely satisfies preflight_guard, at which point
    # the pipeline body (fixture generation -> crt fold -> independent
    # reference check -> cost-model accounting -> artifact serialization to
    # run_directory, honoring REQUIRED_ARTIFACTS and EXACT_ARTIFACT_COUNT)
    # is added under that later task's own write_scope, not this one.
    raise NotImplementedError(
        "run_calibration's pipeline body is intentionally unimplemented in "
        "this implementation-only handoff; only the refusal path above may "
        "execute."
    )


def describe_planned_artifacts() -> Dict[str, object]:
    """Pure documentation helper: returns the exact planned artifact list
    and count for the future run, without writing anything. Safe to call
    (no I/O, no arithmetic over fixture data), but not invoked at import
    time."""
    return {
        "run_directory_template": "experiments/EXP-AUXIN-684adf/runs/<allocated_RUN_ID>/",
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "exact_filename_count": EXACT_ARTIFACT_COUNT,
    }


if __name__ == "__main__":
    # Even a direct CLI invocation of this file only demonstrates the
    # refusal path with an intentionally empty (honest) context; it never
    # supplies a genuine launch lock, review receipt, or hash binding
    # itself. This is documentation of the future CLI shape, not a claim
    # that any scientific run occurred.
    empty_ctx = GuardContext(requested_run_count=1)
    try:
        run_calibration(empty_ctx)
    except ScientificExecutionRefused as exc:
        print("REFUSED (expected under this implementation-only handoff):")
        print(str(exc))
