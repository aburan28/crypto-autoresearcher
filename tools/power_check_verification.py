#!/usr/bin/env python3
"""Mechanical verification of the power-check-before-calibration-run
sequencing discipline (amendment v4 V4-CHG-7 + amendment v5 V5-CHG-3; RC-4 of
TASK-20260908-d54138).

Two independent checks, BOTH required, neither sufficient alone:

  1. ANCESTRY  (V4-CHG-7, unchanged):
         git merge-base --is-ancestor <power_check_ancestor_commit_sha> <HEAD>
     must exit 0.  Rules out "no sha cited", "sha does not exist", and "sha
     postdates HEAD".  It verifies DAG reachability ONLY -- it never inspects
     the ancestor commit's tree contents.

  2. CONTENT   (V5-CHG-3, new):
         git show <power_check_ancestor_commit_sha>:<path-to-power_check_
         results.yaml> | sha256sum
     must match <power_check_artifact_sha256> byte-for-byte.  Rules out "an
     arbitrary-but-real ancestor commit that happens to contain no such
     artifact, or a different, stale, or wrong artifact at that path" -- the
     specific gap the amendment-v4-review's throwaway-git-repository
     demonstration exposed (an unrelated ancestor with NO artifact passes the
     ancestry check with the same exit code 0 as the correct commit).

The sha256 is computed in Python over the exact bytes returned by
`git show <sha>:<path>`; this is byte-for-byte the same digest that
`git show <sha>:<path> | sha256sum` prints, without depending on the
`sha256sum` binary (macOS ships `shasum`/`openssl` instead).

Modes
-----
  --self-test
      Build a throwaway git repository and prove the mechanism end to end:
      the correct commit passes BOTH checks; an unrelated ancestor that
      contains no power-check artifact passes the ancestry check but FAILS
      the content check (reproducing the review's demonstration).  No
      repository state is touched; nothing is committed in the real repo.

  --ancestor <40-hex-sha> --artifact <repo-relative-path> --sha256 <64-hex>
      [--head <ref>]
      Run BOTH checks in the real repository against the cited values.
      Exits 0 only if both pass.

  --sha256-of <path>
      Print the sha256 of a WORKING-TREE file (used to record
      power_check_artifact_sha256 for an artifact that is not yet committed).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile


def _run(cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def _git_show_bytes(repo: str, sha: str, path: str) -> bytes | None:
    """Return the exact bytes of <path> as committed at <sha>, or None if the
    path is not present in that commit's tree."""
    proc = subprocess.run(
        ["git", "show", f"{sha}:{path}"],
        cwd=repo, capture_output=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def check_ancestry(repo: str, ancestor: str, head: str) -> tuple[bool, str]:
    """Check 1 (V4-CHG-7): `git merge-base --is-ancestor <ancestor> <head>`."""
    proc = _run(["git", "merge-base", "--is-ancestor", ancestor, head], cwd=repo)
    ok = proc.returncode == 0
    detail = (f"git merge-base --is-ancestor {ancestor} {head} "
              f"-> exit {proc.returncode}")
    return ok, detail


def check_content(repo: str, ancestor: str, path: str,
                  expected_sha256: str) -> tuple[bool, str]:
    """Check 2 (V5-CHG-3): sha256 of `git show <ancestor>:<path>` equals
    <expected_sha256>."""
    data = _git_show_bytes(repo, ancestor, path)
    if data is None:
        return False, (f"git show {ancestor}:{path} -> path not present in "
                       f"that commit's tree (content check FAILS)")
    actual = hashlib.sha256(data).hexdigest()
    ok = actual == expected_sha256.lower()
    detail = (f"git show {ancestor}:{path} | sha256 -> {actual} "
              f"(expected {expected_sha256.lower()})")
    return ok, detail


def run_both(repo: str, ancestor: str, path: str, expected_sha256: str,
             head: str = "HEAD") -> bool:
    a_ok, a_detail = check_ancestry(repo, ancestor, head)
    c_ok, c_detail = check_content(repo, ancestor, path, expected_sha256)
    print(f"[ancestry] {a_detail}  ->  {'PASS' if a_ok else 'FAIL'}")
    print(f"[content ] {c_detail}  ->  {'PASS' if c_ok else 'FAIL'}")
    both = a_ok and c_ok
    print(f"VERDICT: {'PASS (both checks)' if both else 'FAIL'}")
    return both


def self_test() -> bool:
    """Throwaway-repo demonstration that BOTH checks are required.

    Layout:
        A (root)   : unrelated.txt only  (NO power-check artifact)
        B (child)  : + power_check_results.yaml (known content)
        HEAD = B
    Expected:
        ancestry(A)  PASS  (A is a real ancestor of HEAD)
        content (A)  FAIL  (A's tree has no power_check_results.yaml)
        ancestry(B)  PASS
        content (B)  PASS  (B's tree has the exact artifact)
    This reproduces the amendment-v4-review's finding that ancestry alone is
    insufficient: A passes the ancestry check with exit 0 yet carries no
    artifact, and only the content check catches it.
    """
    print("=== self-test: throwaway git repository ===")
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        env.update({"GIT_AUTHOR_NAME": "rc4-selftest",
                    "GIT_AUTHOR_EMAIL": "rc4@selftest",
                    "GIT_COMMITTER_NAME": "rc4-selftest",
                    "GIT_COMMITTER_EMAIL": "rc4@selftest"})

        def git(*args: str) -> None:
            proc = subprocess.run(["git", *args], cwd=tmp, env=env,
                                  capture_output=True, text=True)
            if proc.returncode != 0:
                raise RuntimeError(f"git {args} failed: {proc.stderr}")

        git("init", "-q")
        # Commit A: unrelated file only.
        with open(os.path.join(tmp, "unrelated.txt"), "w") as f:
            f.write("no power-check artifact here\n")
        git("add", "unrelated.txt")
        git("commit", "-q", "-m", "A: unrelated (no power-check artifact)")
        a_sha = git_rev_parse(tmp, "HEAD")
        # Commit B: add the power-check artifact with known content.
        artifact = "regime_decision: N=10\npre_registered: true\n"
        with open(os.path.join(tmp, "power_check_results.yaml"), "w") as f:
            f.write(artifact)
        git("add", "power_check_results.yaml")
        git("commit", "-q", "-m", "B: power-check artifact committed")
        b_sha = git_rev_parse(tmp, "HEAD")
        expected = hashlib.sha256(artifact.encode()).hexdigest()

        print(f"  A (no artifact) = {a_sha}")
        print(f"  B (artifact)    = {b_sha}")
        print(f"  expected sha256 = {expected}")
        print()

        # The gap the review exposed: ancestry(A) passes, content(A) fails.
        a_anc, a_anc_d = check_ancestry(tmp, a_sha, "HEAD")
        a_con, a_con_d = check_content(tmp, a_sha, "power_check_results.yaml",
                                       expected)
        print(f"  unrelated ancestor A:")
        print(f"    [ancestry] {a_anc_d}  ->  {'PASS' if a_anc else 'FAIL'}")
        print(f"    [content ] {a_con_d}  ->  {'PASS' if a_con else 'FAIL'}")
        gap_shown = a_anc and (not a_con)
        print(f"  -> ancestry ALONE is insufficient: "
              f"{'GAP REPRODUCED (A passes ancestry, fails content)' if gap_shown else 'NOT reproduced'}")
        print()

        # The correct commit B passes both.
        b_ok = run_both(tmp, b_sha, "power_check_results.yaml", expected,
                        head="HEAD")
        print()

        ok = gap_shown and b_ok
        print(f"SELF-TEST VERDICT: {'PASS' if ok else 'FAIL'}")
        return ok


def git_rev_parse(repo: str, ref: str) -> str:
    proc = _run(["git", "rev-parse", ref], cwd=repo)
    if proc.returncode != 0:
        raise RuntimeError(f"git rev-parse {ref} failed: {proc.stderr}")
    return proc.stdout.strip()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true",
                    help="throwaway-repo demonstration of both checks")
    ap.add_argument("--ancestor", help="40-hex power_check_ancestor_commit_sha")
    ap.add_argument("--artifact", help="repo-relative path to power_check_results.yaml")
    ap.add_argument("--sha256", dest="sha256",
                    help="64-hex power_check_artifact_sha256")
    ap.add_argument("--head", default="HEAD",
                    help="branch HEAD the task card is opened on (default HEAD)")
    ap.add_argument("--sha256-of", dest="sha256_of",
                    help="print the sha256 of a working-tree file and exit")
    args = ap.parse_args(argv)

    if args.self_test:
        return 0 if self_test() else 1

    if args.sha256_of:
        with open(args.sha256_of, "rb") as f:
            print(hashlib.sha256(f.read()).hexdigest())
        return 0

    if not (args.ancestor and args.artifact and args.sha256):
        ap.error("--ancestor, --artifact and --sha256 are required together "
                 "(or use --self-test / --sha256-of)")
    repo = os.environ.get("GIT_DIR_REPO", os.getcwd())
    ok = run_both(repo, args.ancestor, args.artifact, args.sha256, head=args.head)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
