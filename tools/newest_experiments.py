#!/usr/bin/env python3
"""Select ECC-first/newest-first execution work without mistaking attempts for completion.

Only explicit trial-plan coverage establishes measurement completion. Legacy
activity without a plan is surfaced by --include-blocked for reconciliation,
not silently called complete and not automatically rerun. Selection never
replaces the dispatcher, committed approval, claim or archive gates.

Committed `coordinator_decision.withheld_contracts` blocks drop their explicit
`ids` from unqualified and --goal selection; `released_contracts.ids` in a later
decision restores them. --experiment still returns a named withheld row. Every
run prints one stderr count line naming each honouring decision, and
--show-withheld lists every held id with its decision (stderr under --json,
stdout after the rows otherwise). --json stdout keeps its row shape.

Ordering is ECC first, then READINESS first (`ready` before
`needs_implementation_or_plan`), then newest. The earlier newest-first order
put 82 unimplemented contracts ahead of the 2 that could run, so every /run
wake read the queue and stopped (docs/track-record-review-20261006.md, P0.3).
Each row also carries `off_main_runs`: remote branches holding unmerged
commits under the experiment's runs/, so a session sees work in flight on
another branch before it starts the same contract.

In a sparse checkout (docs/sparse-checkout.md) a committed run left off disk
still counts: it is read from the index, and a trial plan whose coverage it
decides selects as `needs_materialization`, never as `ready`.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
try:  # libyaml, with the pure loader's errors (tools/fast_yaml.py)
    from fast_yaml import safe_load as _safe_load
except ImportError:  # pragma: no cover - imported from outside tools/
    _safe_load = yaml.safe_load
import ecc_priority  # noqa: E402
import sparse_checkout  # noqa: E402
from experiment_execution import coverage  # noqa: E402

_EXP_ID_RE = re.compile(r"EXP-[A-Za-z0-9]+-(?:[0-9a-fA-F]{6}|\d{3})")


def _load(path: Path) -> dict[str, Any] | None:
    try:
        doc = _safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            return None
        exp = doc.get("experiment", doc)
        return exp if isinstance(exp, dict) else None
    except (OSError, ValueError, yaml.YAMLError):
        return None


def execution_progress(exp_dir: Path, repo: Path) -> dict[str, Any]:
    plan = exp_dir / "trial-plan.json"
    # A sparse checkout leaves tracked files off disk; they still exist.
    absent = sparse_checkout.tracked_absent(repo, f"experiments/{exp_dir.name}/")
    materialize = {"execution_state": "needs_materialization",
                   "reason": "committed records are outside this sparse checkout; run "
                             f"`{sparse_checkout.materialize_hint(exp_dir.name)}` first"}
    if plan.exists() or plan.is_symlink():
        try:
            report = coverage(repo, plan)
            if report.get("not_materialized") and not report["measurement_complete"]:
                return {**materialize, "trial_plan": str(plan.relative_to(repo)), "coverage": report}
            state = ("measurement_complete" if report["measurement_complete"] else
                     "ready" if report["planned"] else "needs_reconciliation")
            return {"execution_state": state, "trial_plan": str(plan.relative_to(repo)),
                    "coverage": report}
        except (OSError, ValueError, TypeError) as error:
            return {"execution_state": "needs_plan_repair", "reason": str(error)}
    if f"experiments/{exp_dir.name}/trial-plan.json" in absent:
        return materialize
    runs = exp_dir / "runs"
    activity = runs.is_dir() and any(runs.iterdir())
    activity = activity or any(exp_dir.rglob("execution-report.yaml")) or any(
        exp_dir.rglob("execution_report.yaml"))
    activity = activity or any(
        path.startswith(f"experiments/{exp_dir.name}/runs/")
        or path.endswith(("/execution-report.yaml", "/execution_report.yaml")) for path in absent)
    if activity:
        return {"execution_state": "needs_reconciliation",
                "reason": "legacy attempts/reports exist without explicit trial coverage; do not rerun blindly"}
    return {"execution_state": "needs_implementation_or_plan",
            "reason": "no trial plan; arrange scoped implementation/contract preparation before execution"}


_READINESS_RANK = {"ready": 0, "needs_materialization": 1, "needs_implementation_or_plan": 2,
                   "needs_reconciliation": 3, "needs_plan_repair": 4}
# needs_materialization occurs only in a sparse checkout: one command from runnable.
_SELECTABLE = ("ready", "needs_materialization", "needs_implementation_or_plan")


def off_main_runs(repo: Path = REPO, *, base: str = "origin/main") -> dict[str, list[str]]:
    """Experiment id -> remote refs with unmerged commits under its runs/.

    One `git log` over every remote ref not reachable from `base`, restricted
    to runs/ paths. Empty when git or the base ref is unavailable; never
    raises, because selection must work in a checkout with no remote.
    """
    try:
        out = subprocess.run(
            ["git", "log", "--remotes=origin", "--not", base, "--name-only",
             "--format=@@%D", "--", "experiments/*/runs"],
            cwd=repo, capture_output=True, text=True, timeout=60, check=False).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    found: dict[str, set[str]] = {}
    refs: list[str] = []
    for line in out.splitlines():
        if line.startswith("@@"):
            refs = [r.strip() for r in line[2:].split(",") if r.strip()]
            continue
        parts = line.split("/")
        if len(parts) >= 3 and parts[0] == "experiments" and parts[2] == "runs":
            found.setdefault(parts[1], set()).update(refs or ["(unnamed commit)"])
    return {eid: sorted(r) for eid, r in sorted(found.items())}


def _completed(exp_dir: Path) -> bool:
    """Compatibility helper: populated directories and prose reports are not completion."""
    return execution_progress(exp_dir, exp_dir.parent.parent)["execution_state"] == "measurement_complete"


def _superseded_ids(specs: list[tuple[Path, dict[str, Any]]]) -> set[str]:
    superseded: set[str] = set()
    for _, exp in specs:
        raw = exp.get("supersedes")
        if raw:
            text = raw if isinstance(raw, str) else " ".join(str(x) for x in raw)
            superseded.update(_EXP_ID_RE.findall(text))
    return superseded


def withheld_state(repo: Path = REPO, *, warn=ecc_priority.warn) -> dict[str, str]:
    """Experiment id -> id of the committed decision that currently withholds it.

    Membership is `withheld_contracts.ids` only. A block is honoured only when
    every rule_9_fields entry is non-empty; otherwise it warns, naming the
    decision, and its ids stay selectable. `released_contracts.ids` restores
    ids and needs no guard. Decisions apply in ecc_priority.ORDERING_RULE
    order; within one decision a release is applied after its holds.
    """
    state: dict[str, str] = {}
    keys = ("withheld_contracts", "released_contracts")
    for dec in ecc_priority.committed_decision_blocks(keys, repo, warn=warn):
        did = dec["decision_id"]
        for key in keys:
            for block in ecc_priority.blocks_of(dec, key, warn=warn):
                raw = block.get("ids")
                if not isinstance(raw, list):
                    warn(f"{did}: {key} has no ids list; nothing in it is applied")
                    continue
                ids = []
                for item in raw:
                    eid = item.get("id") if isinstance(item, dict) else item
                    if isinstance(eid, str) and eid.strip():
                        ids.append(eid.strip())
                    else:
                        warn(f"{did}: a {key}.ids entry is not an explicit id; ignored")
                if key == "released_contracts":
                    for eid in ids:
                        state.pop(eid, None)
                    continue
                missing = ecc_priority.rule_9_missing(block)
                if missing:
                    warn(f"{did}: withheld_contracts not honoured, rule_9_fields empty or "
                         f"missing: {', '.join(missing)}; its {len(ids)} id(s) stay selectable")
                    continue
                for eid in ids:
                    state[eid] = did
    return state


def newest_runnable(repo: Path = REPO, *, include_blocked: bool = False,
                    goal: str | None = None, experiment_ids: set[str] | None = None,
                    honour_holds: bool = True,
                    hold_report: dict[str, Any] | None = None,
                    off_main: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
    """Selectable rows: ECC first, then ready before unimplemented, then newest.

    Withheld ids (withheld_state) are dropped unless `experiment_ids` names
    them. Pass a dict as `hold_report` to receive what the holds did. Pass
    `off_main` (see off_main_runs) to annotate rows; None computes it.
    """
    if off_main is None:
        off_main = off_main_runs(repo)
    repo = repo.resolve()
    policy = ecc_priority.load_policy(repo / "orchestration" / "research-priority.yaml")
    specs = [(spec, exp) for spec in sorted((repo / "experiments").glob("EXP-*/specification.yaml"))
             if (exp := _load(spec)) is not None]
    superseded = _superseded_ids(specs)
    held = withheld_state(repo) if honour_holds else {}
    dropped: list[dict[str, str]] = []
    explicit: list[dict[str, str]] = []
    rows: list[dict[str, Any]] = []
    for spec, exp in specs:
        exp_id = str(exp.get("id") or spec.parent.name)
        if (exp.get("status") != "approved" or not exp.get("approved_by")
                or exp.get("frozen") is not True or exp.get("execution_authorized") is False
                or exp_id in superseded):
            continue
        if goal is not None and exp.get("goal_id") != goal:
            continue
        if experiment_ids is not None and exp_id not in experiment_ids:
            continue
        progress = execution_progress(spec.parent, repo)
        if progress["execution_state"] == "measurement_complete":
            continue
        if not include_blocked and progress["execution_state"] not in _SELECTABLE:
            continue
        if exp_id in held:
            hold = {"id": exp_id, "decision_id": held[exp_id]}
            if experiment_ids is None:
                dropped.append(hold)
                continue
            explicit.append(hold)
        rows.append({"id": exp_id, "designed_at": str(exp.get("designed_at") or ""),
                     "goal_id": exp.get("goal_id"), "hypothesis_id": exp.get("hypothesis_id"),
                     "specification": str(spec.relative_to(repo)),
                     "ecc": ecc_priority.is_ecc(exp_id, policy),
                     "off_main_runs": off_main.get(exp_id, []), **progress})
    ecc = [r for r in rows if r["ecc"]]
    non = [r for r in rows if not r["ecc"]]
    for group in (ecc, non):
        group.sort(key=lambda r: (r["designed_at"], r["id"]), reverse=True)
        group.sort(key=lambda r: _READINESS_RANK.get(r["execution_state"], 9))
    if hold_report is not None:
        decisions: dict[str, dict[str, Any]] = {}
        for eid, did in sorted(held.items()):
            decisions.setdefault(did, {"decision_id": did, "held": 0, "dropped": 0})["held"] += 1
        for hold in dropped:
            decisions[hold["decision_id"]]["dropped"] += 1
        hold_report.update({
            "honour_holds": honour_holds,
            "ordering_rule": ecc_priority.ORDERING_RULE,
            "decisions": sorted(decisions.values(), key=lambda d: d["decision_id"]),
            "withheld": [{"id": eid, "decision_id": did} for eid, did in sorted(held.items())],
            "dropped": dropped,
            "explicit": explicit,
        })
    return ecc + non


def hold_count_line(report: dict[str, Any]) -> str:
    if not report.get("honour_holds", True):
        return "newest_experiments: holds: not honoured (honour_holds=False); 0 row(s) dropped"
    decisions = report.get("decisions") or []
    if not decisions:
        return "newest_experiments: holds: no honouring decision; 0 row(s) dropped"
    parts = [f"{d['decision_id']} dropped {d['dropped']} row(s) of {d['held']} held id(s)"
             for d in decisions]
    return (f"newest_experiments: holds: {'; '.join(parts)}; "
            f"explicit --experiment overrides {len(report.get('explicit') or [])}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1, help="0 means all eligible work")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--include-blocked", action="store_true")
    parser.add_argument("--goal")
    parser.add_argument("--experiment", action="append")
    parser.add_argument("--show-withheld", action="store_true",
                        help="list every withheld id and its decision (stderr under --json)")
    args = parser.parse_args(argv)
    report: dict[str, Any] = {}
    rows = newest_runnable(include_blocked=args.include_blocked, goal=args.goal,
                           experiment_ids=set(args.experiment) if args.experiment else None,
                           hold_report=report)
    shown = rows[:max(args.limit, 0)] if args.limit else rows
    if args.json:
        print(json.dumps(shown, indent=2))
    else:
        for row in shown:
            flight = f"\toff-main: {','.join(row['off_main_runs'])}" if row["off_main_runs"] else ""
            print(f"{row['id']}\t{row['designed_at']}\t{'ECC' if row['ecc'] else 'non-ECC'}"
                  f"\t{row['execution_state']}\t{row['specification']}{flight}")
    ready = sum(1 for r in rows if r["execution_state"] == "ready")
    sparse = sum(1 for r in rows if r["execution_state"] == "needs_materialization")
    print(f"newest_experiments: {len(rows)} selectable row(s): {ready} ready, "
          + (f"{sparse} need materialization (sparse checkout), " if sparse else "")
          + f"{len(rows) - ready - sparse} need implementation/plan; ready rows sort first",
          file=sys.stderr)
    for hold in report.get("explicit") or []:
        print(f"newest_experiments: {hold['id']} is withheld from dispatch by "
              f"{hold['decision_id']}; returned because --experiment named it "
              "(the hold governs unqualified and --goal selection only)", file=sys.stderr)
    print(hold_count_line(report), file=sys.stderr)
    if args.show_withheld:
        withheld = report.get("withheld") or []
        lines = [f"# withheld by decision: {len(withheld)}"]
        lines += [f"{hold['id']}\t{hold['decision_id']}" for hold in withheld]
        print("\n".join(lines), file=sys.stderr if args.json else sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
