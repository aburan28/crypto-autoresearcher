#!/usr/bin/env python3
"""
RED TEAM TASK-20260815-85e02a -- probe0_notarization_and_arithmetic_check.py

Two independent, cheap checks, both required by this task's own
completion_gate:

(1) Notarization chain, checked in BOTH directions with git plumbing
    (matching the Validator's own required check): ancestry of the
    snapshot commit and the self-referential follow-up commit relative to
    HEAD; absence of every producer path at the declared parent; presence
    at the snapshot commit; the exact changed-path-set at both commits;
    independent sha256 recomputation of all 11 producer artifacts against
    run_manifest.yaml's own declared artifact_sha256 map (bypassing
    snapshot-receipt.json's own arithmetic entirely -- recomputed directly
    from `git show <sha>:<path>`).

(2) Independent re-derivation of this task's own total-wall-clock
    arithmetic, because run_manifest.yaml's own prose figure
    ("2662.76s + 4080.23s = 6742.99s") and writeup.md's own headline figure
    ("~4779s") were found, on inspection, to disagree with each other and
    with the run's own recorded run_start_utc.txt/run_end_utc.txt span.
    This probe recomputes all three quantities from the raw, committed
    JSON fields and timestamps directly, with no manual arithmetic taken
    on faith.

Read-only with respect to every committed artifact this probe inspects;
writes only inside this red-team task's own write_scope.
"""
import datetime
import hashlib
import json
import subprocess

REPO = "/home/user/crypto-autoresearcher"
SNAPSHOT_SHA = "71d62ecc6fbae1762f0f14a510d195cd7dabf803"
PARENT_SHA = "0ff467762ff82033de94bcd595105af3eb56e76b"
FOLLOWUP_SHA = "186980fdf59466cffdcac5964484df6e5e8d5e85"  # current HEAD, per task card
TASK_DIR = "coordination/goals/GOAL-MLKEM-005/batches/BATCH-279acb/tasks/TASK-20260815-6e4c02"

PRODUCER_PATHS = [
    "stage0_d512_precision_bisection_and_reattempt.py",
    "bisection_d512_results.json",
    "main_grid_d512_reattempt_results.json",
    "writeup.md",
    "command.txt",
    "stdout.log",
    "stderr.log",
    "run_manifest.yaml",
    "environment.json",
    "run_start_utc.txt",
    "run_end_utc.txt",
]

DECLARED_HASHES = {
    "stage0_d512_precision_bisection_and_reattempt.py": "785bb4e30e79ac73cf2ec7358e28618c780e13589ea839625cdfb3951ad9f059",
    "bisection_d512_results.json": "1bc241b896ad44910498585a216c7711fb1c5749534e6d603e2b663be2f11534",
    "main_grid_d512_reattempt_results.json": "ab72fd00b5bc956624499c90811cb40662845ab82cf03c8704e0e9201aa6fd30",
    "writeup.md": "e15355592e49f4b0641f9bfd37f91ee1a2f6b26b00f7fe3cb0e4492ef29af52d",
    "command.txt": "ac37cbc2fb0a3578facbda8e2fbb89d2fe61c4ecb5b860c4580efe1e3214739d",
    "stdout.log": "b92e0611183a5f5e8ec194b48065ea64abdae3c4329cab21252e9538aae0b3d8",
    "stderr.log": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "run_manifest.yaml": "4dcfaffd937227196a446e7bcf86bf5b002c502bdc1b3d7a9e44f10c9e3612e5",
    "environment.json": "d21b42441e32992ffe2a2456c01bf19c71df0b4e61d3577806d114da5b935f79",
    "run_start_utc.txt": "189c49e0936e77b83ef3d3e9f9755935ec16ab799153566a5278e7849602afcd",
    "run_end_utc.txt": "1072d930e103f189cc0da00844bef5034b2c00682de177a75fe87a734ff240ac",
}


def sh(*args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True)


def check_notarization():
    out = {}

    r = sh("git", "merge-base", "--is-ancestor", SNAPSHOT_SHA, "HEAD")
    out["snapshot_is_ancestor_of_HEAD"] = (r.returncode == 0)

    r = sh("git", "rev-parse", f"{SNAPSHOT_SHA}^")
    out["snapshot_parent_actual"] = r.stdout.strip()
    out["snapshot_parent_matches_declared"] = (r.stdout.strip() == PARENT_SHA)

    r = sh("git", "diff-tree", "--no-commit-id", "--name-status", "-r", SNAPSHOT_SHA)
    changed = [line.split("\t") for line in r.stdout.strip().splitlines() if line]
    out["snapshot_commit_changed_paths"] = changed
    out["snapshot_commit_n_changed_paths"] = len(changed)
    out["snapshot_commit_all_additions"] = all(s == "A" for s, _ in changed)

    r = sh("git", "rev-parse", f"{FOLLOWUP_SHA}^")
    out["followup_parent_actual"] = r.stdout.strip()
    out["followup_parent_is_snapshot"] = (r.stdout.strip() == SNAPSHOT_SHA)
    r = sh("git", "diff-tree", "--no-commit-id", "--name-status", "-r", FOLLOWUP_SHA)
    out["followup_commit_changed_paths"] = [
        line.split("\t") for line in r.stdout.strip().splitlines() if line
    ]

    r = sh("git", "log", "--all", "--oneline", "--", f"{TASK_DIR}/")
    out["all_commits_touching_task_dir"] = r.stdout.strip().splitlines()

    absence = {}
    for p in PRODUCER_PATHS:
        full = f"{TASK_DIR}/{p}"
        r = sh("git", "show", f"{PARENT_SHA}:{full}")
        absence[p] = {
            "absent_at_parent": (r.returncode != 0),
            "stderr": r.stderr.strip()[:200],
        }
    out["absence_at_parent_check"] = absence

    hash_check = {}
    for p in PRODUCER_PATHS:
        full = f"{TASK_DIR}/{p}"
        r = subprocess.run(
            ["git", "show", f"{SNAPSHOT_SHA}:{full}"], cwd=REPO, capture_output=True
        )
        computed = hashlib.sha256(r.stdout).hexdigest()
        declared = DECLARED_HASHES[p]
        hash_check[p] = {"computed": computed, "declared": declared, "match": computed == declared}
    out["independent_hash_recomputation"] = hash_check
    out["all_hashes_match"] = all(v["match"] for v in hash_check.values())

    return out


def check_arithmetic():
    out = {}

    r = subprocess.run(
        ["git", "show", f"{SNAPSHOT_SHA}:{TASK_DIR}/run_start_utc.txt"],
        cwd=REPO, capture_output=True, text=True,
    )
    start_s = r.stdout.strip()
    r = subprocess.run(
        ["git", "show", f"{SNAPSHOT_SHA}:{TASK_DIR}/run_end_utc.txt"],
        cwd=REPO, capture_output=True, text=True,
    )
    end_s = r.stdout.strip()
    start = datetime.datetime.fromisoformat(start_s.replace("Z", "+00:00"))
    end = datetime.datetime.fromisoformat(end_s.replace("Z", "+00:00"))
    outer_span = (end - start).total_seconds()
    out["run_start_utc"] = start_s
    out["run_end_utc"] = end_s
    out["outer_wall_clock_span_seconds_recomputed"] = outer_span

    r = subprocess.run(
        ["git", "show", f"{SNAPSHOT_SHA}:{TASK_DIR}/bisection_d512_results.json"],
        cwd=REPO, capture_output=True, text=True,
    )
    bisection = json.loads(r.stdout)
    r = subprocess.run(
        ["git", "show", f"{SNAPSHOT_SHA}:{TASK_DIR}/main_grid_d512_reattempt_results.json"],
        cwd=REPO, capture_output=True, text=True,
    )
    main_grid = json.loads(r.stdout)

    bisection_wall_clock = bisection["bisection_wall_clock_seconds"]
    bisection_trials_sum = sum(t["subprocess_wall_clock_seconds"] for t in bisection["trials"])
    out["bisection_wall_clock_seconds_field"] = bisection_wall_clock
    out["bisection_trials_sum_independently_recomputed"] = bisection_trials_sum
    out["bisection_field_matches_trial_sum"] = abs(bisection_wall_clock - bisection_trials_sum) < 1.0
    out["bisection_n_trials_actual"] = len(bisection["trials"])
    out["bisection_n_trials_writeup_claims"] = 8
    out["bisection_trial_count_matches_writeup_claim"] = (len(bisection["trials"]) == 8)

    reattempt_cells_sum = sum(
        c["subprocess_wall_clock_seconds"] for c in main_grid["main_grid"]
    )
    internal_total = main_grid["total_script_wall_clock_seconds"]
    out["main_grid_reattempt_cells_sum_independently_recomputed"] = reattempt_cells_sum
    out["main_grid_json_own_total_script_wall_clock_seconds_field"] = internal_total
    out["internal_total_equals_bisection_plus_reattempt_INCLUSIVE"] = abs(
        internal_total - (bisection_wall_clock + reattempt_cells_sum)
    ) < 1.0

    manifest_claimed_total = 2662.76 + 4080.23  # run_manifest.yaml's own stated arithmetic, verbatim
    out["run_manifest_yaml_own_claimed_total_seconds"] = manifest_claimed_total
    out["run_manifest_double_counts_bisection_phase_by_seconds"] = (
        manifest_claimed_total - internal_total
    )
    out["run_manifest_double_count_equals_bisection_cost"] = abs(
        (manifest_claimed_total - internal_total) - bisection_wall_clock
    ) < 5.0

    out["writeup_md_own_claimed_total_seconds"] = 4779
    out["writeup_md_overstates_true_outer_span_by_seconds"] = 4779 - outer_span
    out["writeup_overstatement_equals_WRITE_BUFFER_SECONDS_600"] = (
        (4779 - outer_span) == 600.0
    )

    out["ground_truth_total_wall_clock_seconds"] = outer_span
    out["ground_truth_source"] = (
        "run_start_utc.txt to run_end_utc.txt, the only two timestamps that "
        "bound the actual OS process from outside; internal JSON fields "
        "(total_script_wall_clock_seconds=%.2fs) are %.1fs less, consistent "
        "with Python/subprocess/import startup overhead before t_script_start "
        "was set." % (internal_total, outer_span - internal_total)
    )

    return out


def main():
    result = {
        "notarization_chain": check_notarization(),
        "arithmetic_check": check_arithmetic(),
    }
    print(json.dumps(result, indent=2, default=str))
    with open("probe0_notarization_and_arithmetic_results.json", "w") as f:
        json.dump(result, f, indent=2, default=str)


if __name__ == "__main__":
    main()
