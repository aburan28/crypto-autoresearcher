#!/usr/bin/env python3
"""Compare the audited ledger gate with a later complete-tree run."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def advisory_count(line: str) -> int:
    match = re.fullmatch(r"note: (\d+) advisory\(ies\), not failures .*", line)
    require(match is not None, f"unexpected advisory summary: {line}")
    return int(match.group(1))


def main(old_log: Path, new_log: Path, old_commit: str, new_commit: str) -> dict:
    old_raw, new_raw = old_log.read_bytes(), new_log.read_bytes()
    old, new = old_raw.decode().splitlines(), new_raw.decode().splitlines()
    require(old and new and old[0] == new[0] ==
            "FAIL: 162 new validation error(s):", "unexpected gate status")
    require(old[:-1] == new[:-1],
            "validator output changed beyond the final advisory summary")
    errors = [line[4:] for line in new if line.startswith("  - ")]
    require(len(errors) == 162, "error count changed")
    paths = {line.split(": ", 1)[0] for line in errors}
    require(len(paths) == 49, "affected path count changed")
    before, after = advisory_count(old[-1]), advisory_count(new[-1])
    require(before == 543 and after == 545, "unexpected advisory delta")
    return {
        "status": "pass",
        "old_commit": old_commit,
        "new_commit": new_commit,
        "old_log_sha256": hashlib.sha256(old_raw).hexdigest(),
        "new_log_sha256": hashlib.sha256(new_raw).hexdigest(),
        "unsuppressed_error_lines_identical": True,
        "unsuppressed_errors": len(errors),
        "affected_paths": len(paths),
        "old_advisories": before,
        "new_advisories": after,
        "changed_lines": [old[-1], new[-1]],
    }


if __name__ == "__main__":
    require(len(sys.argv) == 5,
            "usage: check_gate_delta.py OLD_LOG NEW_LOG OLD_COMMIT NEW_COMMIT")
    print(json.dumps(main(Path(sys.argv[1]), Path(sys.argv[2]),
                          sys.argv[3], sys.argv[4]), indent=2))
