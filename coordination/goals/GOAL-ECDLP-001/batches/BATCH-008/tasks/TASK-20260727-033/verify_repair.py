#!/usr/bin/env python3
"""TASK-20260727-033 — re-runnable verification of the a935f207 spec repair.

Discharges RC-3: every claim below is derived here from the git blobs
themselves. No number is copied from any review report. Run from the repo
root; exits non-zero if any check fails.

  python3 coordination/goals/GOAL-ECDLP-001/batches/BATCH-008/tasks/\
TASK-20260727-033/verify_repair.py
"""
import hashlib
import subprocess
import sys

import yaml

CASES = [
    {
        "experiment": "EXP-STR-003",
        "pre_blob": "1c6f10b7ba4db293126504c19b4fe9c931b257f3",
        "post_blob": "5e0dadf7437613e630cfd5511e0ef7a97956a413",
        "line_no": 407,
        "inserted": "'",
        "key": "branch",
    },
    {
        "experiment": "EXP-IC-002",
        "pre_blob": "8987eb01978ab82538b17e35358c389c23a9b7f1",
        "post_blob": "23319080e17607dcb952822317990737adf764ab",
        "line_no": 213,
        "key": "p_dec_counting_bound",
    },
]

failures = []


def check(label, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def blob(sha):
    return subprocess.check_output(["git", "cat-file", "blob", sha])


def strip_added_quotes(post_line, pre_line):
    """Remove exactly the quote pair the repair inserted, then compare."""
    key, _, val = post_line.partition(": ")
    val = val.rstrip("\n")
    if len(val) >= 2 and val[0] == "'" and val[-1] == "'":
        val = val[1:-1]
    return f"{key}: {val}\n" == pre_line


for c in CASES:
    print(f"\n=== {c['experiment']} ===")
    pre, post = blob(c["pre_blob"]), blob(c["post_blob"])

    # 1. the pre-edit blob has NO valid parse (clause L1)
    try:
        yaml.safe_load(pre.decode())
        check("L1 pre-edit blob has no valid parse", False, "it parsed")
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        got = mark.line + 1 if mark else None
        check("L1 pre-edit blob has no valid parse", True,
              f"{type(exc).__name__} at line {got}")

    # 2. the post-edit blob parses and registers the right id
    doc = yaml.safe_load(post.decode())["experiment"]
    check("post-edit blob parses and registers its id",
          doc["id"] == c["experiment"], f"id={doc['id']} status={doc['status']}")

    # 3. whole-file inverse transform: undoing the quoting reproduces the
    #    pre-edit blob byte-for-byte (stronger than a parsed-tree diff,
    #    which is undefined because the pre-edit blob has no parse)
    pre_lines, post_lines = pre.decode().splitlines(True), post.decode().splitlines(True)
    same_len = len(pre_lines) == len(post_lines)
    differing = [i for i, (x, y) in enumerate(zip(pre_lines, post_lines), 1) if x != y]
    check("line count unchanged", same_len, f"{len(pre_lines)} lines")
    check("exactly one differing line", differing == [c["line_no"]], f"differs at {differing}")

    if differing == [c["line_no"]]:
        rebuilt = list(post_lines)
        rebuilt[c["line_no"] - 1] = pre_lines[c["line_no"] - 1]
        check("all other bytes identical", "".join(rebuilt) == pre.decode())
        check("inverse transform reproduces the pre-edit line byte-for-byte",
              strip_added_quotes(post_lines[c["line_no"] - 1], pre_lines[c["line_no"] - 1]))

    # 4. the parsed value equals the original raw text, character for character
    raw = pre_lines[c["line_no"] - 1].split(": ", 1)[1].rstrip("\n")
    found = None
    for entry in doc["metrics"]["secondary"]:
        if isinstance(entry, dict) and c["key"] in entry:
            found = entry[c["key"]]
    check("parsed value == original raw text", found == raw, repr(found))

    # 5. no duplicate mapping keys anywhere (a silent-overwrite risk)
    class Strict(yaml.SafeLoader):
        pass

    def no_dupes(loader, node, deep=False):
        seen = set()
        for k, _ in node.value:
            key = loader.construct_object(k, deep=deep)
            if key in seen:
                raise ValueError(f"duplicate key {key!r}")
            seen.add(key)
        return yaml.SafeLoader.construct_mapping(loader, node, deep)

    Strict.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, no_dupes)
    try:
        yaml.load(post.decode(), Strict)
        check("no duplicate mapping keys", True)
    except ValueError as exc:
        check("no duplicate mapping keys", False, str(exc))

    print(f"  sha256 pre-edit  {hashlib.sha256(pre).hexdigest()}")
    print(f"  sha256 post-edit {hashlib.sha256(post).hexdigest()}")

print("\n=== result ===")
print("  all checks passed" if not failures else f"  FAILURES: {failures}")
sys.exit(1 if failures else 0)
