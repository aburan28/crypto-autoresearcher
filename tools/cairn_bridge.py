#!/usr/bin/env python3
"""The only module in this repository that talks to cairn (distributed-researcher).

Stage 0 of docs/cairn-integration-plan.md: cairn as a second, independently
implemented verifier for certificates this program already claims -- no
objectives funded, no rewards, no ledger writes on this program's side.
`harness/runner.py` calls `score_certificate()` after its own independent
recomputation already passed; a disagreement between the two is a hard
failure (invariant a in the plan), never advisory.

# Opt-in, not a new hard dependency

This adds a Rust toolchain to what CAN be built here, not to what MUST be.
A machine with no cairn binary gets `available() == False` and every run
proceeds exactly as it did before this module existed -- Stage 0 is
additive. What is NOT optional, once cairn IS reachable and answers: a
`reject` where this program's own check said `verified: true` is a real
disagreement and `harness/runner.py` treats it as one. Absence of cairn is
not evidence of anything, same as `unavailable` is not `reject`
(docs/cairn-integration-plan.md invariant b) -- this module's own two
failure shapes, `not installed` and `ran and said unavailable`, are kept
visibly distinct in the return value for exactly that reason.

# Why a bare subprocess call, not the MCP client stack

`cairn-mcp` speaks newline-delimited JSON-RPC on stdio
(distributed-researcher/docs/agents.md, "Driving it without an agent") --
one request in, one response out, then let the process see EOF and exit.
That is the whole integration surface Stage 0 needs, so it is what this
module does, directly, rather than pulling in an MCP client library for a
single round-trip. `score_candidate` is free and RECORDS NOTHING -- the log
is written to at most once per fresh log, by `_ensure_objectives_posted`, to
register the two Stage-0 objectives; every later process reuses those ids
from a small sidecar file next to the log rather than re-posting (see
`_post_new`'s docstring for why the sidecar, and not cairn's own "already
posted" refusal, is what a repeat run trusts).

# Where the log lives

Never inside this repository's tree (docs/cairn-integration-plan.md section
5: this repo is worked by many concurrent worktrees, and cairn is one
writer per log, enforced by an OS lock -- two worktrees sharing a log would
have the second simply refused to open it). Defaults to
`~/.cairn/<worktree-basename>.jsonl`, one file per checkout, override with
`CAIRN_LOG`.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Explicit only -- no sibling-directory autodetection. A guess at where
# distributed-researcher happens to be checked out is exactly the kind of
# ambient, unstated environment dependency this program's own conventions
# refuse elsewhere (AGENTS.md rule 5: never fabricate what was not told to
# you). Point at it or the bridge reports unavailable; nothing in between.
ENV_BIN = "CAIRN_MCP_BIN"
ENV_LOG = "CAIRN_LOG"

DISCRETE_LOG_OBJECTIVE = os.path.join(REPO, "cairn", "objectives", "discrete-log-reverification.json")
DECOMPOSITION_OBJECTIVE = os.path.join(REPO, "cairn", "objectives", "decomposition-reverification.json")

_OBJECTIVE_FILES = {
    "discrete_log": DISCRETE_LOG_OBJECTIVE,
    "decomposition": DECOMPOSITION_OBJECTIVE,
}

# Certificate kinds this bridge can re-verify. harness/runner.py's own
# certificate kinds (docs/claims-and-verification.md) are a superset --
# "none" carries no witness and has nothing for cairn to check either.
SUPPORTED_KINDS = frozenset(_OBJECTIVE_FILES)

_DEFAULT_TIMEOUT_SECONDS = 30

# Per-process memo of objective ids, keyed by (bin, log, root). Posting is
# idempotent on cairn's side (refused as "already posted", never
# double-appended -- verified against a real log before this was written),
# but re-spawning a CLI process to learn that on every single certificate in
# a batch would be pure waste. One provisioning pass per process is enough;
# a fresh process re-derives it from the log, which is the correct behavior
# after a log is deleted or pointed elsewhere.
_provisioned: dict[tuple[str, str, str], dict[str, str]] = {}


class CairnUnavailableError(RuntimeError):
    """cairn could not be reached at all (no binary, or the process failed).

    Distinct from a `verdict: "unavailable"` answer FROM cairn -- that is a
    real response this module returns normally, not an error. This is what
    `score_certificate` raises when there was no answer to return, and
    `available()` is the non-raising way to check for the same condition
    first.
    """


@dataclass(frozen=True)
class CairnVerdict:
    """What cairn's pinned checker said about one artifact.

    `status` is exactly the ledger's own vocabulary (accept | reject |
    unavailable | invalid_spec) -- not reinterpreted, so a caller checking
    `status == "reject"` is checking the same word cairn's own docs and
    `cairn audit` output use.
    """
    status: str
    detail: str
    objective_id: str
    checker_sha256: str | None


def _cairn_mcp_bin() -> str | None:
    configured = os.environ.get(ENV_BIN)
    if configured:
        path = Path(configured)
        return str(path) if path.is_file() and os.access(path, os.X_OK) else None
    found = shutil.which("cairn-mcp")
    return found


def _default_log_path() -> str:
    worktree = os.path.basename(os.path.normpath(REPO)) or "crypto-autoresearcher"
    return str(Path.home() / ".cairn" / f"{worktree}.jsonl")


def _log_path() -> str:
    return os.environ.get(ENV_LOG) or _default_log_path()


def available() -> bool:
    """Whether a Stage 0 cairn re-check can run at all on this machine."""
    return _cairn_mcp_bin() is not None


def _run_cli(bin_path: str, log_path: str, *args: str) -> subprocess.CompletedProcess:
    # The CLI binary sits beside cairn-mcp in the same target/release/ -- one
    # env var covers both, since a build that has one has the other.
    cli_bin = os.path.join(os.path.dirname(bin_path), "cairn")
    if not (os.path.isfile(cli_bin) and os.access(cli_bin, os.X_OK)):
        raise CairnUnavailableError(
            f"{ENV_BIN} points at cairn-mcp but no 'cairn' CLI binary sits beside it "
            f"at {cli_bin}; both come from the same `cargo build --release`."
        )
    return subprocess.run(
        [cli_bin, "--log", log_path, "--root", REPO, *args],
        capture_output=True, text=True, timeout=_DEFAULT_TIMEOUT_SECONDS,
    )


def _sidecar_path(log_path: str) -> Path:
    # Beside the log, not in it and not in the repo: the log is cairn's
    # append-only record and this is purely a local memo of ids this bridge
    # already learned. Losing it costs one re-provisioning pass, never
    # correctness -- it is never the only place an id is recorded, cairn's
    # own log is, and this file is only ever trusted for an id it watched a
    # `post` succeed on in THIS log.
    return Path(f"{log_path}.objective-ids.json")


def _load_sidecar(log_path: str) -> dict[str, str]:
    try:
        return json.loads(_sidecar_path(log_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_sidecar(log_path: str, ids: dict[str, str]) -> None:
    _sidecar_path(log_path).write_text(json.dumps(ids, indent=2, sort_keys=True) + "\n",
                                        encoding="utf-8")


def _post_new(bin_path: str, log_path: str, objective_path: str) -> str:
    """Post an objective this bridge has not seen posted to this log before.

    Trusts only a `post` SUCCESS message for an id -- that message prints the
    full 64-character digest and nothing else claims to. The refusal message
    for an objective already on the log prints a truncated 8-character form
    for a human to eyeball, not the id a caller could safely resubmit
    (confirmed against a real log: parsing it silently produces a *different,
    wrong* objective id that `score_candidate` then can't find at all -- a
    truncated hex prefix is not the same value as the id it is a prefix of).
    So a refusal here is never parsed for an id; it means this log already
    has this objective from before this bridge's sidecar existed, or the
    sidecar was deleted independently of the log, and that is reported as an
    error asking for one of those to be reconciled by hand rather than
    guessed at.
    """
    result = _run_cli(bin_path, log_path, "post", objective_path)
    combined = result.stdout + result.stderr
    if result.returncode == 0:
        for token in combined.split():
            if token.startswith("sha256:") and len(token) == len("sha256:") + 64:
                return token
        raise CairnUnavailableError(f"cairn post produced no objective id: {combined!r}")
    if "already posted" in combined:
        raise CairnUnavailableError(
            f"{objective_path} is already posted to {log_path}, but "
            f"{_sidecar_path(log_path)} has no record of its id -- the sidecar was lost, "
            f"or something else posted to this log first. Delete {log_path} to let this "
            f"bridge re-provision a clean log, or find the id with cairn-mcp's "
            f"list_objectives and add it to the sidecar by hand. Refusal was: "
            f"{combined.strip()!r}"
        )
    raise CairnUnavailableError(f"cairn post {objective_path} failed: {combined.strip()}")


def _ensure_objectives_posted(bin_path: str, log_path: str) -> dict[str, str]:
    key = (bin_path, log_path, REPO)
    cached = _provisioned.get(key)
    if cached is not None:
        return cached
    ids = _load_sidecar(log_path)
    missing = {kind: path for kind, path in _OBJECTIVE_FILES.items() if kind not in ids}
    if missing:
        for kind, path in missing.items():
            ids[kind] = _post_new(bin_path, log_path, path)
        _save_sidecar(log_path, ids)
    _provisioned[key] = ids
    return ids


def _artifact_for(cert: dict[str, Any]) -> dict[str, Any]:
    """The certificate's `statement`, unmodified -- see cairn/checkers/*.py's
    own docstrings for why no translation happens between what this program
    claims and what gets re-checked."""
    statement = cert.get("statement")
    if not isinstance(statement, dict):
        raise ValueError(f"certificate has no statement to re-verify: {cert!r}")
    return statement


def score_certificate(cert: dict[str, Any]) -> CairnVerdict:
    """Re-verify one certificate through cairn's sandboxed checker.

    Raises CairnUnavailableError if cairn cannot be reached at all -- check
    `available()` first if the caller wants to skip rather than fail on a
    machine with no cairn binary. A real response FROM cairn, including
    `unavailable` (missing toolchain, timeout on cairn's side), returns
    normally; that is data, not a bridge failure.
    """
    # Cheap, local, no I/O -- checked before anything that costs a
    # subprocess or touches a log, so a malformed caller fails fast rather
    # than paying for provisioning it was never going to use.
    kind = cert.get("kind")
    if kind not in SUPPORTED_KINDS:
        raise ValueError(
            f"cairn_bridge only re-verifies {sorted(SUPPORTED_KINDS)}, got kind={kind!r}"
        )
    artifact = _artifact_for(cert)

    bin_path = _cairn_mcp_bin()
    if bin_path is None:
        raise CairnUnavailableError(
            f"no cairn-mcp binary: set {ENV_BIN} to a built "
            f"distributed-researcher target/release/cairn-mcp, or leave Stage 0 disabled."
        )
    log_path = _log_path()
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    objective_ids = _ensure_objectives_posted(bin_path, log_path)
    objective_id = objective_ids[kind]

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "score_candidate",
            "arguments": {"objective_id": objective_id, "artifact": artifact},
        },
    }
    try:
        result = subprocess.run(
            [bin_path, "--log", log_path, "--root", REPO],
            input=json.dumps(request) + "\n",
            capture_output=True, text=True, timeout=_DEFAULT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise CairnUnavailableError(f"cairn-mcp timed out scoring: {exc}") from exc

    try:
        response = json.loads(result.stdout.strip().splitlines()[-1])
        text = response["result"]["content"][0]["text"]
    except (IndexError, KeyError, ValueError, json.JSONDecodeError) as exc:
        raise CairnUnavailableError(
            f"cairn-mcp produced no parseable response (exit {result.returncode}); "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        ) from exc

    # First line is "<status>: <detail>"; the rest is the untrusted-text
    # fence and evidence block score_candidate always appends (see the MCP
    # server's own docstring on tainted verifier output). Only the status
    # word and its own one-line detail are read here.
    first_line = text.split("\n", 1)[0]
    status, _, detail = first_line.partition(": ")
    checker_sha256 = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("evidence:"):
            try:
                checker_sha256 = json.loads(line[len("evidence:"):].strip()).get("checker_sha256")
            except json.JSONDecodeError:
                pass
    return CairnVerdict(
        status=status.strip(), detail=detail.strip() or first_line,
        objective_id=objective_id, checker_sha256=checker_sha256,
    )
