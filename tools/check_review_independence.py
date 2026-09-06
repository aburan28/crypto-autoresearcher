#!/usr/bin/env python3
"""Check that a review round rests on the independence it claims.

WHY THIS EXISTS. Independence is a property of how a review was SET UP, and it
is invisible in the output: three concurring reports look identical whether the
reviewers worked blind on separate joints or all read each other and converged
on the most legible step. The difference is decisive -- the first is coverage,
the second is correlated taste wearing the shape of corroboration -- and no
amount of reading the reports recovers which one happened.

So the setup is declared in advance (`review_plan` on the handoff opening the
round) and each reviewer declares what it actually read (`review_attestation`
in its report). This tool checks the two against each other. It cannot verify
that an attestation is truthful; it verifies that the round is internally
consistent and that no declared rule was declared and then broken -- which is
the part that goes wrong silently.

WHAT IT CHECKS.
  * every joint in the plan has exactly one owner, and that owner attested;
  * no reviewer read a sibling report unless `blindness.lifted_for` names it;
  * a claim-changing round declares a proves-too-much control with objects;
  * a blind re-deriver's declared `sources_read` does not intersect the plan's
    `blind_from` -- the one independence property here that is fully mechanical;
  * reviewers report verdicts on the joints they own;
  * the reachable COMMIT-MESSAGE history of the tree a blind agent was given
    states none of the batch's protected literals (--blind-history).

WHY THE HISTORY CHECK EXISTS, AND WHAT IT COSTS. `blind_from` is a list of
FILES, and the checks above can only see declared FILE reads. On 2026-09-05 a
blind re-transcription was nearly contaminated by something that is not a file:
a commit message. Reverting the commit restored the files and could not retract
the message, so `git log --oneline` -- a routine orientation command, in nobody's
blind list -- displayed the protected verdict twice on the branch the blind agent
was to run in (CORR-20260905-547849). Nothing downstream could have detected it
either: a re-derivation that agrees because it was told the answer is
indistinguishable from one that agrees because the answer is right.

This check closes that hole and only that hole.

THE DECLARATION IS BY HASH, AND IT HAS TO BE. A batch running a blind phase
declares that no control-plane file restates the protected values -- so the list
of protected values cannot itself be a plaintext list in the batch file the blind
agent must read to learn its assignment. `blind_phase_hygiene.protected_sha256`
therefore holds sha256 of each protected literal; this tool tokenizes each commit
message and hashes each token, so it can recognise a value it was never told.
Stated plainly: that is obfuscation against a reader, NOT secrecy against a
determined search -- the space of plausible figures is small and brute-forceable.
It keeps the value out of the blind agent's eyes, which is all it claims.

A batch that declares nothing is reported UNCHECKABLE, never passed: silence here
would read as a guarantee. The check cannot see paraphrase, a value written to
different precision, or a verdict described in words it was not given. It
strengthens a declaration; it does not replace giving a blind agent a clean tree.

    python3 tools/check_review_independence.py --plan <handoff.yaml> \
        --reports <dir-or-file> [<dir-or-file> ...]
    python3 tools/check_review_independence.py --batch <batch-dir>
    python3 tools/check_review_independence.py --blind-history origin/main \
        --protected-from <batch.yaml> [--max-commits 500]
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VERDICTS = {"holds", "breaks", "inconclusive"}


def _load(path: str):
    try:
        with open(path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        return {"__error__": str(exc).splitlines()[0]}


def _plan_of(doc) -> dict | None:
    """A plan may be given as a handoff record or as a bare review_plan."""
    if not isinstance(doc, dict):
        return None
    if isinstance(doc.get("review_plan"), dict):
        return doc["review_plan"]
    handoff = doc.get("handoff")
    if isinstance(handoff, dict) and isinstance(handoff.get("review_plan"), dict):
        return handoff["review_plan"]
    return None


def _attestation_of(doc) -> dict | None:
    if not isinstance(doc, dict):
        return None
    if isinstance(doc.get("review_attestation"), dict):
        return doc["review_attestation"]
    for value in doc.values():          # nested under validation_report etc.
        if isinstance(value, dict) and isinstance(
                value.get("review_attestation"), dict):
            return value["review_attestation"]
    return None


def _collect_reports(targets: list[str]) -> list[tuple[str, dict]]:
    reports = []
    for target in targets:
        paths = []
        if os.path.isdir(target):
            for pattern in ("**/*.yaml", "**/*.yml"):
                paths.extend(glob.glob(os.path.join(target, pattern),
                                       recursive=True))
        else:
            paths = [target]
        for path in sorted(set(paths)):
            attestation = _attestation_of(_load(path))
            if attestation is not None:
                reports.append((path, attestation))
    return reports


def _rel(path: str) -> str:
    """Repo-relative where that is shorter, absolute otherwise.

    Reports normally live under `coordination/`, but a caller may point this
    at a path outside the repo; `../../../..` chains help nobody read a
    failure.
    """
    relative = os.path.relpath(path, REPO)
    return path if relative.startswith("..") else relative


def check(plan: dict, reports: list[tuple[str, dict]]) -> list[str]:
    problems: list[str] = []
    rel = _rel

    if not str(plan.get("coordinator_prior") or "").strip():
        problems.append(
            "review_plan.coordinator_prior is empty; the prior is recorded "
            "before the round so that concurrence can be told apart from "
            "agreement with the Coordinator")

    by_task = {}
    for path, attestation in reports:
        task_id = str(attestation.get("task_id") or "").strip()
        if not task_id:
            problems.append(f"{rel(path)}: review_attestation.task_id is empty")
            continue
        if task_id in by_task:
            problems.append(f"{rel(path)}: duplicate attestation for {task_id}")
        by_task[task_id] = (path, attestation)

    # --- joints: enumerated, owned, attested, and reported on ----------------
    joints = plan.get("joints")
    if not isinstance(joints, list) or not joints:
        problems.append("review_plan.joints is empty; a review with no named "
                        "load-bearing step cannot show coverage")
        joints = []
    owners: dict[str, list[str]] = {}
    for index, entry in enumerate(joints):
        if not isinstance(entry, dict):
            problems.append(f"review_plan.joints[{index}] must be a mapping")
            continue
        name = str(entry.get("joint") or "").strip() or f"joints[{index}]"
        owner = str(entry.get("assigned_to") or "").strip()
        if not owner:
            problems.append(f"joint '{name}' has no assigned_to; an unowned "
                            f"joint is the coverage gap this plan exists to "
                            f"make visible")
            continue
        owners.setdefault(name, []).append(owner)
        if not str(entry.get("attack_plan") or "").strip():
            problems.append(f"joint '{name}' has no attack_plan; 'review this' "
                            f"returns an opinion, a worked attack returns a "
                            f"result either way")
        if owner not in by_task:
            problems.append(f"joint '{name}' is assigned to {owner}, which "
                            f"filed no review_attestation")
            continue
        _, attestation = by_task[owner]
        owned = attestation.get("joints_owned") or []
        if name not in [str(j).strip() for j in owned]:
            problems.append(f"{owner} does not claim joint '{name}' in "
                            f"joints_owned")
        if attestation.get("verdict") not in VERDICTS:
            problems.append(f"{owner}: review_attestation.verdict must be "
                            f"holds|breaks|inconclusive")
    for name, assigned in owners.items():
        if len(assigned) > 1:
            problems.append(f"joint '{name}' has {len(assigned)} owners "
                            f"({', '.join(assigned)}); two reviewers on one "
                            f"joint means another joint has none")

    # --- blindness ----------------------------------------------------------
    blindness = plan.get("blindness")
    blindness = blindness if isinstance(blindness, dict) else {}
    lifted = {str(t).strip() for t in (blindness.get("lifted_for") or [])}
    if lifted and not str(blindness.get("rationale") or "").strip():
        problems.append("blindness.lifted_for is nonempty but rationale is "
                        "empty; blindness is lifted on purpose, never drifted "
                        "out of")
    if blindness.get("mutual") is not False:
        for task_id, (path, attestation) in sorted(by_task.items()):
            if attestation.get("read_sibling_reports") and task_id not in lifted:
                problems.append(
                    f"{rel(path)}: {task_id} read sibling reports but is not "
                    f"named in blindness.lifted_for; this round's concurrence "
                    f"is not independent")

    # --- proves-too-much ----------------------------------------------------
    control = plan.get("proves_too_much")
    control = control if isinstance(control, dict) else {}
    if not (control.get("objects") or []):
        problems.append("proves_too_much.objects is empty; a claim-changing "
                        "review runs the argument against objects where its "
                        "conclusion is known false")
    elif not str(control.get("failure_signature") or "").strip():
        problems.append("proves_too_much.failure_signature is empty; state "
                        "what the argument must DO on a known-false object, "
                        "or the control cannot fail")

    # --- blind re-derivation ------------------------------------------------
    rederivation = plan.get("blind_rederivation")
    rederivation = rederivation if isinstance(rederivation, dict) else {}
    if rederivation.get("required"):
        owner = str(rederivation.get("assigned_to") or "").strip()
        blind_from = [str(p).strip() for p in (rederivation.get("blind_from") or [])]
        if not str(rederivation.get("quantity") or "").strip():
            problems.append("blind_rederivation.quantity is empty; the "
                            "re-deriver starts from the statement alone")
        if not blind_from:
            problems.append("blind_rederivation.blind_from is empty; name the "
                            "producer's implementation, notes and report, or "
                            "the independence is not checkable")
        if not owner:
            problems.append("blind_rederivation.required is true with no "
                            "assigned_to")
        elif owner not in by_task:
            problems.append(f"blind_rederivation is assigned to {owner}, which "
                            f"filed no review_attestation")
        else:
            path, attestation = by_task[owner]
            read = [str(p).strip() for p in (attestation.get("sources_read") or [])]
            leaked = sorted({b for b in blind_from
                             for r in read if r == b or r.startswith(b.rstrip("/") + "/")})
            if leaked:
                problems.append(
                    f"{rel(path)}: re-deriver {owner} read {len(leaked)} "
                    f"blind_from path(s) -- {', '.join(leaked)}; the "
                    f"re-derivation is not independent of the implementation "
                    f"it was meant to check")
            if attestation.get("blind_from_respected") is not True and not leaked:
                problems.append(f"{owner}: blind_from_respected must be "
                                f"explicitly true for a re-derivation task")
    return problems


# ---------------------------------------------------------------------------
# blind-history check: the tree a blind agent is GIVEN, not the files it reads
# ---------------------------------------------------------------------------

# A token a commit message could carry a protected value as: a number (with
# optional sign, decimal part and exponent) or a bare word. Hashed one by one,
# so a value can be recognised without this tool ever being told it.
_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def protected_hashes(batch_doc) -> dict[str, str]:
    """{sha256: label} a batch declares protected for its blind phase.

    Read from `blind_phase_hygiene.protected_sha256`, either as a list of
    hex digests or as a {digest: label} mapping. Absent means the batch declared
    nothing, which this tool reports as UNCHECKABLE -- never as a pass. A rule
    stated only in prose cannot be enforced mechanically, and reporting it as
    checked is the false assurance that let CORR-20260905-547849 through.
    """
    batch = (batch_doc or {}).get("batch") or batch_doc or {}
    hygiene = batch.get("blind_phase_hygiene") or {}
    if not isinstance(hygiene, dict):
        return {}
    declared = hygiene.get("protected_sha256")
    if isinstance(declared, dict):
        return {str(k).strip().lower(): str(v) for k, v in declared.items()
                if str(k).strip()}
    if isinstance(declared, list):
        return {str(x).strip().lower(): "protected value" for x in declared
                if str(x).strip()}
    return {}


def _token_hashes(text: str) -> dict[str, str]:
    """{sha256: token} over every token in `text`."""
    import hashlib
    return {hashlib.sha256(t.encode()).hexdigest(): t
            for t in _TOKEN_RE.findall(text)}


def commit_messages(ref: str, max_commits: int = 500,
                    repo: str = REPO) -> list[tuple[str, str]]:
    """(sha, full message) for commits reachable from `ref`, newest first."""
    import subprocess
    # ASCII record/unit separators: neither appears in a commit message, and
    # unlike NUL both survive text-mode subprocess arguments.
    out = subprocess.run(
        ["git", "-C", repo, "log", f"-{int(max_commits)}",
         "--format=%H%x1f%B%x1e", ref],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git log {ref} failed: {out.stderr.strip()[:200]}")
    commits = []
    for chunk in out.stdout.split("\x1e"):
        if "\x1f" not in chunk:
            continue
        sha, _, body = chunk.partition("\x1f")
        commits.append((sha.strip(), body))
    return commits


def check_blind_history(ref: str, hashes: dict[str, str], max_commits: int = 500,
                        repo: str = REPO) -> list[str]:
    """Problems if any protected value appears in `ref`'s reachable messages.

    Reports the OFFENDING COMMIT and the batch's own label for the value, never
    the value itself -- this tool's output is read by the same people the blind
    phase protects.
    """
    if not hashes:
        return ["no protected values declared: add "
                "blind_phase_hygiene.protected_sha256 to the batch, or this "
                "check is UNCHECKABLE rather than passing"]
    problems = []
    for sha, body in commit_messages(ref, max_commits, repo):
        hit = {d: t for d, t in _token_hashes(body).items() if d in hashes}
        for digest in hit:
            problems.append(
                f"{sha[:9]} commit message states a protected value "
                f"({hashes[digest]}) -- a blind agent given this tree can read "
                f"it with `git log`, which is not a file read and is in no "
                f"blind_from list")
    return problems


def _find_in_batch(batch: str) -> tuple[str | None, list[str]]:
    plans = [p for p in glob.glob(os.path.join(batch, "**", "*.yaml"),
                                  recursive=True)
             if _plan_of(_load(p)) is not None]
    return (plans[0] if plans else None), [batch]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", help="handoff or review_plan YAML")
    parser.add_argument("--reports", nargs="*", default=[],
                        help="report files or directories to scan")
    parser.add_argument("--batch", help="batch directory holding both")
    parser.add_argument("--blind-history", metavar="REF",
                        help="git ref whose reachable commit messages must not "
                             "state any protected literal")
    parser.add_argument("--protected-from", metavar="BATCH_YAML",
                        help="batch.yaml declaring blind_phase_hygiene."
                             "protected_literals")
    parser.add_argument("--max-commits", type=int, default=500)
    args = parser.parse_args()

    if args.blind_history:
        if not args.protected_from:
            print("--blind-history requires --protected-from", file=sys.stderr)
            return 2
        hashes = protected_hashes(_load(args.protected_from))
        problems = check_blind_history(args.blind_history, hashes,
                                       args.max_commits)
        if problems:
            for problem in problems:
                print(f"FAIL: {problem}")
            print(f"\n{len(problems)} blind-history problem(s) in {args.blind_history}")
            return 1
        print(f"PASS: {args.blind_history} states none of "
              f"{len(hashes)} protected value(s) in its last "
              f"{args.max_commits} reachable commit messages")
        return 0

    plan_path, report_targets = args.plan, list(args.reports)
    if args.batch:
        found, targets = _find_in_batch(args.batch)
        plan_path = plan_path or found
        report_targets = report_targets or targets
    if not plan_path:
        print("no review_plan found; pass --plan or a --batch containing one",
              file=sys.stderr)
        return 2

    plan = _plan_of(_load(plan_path))
    if plan is None:
        print(f"{plan_path}: no review_plan block", file=sys.stderr)
        return 2

    reports = _collect_reports(report_targets)
    if not reports:
        print("no review_attestation blocks found in the given reports",
              file=sys.stderr)
        return 2

    problems = check(plan, reports)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        print(f"\n{len(problems)} independence problem(s) across "
              f"{len(reports)} report(s)")
        return 1
    print(f"PASS: {len(reports)} report(s), every joint owned and attested, "
          f"blindness respected, controls declared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
