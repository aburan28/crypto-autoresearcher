#!/usr/bin/env python3
"""Reader costmodel (SHF-20261021-477d51): sha256 of every source this reader read.
On-disk files of the crypto checkout (sparse, at b4f056101) are hashed from disk after
checking they equal the committed blob; off-checkout files are hashed from
`git show b4f056101:<path>` (read-only git). Prints JSON."""
import hashlib, json, subprocess, sys, pathlib
CRYPTO = pathlib.Path("/home/user/crypto"); AR = pathlib.Path("/home/user/crypto-autoresearcher")
REV = "b4f056101"
disk = ["AGENTS.md",
        "research/ic_planner_validation_20261020/PROTOCOL.md",
        "research/ic_planner_validation_20261020/PROTOCOL_AMENDMENT_1.md",
        "research/ic_planner_validation_20261020/README.md",
        "research/ic_planner_validation_20261020/REPORT.typ",
        "research/ic_planner_validation_20261020/analysis/summary.json",
        "research/ic_planner_validation_20261020/analysis/table-r24.txt",
        "research/ic_planner_validation_20261020/analysis/band-r24.txt",
        "research/ic_planner_validation_20261020/scripts/summary.sh",
        "research/ic_planner_validation_20261020/scripts/summary.jq",
        "src/cryptanalysis/ic_framework/planner.rs",
        "src/bin/ic/plan.rs",
        "src/bin/ic/bench.rs",
        "src/cryptanalysis/ecbench/band.rs",
        "src/cryptanalysis/ecbench/full_price.rs",
        "src/cryptanalysis/ecbench/methods.rs",
        "docs/ic/LEADERBOARD.md",
        "docs/ic/leaderboard.json",
        "docs/ic/progress-timeline.json",
        "docs/index-calculus-scoreboard.html",
        "docs/ic-leaderboard.html",
        "docs/ic/dashboard-overview-data.json",
        "scripts/build_ic_leaderboard.py"]
for c in ["r24", "r26", "r28", "c24", "c28", "c30"]:
    disk += [f"research/ic_planner_validation_20261020/specs/{c}.json",
             f"research/ic_planner_validation_20261020/sessions/{c}/spec.json",
             f"research/ic_planner_validation_20261020/sessions/{c}/records.jsonl",
             f"research/ic_planner_validation_20261020/analysis/band-{c}.json"]
    disk += sorted(str(p.relative_to(CRYPTO)) for p in (CRYPTO / f"research/ic_planner_validation_20261020/sessions/{c}/comparisons").glob("*.json"))
blobs = ["research/ecbench_rootfinding_batchtable_20261013/followup/reports/holdout/REPORT.md",
         "research/ecbench_rootfinding_batchtable_20261013/followup/reports/sweep/REPORT.md",
         "research/ic_oracle_setup_blocked_20261020/README.md",
         "research/ic_oracle_setup_blocked_20261020/sessions/A-1k-8k/comparisons/rho-neg__blocked-1024.json",
         "research/ic_oracle_setup_blocked_20261020/analysis/table-A.md",
         "research/ic_linalg_pipeline_20261019/README.md",
         "research/la_engines_20261014/README.md",
         "research/la_engines_20261014/summary.json",
         "research/ecbench_rootfind_engine_20261012/README.md",
         "research/notes/index-calculus/RESEARCH_GLV_INVARIANT_FACTOR_BASES.md",
         "research/ecbench_frobenius_orbit_vs_rho_20261014/README.md",
         "research/ecbench_frobenius_orbit_vs_rho_20261014/PROTOCOL.md"]
ar = ["docs/agent-runtime-core.md", "agents/red-team.md", "docs/sheriff.md"]
out = []
def git_blob(path, rev=REV):
    return subprocess.run(["git", "-C", str(CRYPTO), "show", f"{rev}:{path}"], capture_output=True, check=True).stdout
for p in disk:
    b = (CRYPTO / p).read_bytes()
    same = b == git_blob(p)
    out.append({"path": f"crypto:{p}", "sha256": hashlib.sha256(b).hexdigest(), "how": "read from sparse checkout at b4f056101" + ("" if same else " (DIFFERS FROM BLOB)")})
for p in blobs:
    out.append({"path": f"crypto:{p}", "sha256": hashlib.sha256(git_blob(p)).hexdigest(), "how": "git show b4f056101:<path> (off sparse checkout)"})
for p in ar:
    out.append({"path": f"crypto-autoresearcher:{p}", "sha256": hashlib.sha256((AR / p).read_bytes()).hexdigest(), "how": "read (role contract / checklist)"})
json.dump(out, sys.stdout, indent=1)
