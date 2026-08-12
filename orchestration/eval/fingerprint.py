"""What produced this eval result.

A score is only useful for tuning if you can say what it was a score *of*. The
tunable surface of this harness is spread across several files -- the role
contracts in `agents/`, the capability and command allow-lists in
`orchestration/roles.yaml`, the policy requirements, the model bindings, the
suite itself -- and a result that records none of them cannot be attributed to
a change.

So every eval record carries a fingerprint: the git commit, whether the tree
was dirty, and a content hash of each input that can move a score. Two results
with the same fingerprint should be comparable; two with different fingerprints
differ by something you can look up.

`changed_between()` turns that into the question actually worth asking after a
tuning round: what did I change, and did it help.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]

# Everything whose content can move an eval score. Adding a tunable input here
# is what keeps "we tuned it and it improved" checkable rather than folkloric.
TRACKED = [
    "AGENTS.md",
    "agents/coordinator.md",
    "agents/executor.md",
    "agents/idea-generator.md",
    "agents/red-team.md",
    "agents/validator.md",
    "orchestration/roles.yaml",
    "orchestration/model-policies.yaml",
    "orchestration/model-bindings.yaml",
    "orchestration/providers.yaml",
]


def _sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _git(*args: str, repo: Path = REPO) -> str:
    try:
        return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                              text=True, timeout=15).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def harness_fingerprint(*, repo: Path = REPO, suite_path: str | None = None,
                        config_digest: str | None = None) -> dict[str, Any]:
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no", repo=repo))
    inputs = {name: _sha(repo / name) for name in TRACKED}
    if suite_path:
        inputs[str(suite_path)] = _sha(Path(suite_path))
    return {
        "git_commit": _git("rev-parse", "HEAD", repo=repo) or "unknown",
        "git_dirty": dirty,
        "config_digest": config_digest,
        "inputs": inputs,
        # One value to compare when you only care whether anything moved.
        "digest": "sha256:" + hashlib.sha256(
            "".join(f"{k}={v}" for k, v in sorted(inputs.items())).encode()
        ).hexdigest()[:16],
    }


def changed_between(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    """Which tunable inputs differ between two eval records."""
    old, new = before.get("inputs") or {}, after.get("inputs") or {}
    changed = [name for name in sorted(set(old) | set(new))
               if old.get(name) != new.get(name)]
    if before.get("git_commit") != after.get("git_commit") and not changed:
        changed.append("(commit differs, no tracked input changed)")
    return changed


def describe(fingerprint: dict[str, Any]) -> str:
    commit = str(fingerprint.get("git_commit", "unknown"))[:10]
    dirty = "  DIRTY TREE — result not attributable to a commit" if fingerprint.get(
        "git_dirty") else ""
    return f"{commit} inputs={fingerprint.get('digest', '?')}{dirty}"
