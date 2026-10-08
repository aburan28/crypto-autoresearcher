"""Keep a run's certificate *statement* on disk, beside its manifest.

`harness/runner.py` verifies a witness in memory and records only its kind
and the verdict in the manifest; the statement itself -- the curve, the
points, the scalar -- was never written anywhere, so no committed run could
be claimed on a cairn objective without being re-run. This module writes it
as `certificate.json` in the run directory.

Why a sidecar and not a line in `write_run`: `harness/runner.py` is pinned by
hash in the locked execution plans (`finite_yaml_locked_v2/v3
ORIGINAL_SOURCE_PINS`) and a test holds the tree to that pin, so a change to
it is a change to a frozen protocol and needs an amendment, not a patch.
`harness/taskq_bridge.py` took the same way around for the same reason. A
driver that wants its witness claimable calls this after `write_run`:

    run_id = write_run(exp_id, area, result, status=..., command=...)
    certificate_sidecar.write_statement(exp_id, run_id, result.certificate)

`tools/exp_to_objective.py artifact` reads the file back. Nothing here is
read by the harness's own verification, which already happened; the file is
a record of what was claimed, for a verifier that is not this program.
"""
from __future__ import annotations

import json
import os
from typing import Any

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILENAME = "certificate.json"


def run_directory(exp_id: str, run_id: str, out_root: str | None = None) -> str:
    """Where `write_run` put the run: the same rule it uses."""
    root = out_root or os.path.join(REPO, "experiments", exp_id)
    return os.path.join(root, "runs", run_id)


def write_statement(exp_id: str, run_id: str, certificate: dict[str, Any] | None,
                    out_root: str | None = None) -> str | None:
    """Write `certificate.json` for a run whose certificate carries a
    statement. Returns the path, or `None` when there is no statement to
    keep (`kind: none`, or a certificate that is only a verdict).

    Refuses to overwrite: a run record is immutable, and a second statement
    for one run id is a different run.
    """
    if not isinstance(certificate, dict):
        return None
    statement = certificate.get("statement")
    if not isinstance(statement, dict):
        return None
    run_dir = run_directory(exp_id, run_id, out_root)
    if not os.path.isdir(run_dir):
        raise FileNotFoundError(f"{run_id}: no run directory at {run_dir}; call write_run first")
    path = os.path.join(run_dir, FILENAME)
    if os.path.exists(path):
        raise FileExistsError(f"{path} exists; run records are immutable")
    payload = {
        "kind": certificate.get("kind"),
        "statement": statement,
        "verified": certificate.get("verified"),
        "verifier": certificate.get("verifier"),
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def read_statement(exp_id: str, run_id: str, out_root: str | None = None) -> dict[str, Any] | None:
    """The statement a run kept, or `None` when it kept none."""
    path = os.path.join(run_directory(exp_id, run_id, out_root), FILENAME)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as handle:
        doc = json.load(handle)
    statement = doc.get("statement") if isinstance(doc, dict) else None
    return statement if isinstance(statement, dict) else None
