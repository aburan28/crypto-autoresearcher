"""Bridge: execute an approved experiment run on the shared taskq queue and
turn the queue's result into an ordinary, immutable run package.

The taskq queue (aburan28/crypto, `taskq/`) moves a command to a worker pod at
a pinned commit and moves the measurement back as a write-once
`taskq.task-result/v1` document. This module is the submitter-side adapter:

    build_spec()          experiment run -> taskq.task-spec/v1
    submit() / wait()     thin wrappers over the `taskq` package (optional)
    write_run_package()   taskq.task-result/v1 -> experiments/<EXP>/runs/<RUN>/

The run package has the same files and manifest fields `harness/runner.py`
writes (manifest.yaml, command.txt, environment.json, stdout.log, stderr.log,
raw-result.json). What differs is WHO measured: timings and resources come
from the worker's wait4(2) measurement recorded in the result, never from the
caller (the same rule as `runner.run_wrapped`, DEC-20260810-1163ec F-4(e)).

Rules this module keeps rather than restates:

* Certificates are re-verified HERE, on the submitter side, by calling
  `runner._verify` and `runner._cairn_cross_check` -- the functions
  `runner.write_run` calls -- and the invalid_measurement verdict is
  `write_run`'s own rule. harness/runner.py itself is not edited: locked
  execution plans pin it by sha256 (harness/finite_yaml_locked_v3.py
  ORIGINAL_SOURCE_PINS), so the few lines of `write_run` that sequence those
  calls are mirrored below in `verify_certificate` / `apply_certificate_verdict`
  / `certificate_summary`, and tests/test_taskq_bridge.py holds them equal to
  `write_run`'s output. A worker-side `verification` block, when
  a newer worker writes one, is ADVISORY: it is recorded, a disagreement with
  this repo's verdict is flagged, and it never decides the status.
* Run directories are never overwritten (FileExistsError), and every refusal
  happens before the directory is created, so a refused package never leaves
  an empty RUN id behind.
* taskq `not_completed` (timeout / cancelled / infra_error) is NEVER a
  negative observation (AGENTS.md rule 3): it maps to `failed_infrastructure`
  with `result.valid: false`.

Nothing here approves an experiment, allocates an id, or writes a ledger
record. A task id is not an approval; the Coordinator's approval of the
experiment comes before submission.

The vendored schemas in `harness/taskq_schemas/` are byte copies of
aburan28/crypto `taskq/taskq/schemas/*.v1.json` at commit
a2968daa8843464ae7dae13cabb0677239c03b25. They are used for offline validation;
`jsonschema` is used when installed, otherwise a small subset validator.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shlex
from collections.abc import Callable
from typing import Any

import yaml

from . import runner

SPEC_SCHEMA_ID = "taskq.task-spec/v1"
RESULT_SCHEMA_ID = "taskq.task-result/v1"
SOURCE_REPO = "crypto-autoresearcher"

# taskq/protocol.py: which terminal statuses mean "the command ran to exit".
TASKQ_COMPLETED = ("succeeded", "failed")
TASKQ_NOT_COMPLETED = ("timeout", "cancelled", "infra_error")
TASKQ_TERMINAL_STATES = TASKQ_COMPLETED + TASKQ_NOT_COMPLETED + ("dead",)

# Manifest statuses this bridge can write. `completed_invalid` is produced only
# by apply_certificate_verdict (write_run's rule).
STATUS_SUCCEEDED = "completed_valid"
STATUS_FAILED = "failed"
STATUS_NOT_COMPLETED = "failed_infrastructure"

LOG_PATHS = {
    "stdout": ("_taskq_logs/stdout.log", "_taskq_logs/stdout.log.truncated"),
    "stderr": ("_taskq_logs/stderr.log", "_taskq_logs/stderr.log.truncated"),
}
CERTIFICATE_FILE = "certificate.json"

_EXP_ID = re.compile(r"^EXP-[A-Za-z0-9._-]+$")
_RUN_ID = re.compile(r"^RUN-[A-Za-z0-9._-]+$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")

_SCHEMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "taskq_schemas")


class BridgeError(ValueError):
    """The result cannot be turned into a run package as given."""


class ArtifactIntegrityError(BridgeError):
    """An artifact's bytes do not match the sha256/size the result recorded."""


class TaskqUnavailable(RuntimeError):
    """The optional `taskq` package (and its Redis client) is not installed."""


# -- schemas -----------------------------------------------------------------

def load_schema(name: str) -> dict[str, Any]:
    with open(os.path.join(_SCHEMA_DIR, name), encoding="utf-8") as fh:
        return json.load(fh)


SPEC_SCHEMA = load_schema("task-spec.v1.json")
RESULT_SCHEMA = load_schema("task-result.v1.json")

_JSON_TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "null": type(None),
}


def _is_type(value: Any, name: str) -> bool:
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _JSON_TYPES[name])


def _subset_validate(doc: Any, schema: dict[str, Any], where: str = "") -> None:
    """The subset of JSON Schema the two taskq v1 schemas use.

    Used only when `jsonschema` is not installed, so this repository keeps a
    real (if smaller) check without taking a new dependency.
    """
    at = where or "<root>"
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(doc, t) for t in types):
            raise BridgeError(f"{at}: expected {'|'.join(types)}, got {type(doc).__name__}")
    if "const" in schema and doc != schema["const"]:
        raise BridgeError(f"{at}: must equal {schema['const']!r}")
    if "enum" in schema and doc not in schema["enum"]:
        raise BridgeError(f"{at}: {doc!r} is not one of {schema['enum']}")
    if isinstance(doc, str):
        if "pattern" in schema and not re.search(schema["pattern"], doc):
            raise BridgeError(f"{at}: {doc!r} does not match {schema['pattern']}")
        if "maxLength" in schema and len(doc) > schema["maxLength"]:
            raise BridgeError(f"{at}: longer than {schema['maxLength']}")
    if _is_type(doc, "number"):
        if "minimum" in schema and doc < schema["minimum"]:
            raise BridgeError(f"{at}: below minimum {schema['minimum']}")
        if "maximum" in schema and doc > schema["maximum"]:
            raise BridgeError(f"{at}: above maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema and doc <= schema["exclusiveMinimum"]:
            raise BridgeError(f"{at}: must exceed {schema['exclusiveMinimum']}")
    if isinstance(doc, dict):
        for key in schema.get("required", []):
            if key not in doc:
                raise BridgeError(f"{at}: missing required {key!r}")
        props = schema.get("properties", {})
        for key, value in doc.items():
            if key in props:
                _subset_validate(value, props[key], f"{where}/{key}")
            elif schema.get("additionalProperties") is False:
                raise BridgeError(f"{at}: unexpected property {key!r}")
            elif isinstance(schema.get("additionalProperties"), dict):
                _subset_validate(value, schema["additionalProperties"], f"{where}/{key}")
    if isinstance(doc, list):
        if "minItems" in schema and len(doc) < schema["minItems"]:
            raise BridgeError(f"{at}: fewer than {schema['minItems']} items")
        if "items" in schema:
            for i, item in enumerate(doc):
                _subset_validate(item, schema["items"], f"{where}/{i}")


def _validate(doc: Any, schema: dict[str, Any]) -> None:
    try:
        import jsonschema
    except ImportError:
        _subset_validate(doc, schema)
        return
    try:
        jsonschema.validate(doc, schema)
    except jsonschema.ValidationError as err:
        where = "/".join(str(p) for p in err.absolute_path) or "<root>"
        raise BridgeError(f"{where}: {err.message}") from None


def validate_spec(spec: dict[str, Any]) -> None:
    _validate(spec, SPEC_SCHEMA)


def validate_result(result: dict[str, Any]) -> None:
    _validate(result, RESULT_SCHEMA)


def canonical_json(doc: Any) -> bytes:
    """taskq/protocol.py canonical_json: the bytes spec_sha256 is taken over."""
    return json.dumps(doc, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode()


def spec_sha256(spec: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(spec)).hexdigest()


# -- spec --------------------------------------------------------------------

def idempotency_key(exp_id: str, run_id: str) -> str:
    """One key per planned run: re-dispatching the same RUN cannot run twice."""
    return f"{exp_id}/{run_id}"


def build_spec(exp_id: str, run_id: str, argv: list[str], commit: str, *,
               queue: str = "cpu", repetitions: int | None = None,
               warmups: int = 1, setup: list[list[str]] | None = None,
               cwd: str = ".", env: dict[str, str] | None = None,
               timeout: float = 3600, setup_timeout: float | None = None,
               memory_mb: int | None = None, cpus: int | None = None,
               max_attempts: int | None = None,
               sparse_paths: list[str] | None = None,
               submitted_by: str = "executor",
               labels: dict[str, str] | None = None,
               worker_verify: bool = False) -> dict[str, Any]:
    """A taskq.task-spec/v1 for one planned run of an approved experiment.

    `commit` must be a full, PUSHED 40-hex sha: the worker fetches it from the
    remote and runs exactly that tree. `repetitions` makes it a benchmark
    (`warmups` unrecorded + `repetitions` timed executions); omitted, argv runs
    once. Extra `labels` (goal, task) may be added but cannot override the
    experiment/run/submitted_by provenance labels.

    `worker_verify=True` adds `"verify": {"builtin": "certificate"}`, asking a
    worker that supports it (aburan28/crypto#1091) to run taskq.verify on each
    run's certificate.json. That verdict is ADVISORY only; the field is not in
    the v1 schema vendored here, so the rest of the spec is validated without
    it, and a taskq client or worker that predates it refuses the spec.
    """
    if not _EXP_ID.match(exp_id):
        raise BridgeError(f"bad experiment id {exp_id!r}")
    if not _RUN_ID.match(run_id):
        raise BridgeError(f"bad run id {run_id!r}")
    if not _COMMIT.match(commit or ""):
        raise BridgeError(f"commit must be a full 40-hex sha, got {commit!r}")
    if not argv:
        raise BridgeError("argv is empty")
    base_labels = {"experiment": exp_id, "run": run_id, "submitted_by": submitted_by}
    extra = dict(labels or {})
    clash = sorted(k for k in extra if k in base_labels and extra[k] != base_labels[k])
    if clash:
        raise BridgeError(f"labels may not override provenance labels: {clash}")
    spec: dict[str, Any] = {
        "schema": SPEC_SCHEMA_ID,
        "queue": queue,
        "kind": "benchmark" if repetitions else "command",
        "source": {"repo": SOURCE_REPO, "commit": commit},
        "command": {"argv": [str(a) for a in argv], "cwd": cwd,
                    "env": dict(env or {}),
                    "setup": [list(step) for step in (setup or [])]},
        "limits": {"timeout_seconds": timeout},
        "idempotency_key": idempotency_key(exp_id, run_id),
        "labels": {**extra, **base_labels},
    }
    if sparse_paths:
        spec["source"]["sparse_paths"] = list(sparse_paths)
    if repetitions:
        spec["benchmark"] = {"warmups": warmups, "repetitions": repetitions}
    if setup_timeout is not None:
        spec["limits"]["setup_timeout_seconds"] = setup_timeout
    if memory_mb is not None:
        spec["limits"]["memory_mb"] = memory_mb
    if cpus is not None:
        spec["placement"] = {"cpus": cpus}
    if max_attempts is not None:
        spec["retry"] = {"max_attempts": max_attempts}
    validate_spec(spec)
    if worker_verify:
        spec["verify"] = {"builtin": "certificate"}
    return spec


# -- queue access (optional dependency) --------------------------------------

def _store(store: Any = None) -> Any:
    if store is not None:
        return store
    try:
        from taskq.config import store_from_env
    except ImportError as err:
        raise TaskqUnavailable(
            "the `taskq` package is not installed; install it from "
            "aburan28/crypto (`pip install -e 'taskq[mcp]'`) and set "
            "TASKQ_REDIS_URL, or use the taskq MCP server") from err
    return store_from_env()


def submit(spec: dict[str, Any], store: Any = None) -> dict[str, Any]:
    """Enqueue `spec`. Returns {task_id, spec_sha256, deduplicated}.

    A resubmission with the same idempotency key returns the first task's id
    (`deduplicated: true`); the same key with a different spec is refused by
    the queue.
    """
    validate_spec({k: v for k, v in spec.items() if k != "verify"})
    return _store(store).submit(spec)


def wait(task_id: str, timeout: float | None = None, store: Any = None,
         chunk_seconds: float = 300) -> dict[str, Any] | None:
    """Block until the task is terminal (or `timeout` elapses); returns the task.

    `timeout=None` waits indefinitely, in `chunk_seconds` slices. Waiting out a
    timeout is NOT a task outcome: the task keeps running and is still owed
    its result.
    """
    import time
    s = _store(store)
    deadline = None if timeout is None else time.monotonic() + timeout
    while True:
        left = chunk_seconds if deadline is None else min(
            chunk_seconds, max(0.0, deadline - time.monotonic()))
        task = s.wait(task_id, left)
        if task is None or task.get("state") in TASKQ_TERMINAL_STATES:
            return task
        if deadline is not None and time.monotonic() >= deadline:
            return task


def fetch(task_id: str, store: Any = None) -> tuple[dict | None, dict | None]:
    """(task record with its normalised spec, write-once result or None)."""
    s = _store(store)
    return s.get_task(task_id), s.get_result(task_id)


# -- artifacts ---------------------------------------------------------------

ArtifactFetch = Callable[[dict[str, Any]], bytes]


def uri_fetch(entry: dict[str, Any]) -> bytes:
    """Read an artifact from its `uri` (a path on the artifact store volume)."""
    uri = entry.get("uri")
    if not uri:
        raise BridgeError(f"artifact {entry.get('path')!r} has no uri; pass an "
                          f"artifact_fetch that can read it")
    path = uri[len("file://"):] if uri.startswith("file://") else uri
    with open(path, "rb") as fh:
        return fh.read()


def dir_fetch(artifact_root: str, task_id: str, attempt: int) -> ArtifactFetch:
    """Read artifacts from a local copy of the worker's --artifact-dir
    (`<root>/<task_id>/attempt-<n>/<path>`)."""
    base = os.path.join(artifact_root, task_id, f"attempt-{attempt}")

    def _fetch(entry: dict[str, Any]) -> bytes:
        rel = entry["path"]
        if os.path.isabs(rel) or ".." in rel.split("/"):
            raise BridgeError(f"artifact path {rel!r} escapes the artifact root")
        with open(os.path.join(base, rel), "rb") as fh:
            return fh.read()
    return _fetch


def fetch_verified(entry: dict[str, Any], artifact_fetch: ArtifactFetch) -> bytes:
    """Artifact bytes, refused unless they match the recorded sha256 and size."""
    data = artifact_fetch(entry)
    digest = hashlib.sha256(data).hexdigest()
    if digest != entry.get("sha256"):
        raise ArtifactIntegrityError(
            f"artifact {entry.get('path')!r}: sha256 {digest} does not match the "
            f"result's {entry.get('sha256')}; refusing to use it")
    if len(data) != entry.get("bytes"):
        raise ArtifactIntegrityError(
            f"artifact {entry.get('path')!r}: {len(data)} bytes, result says "
            f"{entry.get('bytes')}; refusing to use it")
    return data


# -- certificates ------------------------------------------------------------

def _as_int(v: Any) -> Any:
    """Wire integers may be ints, decimal strings or 0x-hex strings."""
    if isinstance(v, bool) or isinstance(v, int):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        try:
            return int(s, 16) if s.startswith("0x") else int(s, 10)
        except ValueError:
            return v
    return v


def to_runner_certificate(cert: dict[str, Any]) -> dict[str, Any]:
    """Adapt the taskq wire form of a certificate to what runner._verify reads.

    Format only, no judgement: the shared format allows the curve at the top
    level (`cert.curve`) where runner._verify reads `statement.curve`, and
    allows integers as decimal/0x strings. A prime-field curve and the
    statement's P, Q, k are moved/coerced; anything else is passed through
    untouched, and a shape runner._verify cannot read fails verification.
    """
    out = copy.deepcopy(cert)
    if out.get("kind") != "discrete_log":
        return out
    st = out.get("statement")
    if not isinstance(st, dict):
        return out
    curve = st.get("curve", out.get("curve"))
    if isinstance(curve, dict) and curve.get("field", "prime") == "prime":
        st["curve"] = {**curve, **{k: _as_int(curve[k]) for k in ("p", "a", "b")
                                   if k in curve}}
    for pt in ("P", "Q"):
        if isinstance(st.get(pt), list):
            st[pt] = [_as_int(c) for c in st[pt]]
    if "k" in st:
        st["k"] = _as_int(st["k"])
    return out


# -- runner.write_run's certificate discipline -------------------------------
#
# Mirrors harness/runner.py write_run (certificate block and the
# completed_invalid override). runner.py cannot be refactored to export these:
# it is sha256-pinned by locked plans. A drift test compares the two.

# The kinds write_run treats as solve/relation claims.
CLAIM_CERTIFICATE_KINDS = ("discrete_log", "decomposition", "md5_collision_pair")


def verify_certificate(certificate: dict, commit: str
                       ) -> tuple[dict, bool, dict | None]:
    """write_run's verification sequence: runner._verify, annotate, then the
    cairn cross-check (which raises RuntimeError on a disagreement)."""
    cert = dict(certificate)
    verified, verifier = runner._verify(cert)
    cert["verified"] = verified
    cert["verifier"] = verifier
    cert["verifier_commit"] = commit
    cairn_cross_check = runner._cairn_cross_check(cert, verified)
    if cairn_cross_check is not None:
        cert["cairn_cross_check"] = cairn_cross_check
    return cert, verified, cairn_cross_check


def apply_certificate_verdict(status: str, valid: bool,
                              invalid_reason: str | None, cert: dict,
                              verified: bool) -> tuple[str, bool, str | None]:
    """write_run: a claim that fails independent verification is
    completed_invalid (invalid_measurement), never a result."""
    if cert.get("kind") in CLAIM_CERTIFICATE_KINDS and not verified:
        return ("completed_invalid", False,
                "certificate failed independent verification")
    return status, valid, invalid_reason


def certificate_summary(cert: dict, cairn_cross_check: dict | None) -> dict:
    """write_run's manifest run.result.certificate block."""
    return {"kind": cert.get("kind"),
            "verified": cert.get("verified"),
            "verifier": cert.get("verifier"),
            **({"failing_checks": cert["failing_checks"]}
               if cert.get("failing_checks") else {}),
            **({"cairn_cross_check": cairn_cross_check}
               if cairn_cross_check is not None else {})}


def _verify_one(cert: dict[str, Any], commit: str) -> tuple[dict, bool, dict | None]:
    """verify_certificate, with an unreadable certificate recorded as
    unverified instead of crashing the package write.

    runner._verify raises on a certificate it cannot parse (e.g. a
    binary-field curve, which it has no arithmetic for). write_run would let
    that propagate; here the run already happened remotely, so the honest
    record is `verified: false` with the reason -- which for a claim-bearing
    kind is completed_invalid, never a result.
    """
    try:
        runner._verify(copy.deepcopy(cert))
    except Exception as exc:  # noqa: BLE001 -- recorded, not swallowed
        bad = dict(cert)
        bad.update(verified=False,
                   verifier=f"error:{type(exc).__name__}: {exc}",
                   verifier_commit=commit)
        return bad, False, None
    return verify_certificate(cert, commit)


def _plan_length(spec: dict[str, Any]) -> int:
    if spec.get("kind") == "benchmark":
        bench = spec.get("benchmark") or {}
        return int(bench.get("warmups", 1)) + int(bench.get("repetitions", 5))
    return 1


def _certificate_path(spec: dict[str, Any], index: int) -> str:
    """taskq/execute.py: each execution gets `run-<i>/` when the plan has more
    than one, else the output dir itself."""
    return (f"run-{index}/{CERTIFICATE_FILE}" if _plan_length(spec) > 1
            else CERTIFICATE_FILE)


# -- the run package ---------------------------------------------------------

def _recorded_runs(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in result.get("runs", []) if not r.get("warmup")]


def _command_text(spec: dict[str, Any], result: dict[str, Any]) -> str:
    cmd = spec["command"]
    src = result["source"]
    lines = [
        f"# taskq task {result['task_id']} (attempt {result['attempt']}, "
        f"fence {result['fence']}) on queue {spec.get('queue')}",
        f"# source {src.get('repo')}@{src.get('resolved_commit') or src.get('commit')}"
        f"{'' if src.get('resolved_commit') else ' (NOT resolved: never checked out)'}",
        f"# cwd {cmd.get('cwd', '.')}",
    ]
    for k, v in sorted((cmd.get("env") or {}).items()):
        lines.append(f"# env {k}={v}")
    for step in cmd.get("setup") or []:
        lines.append(f"# setup {shlex.join(step)}")
    if spec.get("kind") == "benchmark":
        b = spec.get("benchmark") or {}
        lines.append(f"# benchmark warmups={b.get('warmups')} "
                     f"repetitions={b.get('repetitions')}")
    lines.append(shlex.join(cmd["argv"]))
    return "\n".join(lines) + "\n"


def _check_binding(result: dict[str, Any], spec: dict[str, Any],
                   task_meta: dict[str, Any] | None, exp_id: str,
                   run_id: str) -> str:
    """Refuse a result that is not the one this RUN asked for. Returns the
    spec sha256 that matched."""
    if result.get("schema") != RESULT_SCHEMA_ID:
        raise BridgeError(f"not a {RESULT_SCHEMA_ID} document")
    validate_result(result)
    expected_class = "completed" if result["status"] in TASKQ_COMPLETED else "not_completed"
    if result["outcome_class"] != expected_class:
        raise BridgeError(f"status {result['status']} with outcome_class "
                          f"{result['outcome_class']} is inconsistent")
    digest = spec_sha256(spec)
    if digest != result["spec_sha256"]:
        try:  # a caller may pass the spec as submitted; normalise if we can
            from taskq import protocol
            digest = protocol.spec_sha256(protocol.normalize_spec(spec))
        except ImportError:
            pass
    if digest != result["spec_sha256"]:
        raise BridgeError(
            f"spec sha256 {digest} does not match the result's "
            f"{result['spec_sha256']}; pass the normalised spec the task ran "
            f"(task_meta['spec'])")
    if task_meta:
        if task_meta.get("task_id") not in (None, result["task_id"]):
            raise BridgeError(f"task_meta is {task_meta.get('task_id')}, result "
                              f"is {result['task_id']}")
        if task_meta.get("spec_sha256") not in (None, result["spec_sha256"]):
            raise BridgeError("task_meta spec_sha256 differs from the result's")
    if spec["source"]["repo"] != SOURCE_REPO:
        raise BridgeError(f"source repo {spec['source']['repo']!r} is not {SOURCE_REPO}")
    labels = spec.get("labels") or {}
    if labels.get("experiment") != exp_id or labels.get("run") != run_id:
        raise BridgeError(
            f"spec labels name {labels.get('experiment')}/{labels.get('run')}, "
            f"not {exp_id}/{run_id}")
    if spec.get("idempotency_key") != idempotency_key(exp_id, run_id):
        raise BridgeError(f"idempotency_key {spec.get('idempotency_key')!r} is not "
                          f"{idempotency_key(exp_id, run_id)!r}")
    resolved = result["source"].get("resolved_commit")
    if resolved is not None and resolved != spec["source"]["commit"]:
        raise BridgeError(f"worker resolved {resolved}, spec pinned "
                          f"{spec['source']['commit']}")
    return digest


def _base_status(result: dict[str, Any]) -> tuple[str, bool, str | None]:
    """taskq status -> (manifest status, valid, invalid_reason), before the
    certificate verdict. See the table in docs/taskq-execution.md."""
    ts, err = result["status"], result.get("error")
    if ts == "succeeded":
        return STATUS_SUCCEEDED, True, None
    if ts == "failed":
        return (STATUS_FAILED, False,
                f"taskq status failed: {err or 'command exited nonzero'}. The "
                f"command did not exit 0; a crash is never negative mathematical "
                f"evidence (AGENTS.md rule 3).")
    return (STATUS_NOT_COMPLETED, False,
            f"taskq status {ts} (outcome_class not_completed): "
            f"{err or 'no detail'}. Never negative mathematical evidence "
            f"(AGENTS.md rule 3).")


def write_run_package(result: dict[str, Any], spec: dict[str, Any] | None,
                      task_meta: dict[str, Any] | None, exp_dir: str,
                      run_id: str, artifact_fetch: ArtifactFetch = uri_fetch, *,
                      inputs: dict[str, Any] | None = None) -> str:
    """Write experiments/<EXP>/runs/<RUN>/ from a taskq result. Returns run_dir.

    `spec` is the NORMALISED spec the task ran (`task_meta['spec']` from
    `taskq get_task`); None takes it from `task_meta`. `exp_dir` is the
    experiment directory (its basename is the experiment id). `inputs` is the
    manifest's run.inputs (curve_id, seed, parameters) -- the queue does not
    know them.

    Every refusal (existing RUN dir, schema, spec/label binding, artifact hash
    mismatch, cairn disagreement) is raised before the directory is created.
    """
    exp_dir = os.path.abspath(exp_dir)
    exp_id = os.path.basename(exp_dir.rstrip(os.sep))
    run_dir = os.path.join(exp_dir, "runs", run_id)
    if os.path.exists(run_dir):
        raise FileExistsError(
            f"run {run_id} already exists at {run_dir}; run records are "
            f"immutable -- supersede with a new RUN id, do not overwrite")
    if not _RUN_ID.match(run_id):
        raise BridgeError(f"bad run id {run_id!r}")
    if spec is None:
        spec = (task_meta or {}).get("spec")
        if spec is None:
            raise BridgeError("no spec: pass it or a task_meta carrying it")
    digest = _check_binding(result, spec, task_meta, exp_id, run_id)

    by_path = {a["path"]: a for a in result.get("artifacts", [])}
    used: list[dict[str, Any]] = []

    def get(path: str) -> bytes | None:
        entry = by_path.get(path)
        if entry is None:
            return None
        data = fetch_verified(entry, artifact_fetch)
        used.append({k: entry[k] for k in ("path", "sha256", "bytes")})
        return data

    logs: dict[str, str] = {}
    truncated: list[str] = []
    for stream, candidates in LOG_PATHS.items():
        text = None
        for path in candidates:
            data = get(path)
            if data is not None:
                text = data.decode("utf-8", errors="replace")
                if path.endswith(".truncated"):
                    truncated.append(stream)
                break
        logs[stream] = text if text is not None else ""

    # This repo's verifier commit: verification runs here, not on the worker.
    local_commit, _ = runner.git_state()
    recorded = _recorded_runs(result)
    per_run: list[dict[str, Any]] = []
    for run in recorded:
        cert_path = _certificate_path(spec, run["index"])
        raw_cert = get(cert_path)
        if raw_cert is None:
            wire = {"kind": "none"}
        else:
            try:
                wire = json.loads(raw_cert)
            except ValueError as exc:
                wire = {"kind": "unparseable", "error": str(exc)}
            if not isinstance(wire, dict):
                wire = {"kind": "unparseable", "error": "not a JSON object"}
        cert, verified, cairn = _verify_one(to_runner_certificate(wire), local_commit)
        advisory = run.get("verification")
        disagreement = None
        if isinstance(advisory, dict) and cert.get("kind") in CLAIM_CERTIFICATE_KINDS:
            worker_says = advisory.get("status")
            if worker_says in ("verified", "refuted"):
                disagreement = (worker_says == "verified") != verified
        cert_sha_matches = None
        if isinstance(advisory, dict) and advisory.get("certificate_sha256"):
            cert_sha_matches = (by_path.get(cert_path, {}).get("sha256")
                                == advisory["certificate_sha256"])
        per_run.append({"index": run["index"], "certificate": cert,
                        "worker_certificate_sha256_matches": cert_sha_matches,
                        "certificate_submitted": wire if raw_cert is not None else None,
                        "verified": verified, "cairn_cross_check": cairn,
                        "worker_verification": advisory,
                        "worker_verification_disagrees": disagreement})

    if not per_run:
        cert, verified, cairn = _verify_one({"kind": "none"}, local_commit)
    elif len(per_run) == 1:
        cert, verified, cairn = (per_run[0]["certificate"], per_run[0]["verified"],
                                 per_run[0]["cairn_cross_check"])
    else:
        kinds = {p["certificate"].get("kind") for p in per_run}
        if len(kinds) != 1:
            raise BridgeError(f"repetitions carry different certificate kinds "
                              f"{sorted(map(str, kinds))}; one run package cannot "
                              f"summarise them")
        verified = all(p["verified"] for p in per_run)
        verifiers = sorted({str(p["certificate"].get("verifier")) for p in per_run})
        failing = [f"run-{p['index']}" for p in per_run if not p["verified"]]
        cert = {"kind": kinds.pop(), "verified": verified,
                "verifier": verifiers[0] if len(verifiers) == 1 else verifiers,
                "verifier_commit": local_commit,
                **({"failing_checks": failing} if failing else {}),
                "per_run": [p["certificate"] for p in per_run]}
        cairn = None

    status, valid, invalid_reason = _base_status(result)
    if result["outcome_class"] == "completed":
        status, valid, invalid_reason = apply_certificate_verdict(
            status, valid, invalid_reason, cert, verified)
    elif cert.get("kind") in CLAIM_CERTIFICATE_KINDS and not verified:
        invalid_reason += " A certificate was present and failed independent verification."

    # Wrapper-measured timing: the worker's parent-clock wall time and wait4
    # rusage of each timed execution. Nothing here is caller-supplied.
    timing = result["timing"]
    wall = (round(sum(r["wall_seconds"] for r in recorded), 6) if recorded else None)
    peak_rss = (max(r["max_rss_kb"] for r in recorded) * 1024 if recorded else None)
    cpu = (round(sum(r["user_cpu_seconds"] + r["sys_cpu_seconds"] for r in recorded), 6)
           if recorded else None)

    env = result.get("environment") or {}
    worker = result.get("worker") or {}
    src = result["source"]
    resolved = src.get("resolved_commit")
    command = shlex.join(spec["command"]["argv"])
    advisory_rollup = result.get("verification")

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": exp_id,
            "status": status,
            "code": {
                "commit": resolved or src.get("commit"),
                "dirty": False if resolved else None,
                "command": command,
                "source": {
                    "pinned_by": "commit",
                    "files": {},
                    "file_count": 0,
                    "all_pinned": bool(resolved),
                    "all_clean": None,
                    "note": (
                        "Executed by a taskq worker at the pinned commit: the "
                        "worker ran `git reset --hard <commit>` and verified "
                        "`rev-parse HEAD`, so every tracked file is exactly that "
                        "commit. taskq v1 reuses worktrees and does not record "
                        "untracked files in them, so all_clean is not asserted."
                        if resolved else
                        "The worker never resolved the commit (infrastructure "
                        "failure before checkout); `commit` is the requested one "
                        "and no code ran."),
                },
                "untracked": None,
            },
            "inference": runner._inference_block(),
            "environment": {
                "operating_system": env.get("platform"),
                "architecture": env.get("machine"),
                "python_version": env.get("python"),
                "sage_version": None,
                "dependencies": {},
            },
            "inputs": dict(inputs) if inputs is not None else
                      {"curve_id": None, "seed": None, "parameters": {}},
            "timing": {
                "started_at": runner._iso(timing["started_at"]),
                "finished_at": runner._iso(timing["finished_at"]),
                "wall_seconds": wall,
                "timing_source": "taskq-worker",
                "queued_at": runner._iso(timing["queued_at"]),
                "setup_wall_seconds": timing.get("setup_wall_seconds"),
            },
            "resources": {"peak_rss_bytes": peak_rss, "cpu_seconds": cpu},
            "result": {
                "metrics": (recorded[0].get("metrics") or {}) if len(recorded) == 1
                           else {"per_run": [r.get("metrics") for r in recorded],
                                 "summary": result.get("summary")},
                "valid": valid,
                "invalid_reason": invalid_reason,
                "certificate": certificate_summary(cert, cairn),
            },
            "taskq": {
                "task_id": result["task_id"],
                "attempt": result["attempt"],
                "fence": result["fence"],
                "spec_sha256": digest,
                "queue": spec.get("queue"),
                "idempotency_key": spec.get("idempotency_key"),
                "status": result["status"],
                "outcome_class": result["outcome_class"],
                "error": result.get("error"),
                "worker": {"id": worker.get("id"), "hostname": worker.get("hostname"),
                           "labels": worker.get("labels")},
                "source": {"repo": src.get("repo"), "commit": src.get("commit"),
                           "resolved_commit": resolved},
                "infra_failures": len((task_meta or {}).get("infra_failures") or []),
                "logs_truncated": truncated,
                "artifacts_used": used,
                "artifacts": [{k: a.get(k) for k in ("path", "sha256", "bytes")}
                              for a in result.get("artifacts", [])],
                "worker_verification": {
                    "authority": "advisory; this repo's runner verification decides",
                    "rollup": advisory_rollup,
                    "disagrees_with_repo_verifier": [
                        p["index"] for p in per_run if p["worker_verification_disagrees"]],
                },
            },
            "artifacts": {
                "command": "command.txt",
                "environment": "environment.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "raw_result": "raw-result.json",
            },
        }
    }

    raw = {
        "metrics": manifest["run"]["result"]["metrics"],
        "certificate": cert,
        "raw": {
            "summary": result.get("summary"),
            "runs": result.get("runs", []),
            "setup": result.get("setup", []),
            "certificates": [{k: p[k] for k in (
                "index", "certificate_submitted", "worker_verification",
                "worker_verification_disagrees",
                "worker_certificate_sha256_matches")} for p in per_run],
            "taskq_result": result,
            "taskq_spec": spec,
        },
    }

    os.makedirs(run_dir)
    runner._write(run_dir, "manifest.yaml", yaml.safe_dump(manifest, sort_keys=False))
    runner._write(run_dir, "command.txt", _command_text(spec, result))
    runner._write(run_dir, "environment.json",
                  json.dumps({**env, "worker": worker}, indent=2, sort_keys=True))
    runner._write(run_dir, "stdout.log", logs["stdout"])
    runner._write(run_dir, "stderr.log", logs["stderr"])
    runner._write(run_dir, "raw-result.json",
                  json.dumps(raw, indent=2, sort_keys=True, default=str))
    return run_dir


def package_task(task_id: str, exp_dir: str, run_id: str, *,
                 artifact_fetch: ArtifactFetch = uri_fetch, store: Any = None,
                 inputs: dict[str, Any] | None = None) -> str:
    """Fetch a finished task from the queue and write its run package."""
    task, result = fetch(task_id, store)
    if task is None:
        raise BridgeError(f"no such task {task_id}")
    if result is None:
        raise BridgeError(f"task {task_id} is {task.get('state')}; no result yet")
    return write_run_package(result, task["spec"], task, exp_dir, run_id,
                             artifact_fetch, inputs=inputs)
