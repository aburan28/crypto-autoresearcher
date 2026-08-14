#!/usr/bin/env python3
"""TASK-20260813-59c321 (Validator) -- probe 1 of 4.

GIT PLUMBING, RUN IN THIS WORKTREE, ACCEPTING NO COORDINATOR CLAIM.

Checks, all with `git` plumbing commands whose exact argv is recorded in the
output:

  A. change-set equality on BOTH archive commits: the commit's change set
     equals its DECLARED set (own artifact_paths UNION source-task
     artifact_paths), with 0 extra and 0 missing, and both counts reported.
  B. the notarization chain in BOTH directions:
       - prereg.md ABSENT at the notarizing commit's parent 5f1ed1e8f
       - prereg.md PRESENT at 60ac81998 with the declared sha256
       - ZERO producer files at 60ac81998
       - `git log --all --follow -- prereg.md` returns EXACTLY ONE commit
       - ancestry asserted against the NOTARIZING COMMIT ITSELF
  C. every producer artifact FIRST APPEARS at 4e466c6bf (absent at its parent,
     exactly one commit on every ref).
  D. declared path_sha256 in each archive block == git blob content at the
     commit == working-tree content (so a working-tree read is a committed read).
  E. dirty-tree state of the producer paths right now.

Writes exactly one file: its --out path.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from collections import OrderedDict

ROOT = "/home/user/crypto-autoresearcher"
QUEUE = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/"
         "dispatch_queue.json")
PREREG = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/tasks/"
          "TASK-20260813-25cb95/prereg.md")
PREREG_SHA_DECLARED = ("6c7c0800f0fdd94f62443262e5283aad"
                       "c2149bad97d377634581d7aceba405ed")
NOTARIZE = "60ac819982793e8ed402bc3b2f4b7ad1b1824f92"
NOTARIZE_PARENT = "5f1ed1e8f209f5fa3f0bb3c2b05d7ae35f940280"
PRODUCER = "4e466c6bf221ea002fe84311baccdb816081a8cd"

ARCHIVES = [
    ("TASK-20260813-502381", ["TASK-20260813-25cb95"], 3),
    ("TASK-20260813-48240d", ["TASK-20260813-2ce014"], 11),
]

CMDS = []


def git(*args):
    argv = ["git", "-C", ROOT] + list(args)
    p = subprocess.run(argv, capture_output=True, text=True)
    CMDS.append({"argv": argv, "returncode": p.returncode})
    return p


def git_ok(*args):
    p = git(*args)
    if p.returncode != 0:
        raise RuntimeError("git failed: %s\n%s" % (args, p.stderr))
    return p.stdout


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def blob_sha256_at(commit, path):
    p = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, path)],
                       capture_output=True)
    CMDS.append({"argv": ["git", "-C", ROOT, "show", "%s:%s" % (commit, path)],
                 "returncode": p.returncode})
    if p.returncode != 0:
        return None
    return sha256_bytes(p.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    R = OrderedDict()
    R["probe"] = "probe_git_chain.py"
    R["task_id"] = "TASK-20260813-59c321"
    R["role"] = "validator"
    R["worktree"] = ROOT
    R["head"] = git_ok("rev-parse", "HEAD").strip()
    R["branch"] = git_ok("rev-parse", "--abbrev-ref", "HEAD").strip()

    queue = json.load(open("%s/%s" % (ROOT, QUEUE)))
    T = {t["id"]: t for t in queue["tasks"]}

    # ---------------------------------------------------------------- A
    arch = OrderedDict()
    for aid, sources, expect in ARCHIVES:
        task = T[aid]
        declared = list(task["artifact_paths"])
        for s in sources:
            for p in T[s]["artifact_paths"]:
                if p not in declared:
                    declared.append(p)
        blk = task["archive"]
        sha = blk["commit_sha"]
        changed = [x for x in
                   git_ok("diff-tree", "--no-commit-id", "--name-only", "-r",
                          sha).splitlines() if x]
        ds, cs = set(declared), set(changed)
        parents = git_ok("rev-list", "--parents", "-n", "1", sha).split()
        # declared hashes vs blob at commit vs working tree
        hashchk = OrderedDict()
        for p, h in blk["path_sha256"].items():
            at_commit = blob_sha256_at(sha, p)
            try:
                wt = sha256_bytes(open("%s/%s" % (ROOT, p), "rb").read())
            except OSError:
                wt = None
            hashchk[p] = {
                "declared": h, "blob_at_commit": at_commit,
                "working_tree": wt,
                "declared_eq_blob": at_commit == h,
                "blob_eq_working_tree": at_commit == wt,
            }
        arch[aid] = OrderedDict([
            ("commit_sha", sha),
            ("declared_parent", blk["parent_sha"]),
            ("actual_parents", parents[1:]),
            ("parent_matches", parents[1:] == [blk["parent_sha"]]),
            ("n_declared", len(declared)),
            ("n_declared_expected_by_queue", expect),
            ("n_changed", len(changed)),
            ("extra_in_commit_not_declared", sorted(cs - ds)),
            ("missing_declared_not_in_commit", sorted(ds - cs)),
            ("n_extra", len(cs - ds)),
            ("n_missing", len(ds - cs)),
            ("EQUALITY", len(cs - ds) == 0 and len(ds - cs) == 0
             and len(declared) == expect and len(changed) == expect),
            ("declared_paths", sorted(declared)),
            ("changed_paths", sorted(changed)),
            ("path_sha256_checks", hashchk),
            ("all_declared_hashes_match_blob",
             all(v["declared_eq_blob"] for v in hashchk.values())),
            ("all_blobs_match_working_tree",
             all(v["blob_eq_working_tree"] for v in hashchk.values())),
            ("reachable_from_head",
             git("merge-base", "--is-ancestor", sha, "HEAD").returncode == 0),
            ("commit_message_first_line",
             git_ok("log", "-1", "--format=%s", sha).strip()),
        ])
    R["A_change_set_equality"] = arch

    # ---------------------------------------------------------------- B
    p_parent = git("cat-file", "-e", "%s:%s" % (NOTARIZE_PARENT, PREREG))
    p_notar = git("cat-file", "-e", "%s:%s" % (NOTARIZE, PREREG))
    follow = [ln for ln in git_ok("log", "--all", "--follow", "--format=%H",
                                  "--", PREREG).splitlines() if ln]
    notar_changed = [x for x in
                     git_ok("diff-tree", "--no-commit-id", "--name-only", "-r",
                            NOTARIZE).splitlines() if x]
    producer_dir = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/"
                    "tasks/TASK-20260813-2ce014/")
    prod_at_notar = [x for x in notar_changed if x.startswith(producer_dir)]
    # also: anything at the notarizing commit that is not one of the 3 paths
    R["B_notarization_both_directions"] = OrderedDict([
        ("prereg_absent_at_parent_5f1ed1e8f", p_parent.returncode != 0),
        ("prereg_present_at_60ac81998", p_notar.returncode == 0),
        ("prereg_sha256_at_60ac81998", blob_sha256_at(NOTARIZE, PREREG)),
        ("prereg_sha256_declared", PREREG_SHA_DECLARED),
        ("prereg_sha256_matches",
         blob_sha256_at(NOTARIZE, PREREG) == PREREG_SHA_DECLARED),
        ("prereg_sha256_working_tree",
         sha256_bytes(open("%s/%s" % (ROOT, PREREG), "rb").read())),
        ("sidecar_txt_content",
         git_ok("show", "%s:%s" % (NOTARIZE, PREREG.replace(
             "prereg.md", "prereg_sha256.txt"))).strip()),
        ("git_log_all_follow_commits", follow),
        ("git_log_all_follow_count", len(follow)),
        ("exactly_one_commit_for_frozen_text", len(follow) == 1
         and follow[0] == NOTARIZE),
        ("producer_files_at_notarizing_commit", prod_at_notar),
        ("n_producer_files_at_notarizing_commit", len(prod_at_notar)),
        ("notarizing_commit_change_set", sorted(notar_changed)),
        ("notarizing_commit_is_ancestor_of_producer_commit",
         git("merge-base", "--is-ancestor", NOTARIZE,
             PRODUCER).returncode == 0),
        ("notarizing_commit_is_ancestor_of_head",
         git("merge-base", "--is-ancestor", NOTARIZE, "HEAD").returncode == 0),
        ("producer_commit_is_ancestor_of_head",
         git("merge-base", "--is-ancestor", PRODUCER, "HEAD").returncode == 0),
        ("notarizing_commit_precedes_producer_commit_in_time",
         git_ok("log", "-1", "--format=%cI", NOTARIZE).strip()
         < git_ok("log", "-1", "--format=%cI", PRODUCER).strip()),
        ("notarize_committer_date",
         git_ok("log", "-1", "--format=%cI", NOTARIZE).strip()),
        ("producer_committer_date",
         git_ok("log", "-1", "--format=%cI", PRODUCER).strip()),
    ])

    # ---------------------------------------------------------------- C
    first = OrderedDict()
    prod_paths = sorted(T["TASK-20260813-2ce014"]["artifact_paths"]
                        + T["TASK-20260813-48240d"]["artifact_paths"])
    prod_parent = git_ok("rev-list", "--parents", "-n", "1",
                         PRODUCER).split()[1]
    for p in prod_paths:
        commits = [ln for ln in
                   git_ok("log", "--all", "--format=%H", "--", p).splitlines()
                   if ln]
        first[p] = OrderedDict([
            ("commits_touching_on_every_ref", commits),
            ("n_commits", len(commits)),
            ("absent_at_producer_parent",
             git("cat-file", "-e",
                 "%s:%s" % (prod_parent, p)).returncode != 0),
            ("present_at_producer_commit",
             git("cat-file", "-e", "%s:%s" % (PRODUCER, p)).returncode == 0),
            ("FIRST_APPEARS_AT_4e466c6bf",
             len(commits) == 1 and commits[0] == PRODUCER),
        ])
    R["C_producer_first_appearance"] = OrderedDict([
        ("producer_commit", PRODUCER),
        ("producer_commit_parent", prod_parent),
        ("per_path", first),
        ("ALL_FIRST_APPEAR_AT_PRODUCER_COMMIT",
         all(v["FIRST_APPEARS_AT_4e466c6bf"] for v in first.values())),
    ])

    # ---------------------------------------------------------------- E
    porcelain = [ln for ln in git_ok("status", "--porcelain").splitlines()
                 if ln]
    R["E_worktree_state_now"] = OrderedDict([
        ("git_status_porcelain", porcelain),
        ("producer_paths_dirty",
         [ln for ln in porcelain if "TASK-20260813-2ce014" in ln]),
        ("prereg_dirty", [ln for ln in porcelain if "prereg" in ln]),
        ("validator_own_paths",
         [ln for ln in porcelain if "TASK-20260813-59c321" in ln]),
    ])

    R["git_commands_executed"] = CMDS
    with open(a.out, "w") as f:
        json.dump(R, f, indent=1)

    # ------------------------------------------------------------- stdout
    print("== A. CHANGE-SET EQUALITY ON BOTH ARCHIVES")
    for aid, v in arch.items():
        print("  %s  declared=%d changed=%d extra=%d missing=%d  EQUALITY=%s"
              % (aid, v["n_declared"], v["n_changed"], v["n_extra"],
                 v["n_missing"], v["EQUALITY"]))
        print("     parent_matches=%s  hashes_match_blob=%s  "
              "blob==worktree=%s  reachable_from_HEAD=%s"
              % (v["parent_matches"], v["all_declared_hashes_match_blob"],
                 v["all_blobs_match_working_tree"], v["reachable_from_head"]))
    b = R["B_notarization_both_directions"]
    print("== B. NOTARIZATION, BOTH DIRECTIONS")
    for kk in ("prereg_absent_at_parent_5f1ed1e8f",
               "prereg_present_at_60ac81998", "prereg_sha256_matches",
               "git_log_all_follow_count",
               "exactly_one_commit_for_frozen_text",
               "n_producer_files_at_notarizing_commit",
               "notarizing_commit_is_ancestor_of_producer_commit",
               "notarizing_commit_is_ancestor_of_head",
               "notarizing_commit_precedes_producer_commit_in_time"):
        print("  %-52s %s" % (kk, b[kk]))
    print("  sidecar txt: %s" % b["sidecar_txt_content"][:200])
    c = R["C_producer_first_appearance"]
    print("== C. FIRST APPEARANCE OF EVERY PRODUCER ARTIFACT")
    print("  ALL_FIRST_APPEAR_AT_4e466c6bf = %s  (%d paths)"
          % (c["ALL_FIRST_APPEAR_AT_PRODUCER_COMMIT"], len(c["per_path"])))
    for p, v in c["per_path"].items():
        if not v["FIRST_APPEARS_AT_4e466c6bf"]:
            print("  !! %s -> %s" % (p, v["commits_touching_on_every_ref"]))
    print("== E. WORKTREE STATE NOW")
    print("  dirty producer paths: %s"
          % R["E_worktree_state_now"]["producer_paths_dirty"])
    print("  dirty prereg paths  : %s"
          % R["E_worktree_state_now"]["prereg_dirty"])
    print("  validator own paths : %s"
          % R["E_worktree_state_now"]["validator_own_paths"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
