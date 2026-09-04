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
  * reviewers report verdicts on the joints they own.

    python3 tools/check_review_independence.py --plan <handoff.yaml> \
        --reports <dir-or-file> [<dir-or-file> ...]
    python3 tools/check_review_independence.py --batch <batch-dir>
"""

from __future__ import annotations

import argparse
import glob
import os
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
    args = parser.parse_args()

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
