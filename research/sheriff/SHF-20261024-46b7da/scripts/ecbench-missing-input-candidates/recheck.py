#!/usr/bin/env python3
"""Check whether tracked scratch specs recover four incomplete ecbench inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


HEAD = "172f84c7b0143ff5b4a26d6d21ffed3bf0f0cf3b"
ECBENCH_SHA256 = "d4916fcb1ba46f8313d83a3776325afee0c0a9b513520730f58b238b62c022a2"
PAIRS = (
    ("research/gaudry_quartic_d4_char2_20261015/pilot/scratch-session-m10",
     "research/gaudry_quartic_d4_char2_20261015/pilot/scratch-spec-m10.json"),
    ("research/gaudry_quartic_d4_char2_20261015/pilot/scratch-session-m5",
     "research/gaudry_quartic_d4_char2_20261015/pilot/scratch-spec-m5.json"),
    ("research/gaudry_quartic_d4_char2_20261015/pilot/scratch-session-m8",
     "research/gaudry_quartic_d4_char2_20261015/pilot/scratch-spec-m8.json"),
    ("research/gaudry_quartic_d4_cost_20261014/pilot/scratch-session",
     "research/gaudry_quartic_d4_cost_20261014/pilot/scratch-spec.json"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(repo: Path) -> dict:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                              text=True).stdout.strip()

    head = git("rev-parse", "HEAD")
    if head != HEAD:
        raise ValueError(f"expected pinned crypto head {HEAD}, got {head}")
    binary = repo / "target/release/ecbench"
    binary_sha256 = sha256(binary)
    if binary_sha256 != ECBENCH_SHA256:
        raise ValueError(f"expected pinned ecbench binary {ECBENCH_SHA256}, got {binary_sha256}")
    names = git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
    host_paths = [p for p in names if "host" in Path(p).name.lower() and p.endswith(".json")]
    missing_hosts = [p for p in host_paths if not (repo / p).is_file()]
    if missing_hosts:
        raise ValueError(f"{len(missing_hosts)} tracked host candidates are not materialized")
    hosts_by_sha = {sha256(repo / p): p for p in host_paths}
    rows = []
    for session_rel, candidate_rel in PAIRS:
        session = json.loads((repo / session_rel / "session.json").read_text())
        candidate = repo / candidate_rel
        plan = json.loads(subprocess.run([str(binary), "plan", "--spec", str(candidate), "--json"],
                                         cwd=repo, check=True, capture_output=True, text=True).stdout)
        row = {
            "session_dir": session_rel,
            "session_id": session["session_id"],
            "candidate_spec": candidate_rel,
            "candidate_spec_file_sha256": sha256(candidate),
            "candidate_spec_id": plan["spec_id"],
            "candidate_spec_sha256": plan["spec_sha256"],
            "session_spec_id": session["spec_id"],
            "session_spec_sha256": session["spec_sha256"],
            "spec_identity_matches": plan["spec_id"] == session["spec_id"] and
                                     plan["spec_sha256"] == session["spec_sha256"],
            "session_host_sha256": session["host_sha256"],
            "tracked_host_candidate": hosts_by_sha.get(session["host_sha256"]),
        }
        rows.append(row)
    return {
        "schema": "sheriff.ecbench-missing-input-candidates/v1",
        "crypto_head": head,
        "ecbench_binary_sha256": binary_sha256,
        "host_search": "tracked files whose basename contains host and ends .json",
        "tracked_host_candidates_scanned": len(host_paths),
        "all_spec_identities_match": all(row["spec_identity_matches"] for row in rows),
        "all_exact_host_candidates_found": all(row["tracked_host_candidate"] for row in rows),
        "sessions": rows,
        "interpretation": "matching canonical specs are recoverable candidates; absent exact host bytes keep sessions input-incomplete",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repo.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{len(result['sessions'])} spec identities match; "
          f"{sum(bool(row['tracked_host_candidate']) for row in result['sessions'])} exact host candidates found")
