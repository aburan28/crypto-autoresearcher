#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM PROBE D  --  TASK-20260809-444fe7 / BATCH-9e3584 / GOAL-MLKEM-005

INDEPENDENT VERIFICATION OF THE COORDINATOR'S CLAIMS ABOUT THE GIT RECORD.

WHY THIS EXISTS.  COORDINATOR-ADJUDICATION-20260811.md section 0 states plainly
that every statement it makes about git is ATTRIBUTED, not verified: "I hold no
shell and ran no git command."  Both COORDINATOR-DEFECT.md files repeat it.
The Red Team card requires the three-way commit split, the 30-for-30 content
match and the D3 dangling-artifact-path table to be verified INDEPENDENTLY,
because a Validator already proved one Coordinator git claim false in this goal
(BATCH-cbe023 F-1).  This probe is that verification, packaged so a later
reader can re-run it rather than trust this report.

It also resolves, rather than inherits, the three facts the adjudication marks
UNKNOWN: whether each archive commit's message contains its task id and
GOAL-MLKEM-005 (research_dispatch.py:1103-1114), and what base commit each
archive recorded.

READ-ONLY.  Only `git cat-file`, `git rev-parse`, `git log`, `git diff-tree`
and `git merge-base` are invoked.  NO write, NO commit, NO index change.
WRITES exactly one file: probe_archive_record.json, beside this script.
CLAIM TIER TOY -- this is bookkeeping verification and adjudicates no
scientific proposition.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import OrderedDict

T0 = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..",
                                          "..", "..", ".."))
BATCH_REL = "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584"

NOTARIZE_COMMIT = "1aa7db53"
PRODUCER_COMMIT = "c034ef38"
RECEIPT_COMMIT = "502d15a0"
NOTARIZE_TASK = "TASK-20260809-91cf76"
PRODUCER_TASK = "TASK-20260809-4d928d"
PRODUCERS = ["TASK-20260809-cda2f6", "TASK-20260809-311784",
             "TASK-20260809-97d6cf", "TASK-20260809-3eb72c"]
PREREG_REL = BATCH_REL + "/tasks/TASK-20260809-4011dd/prereg.md"


def git(*a):
    p = subprocess.run(("git",) + a, cwd=REPO_ROOT, capture_output=True,
                       text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def changed(commit):
    rc, out, _ = git("diff-tree", "--no-commit-id", "--name-only", "-r",
                     commit)
    return sorted(out.split()) if rc == 0 else None


def blob_sha256(commit, path):
    p = subprocess.run(("git", "show", "%s:%s" % (commit, path)),
                       cwd=REPO_ROOT, capture_output=True)
    if p.returncode != 0:
        return None
    return hashlib.sha256(p.stdout).hexdigest()


def file_sha256(path):
    fp = os.path.join(REPO_ROOT, path)
    if not os.path.exists(fp):
        return None
    return hashlib.sha256(open(fp, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe_id"] = "PROBE-D / probe_archive_record"
    R["task_id"] = "TASK-20260809-444fe7"
    R["role"] = "red-team"
    R["batch_id"] = "BATCH-9e3584"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["claim_tier"] = "toy"
    R["status_of_this_artifact"] = (
        "RED TEAM PROBE. Independent re-verification of Coordinator claims "
        "about the git record. Adjudicates no scientific proposition.")
    R["read_only"] = True
    R["HEAD"] = git("rev-parse", "HEAD")[1]

    # ---- (1) the three-way commit split
    split = OrderedDict()
    for label, c in [("notarization", NOTARIZE_COMMIT),
                     ("producer_snapshot", PRODUCER_COMMIT),
                     ("receipts_and_queue", RECEIPT_COMMIT)]:
        rc, full, _ = git("rev-parse", c)
        _, meta, _ = git("log", "-1", "--format=%H|%P|%cI|%s", c)
        anc = git("merge-base", "--is-ancestor", c, "HEAD")[0] == 0
        _, msg, _ = git("log", "-1", "--format=%B", c)
        ch = changed(c)
        split[label] = OrderedDict([
            ("declared_prefix", c),
            ("resolved_sha", full if rc == 0 else None),
            ("parent", meta.split("|")[1] if rc == 0 else None),
            ("committer_date", meta.split("|")[2] if rc == 0 else None),
            ("subject", meta.split("|")[3] if rc == 0 else None),
            ("is_ancestor_of_HEAD", anc),
            ("n_paths_changed", len(ch) if ch is not None else None),
            ("paths_changed", ch),
            ("message_contains_GOAL-MLKEM-005", "GOAL-MLKEM-005" in msg),
        ])
    split["notarization"]["message_contains_its_task_id"] = \
        NOTARIZE_TASK in git("log", "-1", "--format=%B", NOTARIZE_COMMIT)[1]
    split["producer_snapshot"]["message_contains_its_task_id"] = \
        PRODUCER_TASK in git("log", "-1", "--format=%B", PRODUCER_COMMIT)[1]
    R["three_way_commit_split"] = split
    R["three_way_split_VERDICT"] = {
        "receipts ride in a THIRD commit, separate from both artifact commits":
            (BATCH_REL + "/archives/%s/snapshot-receipt.json" % NOTARIZE_TASK
             in (split["receipts_and_queue"]["paths_changed"] or []))
            and (BATCH_REL + "/archives/%s/snapshot-receipt.json" % PRODUCER_TASK
                 in (split["receipts_and_queue"]["paths_changed"] or [])),
        "notarization commit changed exactly 2 paths":
            split["notarization"]["n_paths_changed"] == 2,
        "producer commit changed exactly 28 paths":
            split["producer_snapshot"]["n_paths_changed"] == 28,
        "producer commit's parent IS the notarization commit":
            split["producer_snapshot"]["parent"] ==
            split["notarization"]["resolved_sha"],
    }

    # ---- (2) the 30-for-30 content match, against BLOBS AT THE DECLARED COMMIT
    recs = OrderedDict()
    tot = ok_commit = ok_tree = 0
    mismatches = []
    for task, commit in [(NOTARIZE_TASK, NOTARIZE_COMMIT),
                         (PRODUCER_TASK, PRODUCER_COMMIT)]:
        rp = BATCH_REL + "/archives/%s/snapshot-receipt.json" % task
        rec = json.load(open(os.path.join(REPO_ROOT, rp)))
        arc = rec["archive"]
        ps = arc["path_sha256"]
        per = []
        for path, h in sorted(ps.items()):
            tot += 1
            bh = blob_sha256(commit, path)
            fh = file_sha256(path)
            if bh == h:
                ok_commit += 1
            if fh == h:
                ok_tree += 1
            if bh != h or fh != h:
                mismatches.append({"task": task, "path": path,
                                   "declared": h, "at_commit": bh,
                                   "at_working_tree": fh})
            per.append({"path": path, "declared_sha256": h,
                        "matches_blob_at_declared_commit": bh == h,
                        "matches_working_tree": fh == h})
        cs = set(changed(commit) or [])
        recs[task] = OrderedDict([
            ("receipt_path", rp),
            ("receipt_declares_commit_sha", arc.get("commit_sha")),
            ("receipt_declares_parent_sha", arc.get("parent_sha")),
            ("n_declared_paths", len(ps)),
            ("declared_path_set_EQUALS_commit_change_set", cs == set(ps)),
            ("receipt_is_INSIDE_its_own_declared_commit", rp in cs),
            ("paths", per)])
    R["content_match"] = recs
    R["content_match_VERDICT"] = {
        "total_declared_paths": tot,
        "matching_blob_at_declared_commit": ok_commit,
        "matching_working_tree_at_HEAD": ok_tree,
        "mismatches": mismatches,
        "reading": "The Coordinator's 30-for-30 claim is checked against the "
                   "BLOBS AT THE DECLARED COMMITS, which is strictly stronger "
                   "than checking the working tree."}

    # ---- (3) the D3 dangling-artifact-path table
    q = json.load(open(os.path.join(REPO_ROOT, BATCH_REL,
                                    "dispatch_queue.json")))
    tasks = {t["id"]: t for t in q["tasks"]}
    committed = set(changed(PRODUCER_COMMIT) or [])
    declared = []
    d3 = OrderedDict()
    for p in PRODUCERS:
        ap_ = tasks[p].get("artifact_paths", [])
        declared += ap_
        d3[p] = {"n_declared": len(ap_),
                 "dangling": sorted(x for x in ap_ if x not in committed),
                 "deliverables": tasks[p].get("deliverables")}
    dangling = sorted(x for x in declared if x not in committed)
    undeclared = sorted(x for x in committed if x not in set(declared))
    R["D3_artifact_path_table"] = {
        "per_producer": d3,
        "n_declared_total": len(declared),
        "n_dangling_declared_but_not_committed": len(dangling),
        "dangling_paths": dangling,
        "n_undeclared_committed_but_not_declared": len(undeclared),
        "undeclared_paths": undeclared,
        "any_dangling_path_exists_on_disk":
            sorted(x for x in dangling
                   if os.path.exists(os.path.join(REPO_ROOT, x))),
        "reading": "D3 is a defect of the QUEUE's declared artifact_paths. "
                   "The RECEIPT's path_sha256 map declares the COMMITTED "
                   "names and is internally consistent with its commit; the "
                   "adjudication's phrase 'nine of the 28 declared producer "
                   "artifact paths do not exist' is true of the QUEUE, not of "
                   "the receipt, and this probe separates the two."}

    # ---- (4) the notarization property, re-derived from git
    prereg_sha = file_sha256(PREREG_REL)
    parent = git("rev-parse", "%s^" % NOTARIZE_COMMIT)[1]
    absent_at_parent = git("cat-file", "-e",
                           "%s:%s" % (parent, PREREG_REL))[0] != 0
    _, follow, _ = git("log", "--all", "--follow", "--format=%H", "--",
                       PREREG_REL)
    prod_absent_at_notarizer = []
    for p in PRODUCERS:
        for f in ("run_manifest.yaml", "command.txt"):
            rel = BATCH_REL + "/tasks/%s/%s" % (p, f)
            prod_absent_at_notarizer.append(
                {"path": rel,
                 "absent_at_notarizing_commit":
                     git("cat-file", "-e", "%s:%s"
                         % (NOTARIZE_COMMIT, rel))[0] != 0})
    R["notarization_property"] = {
        "prereg_sha256_at_HEAD": prereg_sha,
        "prereg_sha256_at_notarizing_commit":
            blob_sha256(NOTARIZE_COMMIT, PREREG_REL),
        "prereg_sha256_declared_in_sidecar":
            open(os.path.join(REPO_ROOT, BATCH_REL,
                              "tasks/TASK-20260809-4011dd/prereg_sha256.txt")
                 ).read().split()[0],
        "notarizing_commit_parent": parent,
        "frozen_text_ABSENT_at_parent": absent_at_parent,
        "git_log_all_follow_n_commits": len(follow.split()) if follow else 0,
        "every_producer_artifact_ABSENT_at_notarizing_commit":
            all(x["absent_at_notarizing_commit"]
                for x in prod_absent_at_notarizer),
        "detail": prod_absent_at_notarizer,
        "commits_touching_any_BATCH-9e3584_tasks_path":
            git("log", "--all", "--format=%H", "--",
                BATCH_REL + "/tasks/")[1].split()}

    # ---- (5) the adjudication's three UNKNOWNs, RESOLVED
    R["adjudication_UNKNOWNs_resolved"] = {
        "commit messages contain task id and GOAL-MLKEM-005": {
            NOTARIZE_COMMIT: {
                "task_id": split["notarization"]["message_contains_its_task_id"],
                "goal_id": split["notarization"]["message_contains_GOAL-MLKEM-005"]},
            PRODUCER_COMMIT: {
                "task_id":
                    split["producer_snapshot"]["message_contains_its_task_id"],
                "goal_id":
                    split["producer_snapshot"]["message_contains_GOAL-MLKEM-005"]}},
        "base commit recorded in the commit messages (not in the receipts)": {
            NOTARIZE_COMMIT: [l for l in
                              git("log", "-1", "--format=%B",
                                  NOTARIZE_COMMIT)[1].splitlines()
                              if "Base checked" in l or "origin/main" in l],
            PRODUCER_COMMIT: [l for l in
                              git("log", "-1", "--format=%B",
                                  PRODUCER_COMMIT)[1].splitlines()
                              if "Base checked" in l or "origin/main" in l]},
        "note": "research_dispatch.py:1103-1114 requires the archive commit "
                "message to name the task and the record ids. This probe "
                "resolves that question; the adjudication left it UNKNOWN."}

    R["what_this_probe_does_NOT_establish"] = [
        "It verifies BOOKKEEPING only and adjudicates no producer headline.",
        "It does not assert that a push or a PR happened; that is outside git "
        "history reachable from this clone and stays UNKNOWN here too.",
        "A content match is not a claim that the artifacts are correct, only "
        "that the bytes reviewed are the bytes declared.",
        "CLAIM TIER TOY.",
    ]
    R["wall_clock_seconds"] = round(time.time() - T0, 3)

    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=2)
        fh.write("\n")

    print("PROBE D -- independent verification of the git record")
    print("  HEAD:", R["HEAD"])
    for k, v in split.items():
        print("   %-18s %s  parent=%s  paths=%s  ancestor_of_HEAD=%s"
              % (k, v["resolved_sha"][:12] if v["resolved_sha"] else None,
                 (v["parent"] or "")[:12], v["n_paths_changed"],
                 v["is_ancestor_of_HEAD"]))
    print("  three-way split verdict:",
          json.dumps(R["three_way_split_VERDICT"]))
    print("  content: %d declared, %d match blob-at-commit, %d match tree, "
          "%d mismatches" % (tot, ok_commit, ok_tree, len(mismatches)))
    for t, v in recs.items():
        print("   %s: declared==changeset %s ; receipt inside own commit %s"
              % (t, v["declared_path_set_EQUALS_commit_change_set"],
                 v["receipt_is_INSIDE_its_own_declared_commit"]))
    print("  D3: %d declared, %d dangling, %d undeclared"
          % (R["D3_artifact_path_table"]["n_declared_total"],
             R["D3_artifact_path_table"]["n_dangling_declared_but_not_committed"],
             R["D3_artifact_path_table"]["n_undeclared_committed_but_not_declared"]))
    print("  notarization: absent at parent %s ; --follow commits %s ; "
          "producers absent at notarizer %s"
          % (R["notarization_property"]["frozen_text_ABSENT_at_parent"],
             R["notarization_property"]["git_log_all_follow_n_commits"],
             R["notarization_property"]
              ["every_producer_artifact_ABSENT_at_notarizing_commit"]))
    print("  UNKNOWNs resolved:",
          json.dumps(R["adjudication_UNKNOWNs_resolved"]
                     ["commit messages contain task id and GOAL-MLKEM-005"]))
    print("  wall clock %.2f s" % R["wall_clock_seconds"])


if __name__ == "__main__":
    main()
