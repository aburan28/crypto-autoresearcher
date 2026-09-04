#!/usr/bin/env python3
"""ECC priority and budget policy — the single loader for research-priority.yaml.

Declared on user instruction (2026-09-04):
  1. All ECC goals have UNLIMITED budget.
  2. ECC goals take priority over every other goal, always.
  3. Open ECC ideas must be designed into experiments.

Every consumer (goal_portfolio_health.py, validate_ledger.py, the harness
skills) reads the area set from `orchestration/research-priority.yaml` through
this module. Nothing re-derives it, and nothing infers ECC membership from an
identifier prefix: `CRYPTO-001` is an ECDLP search and `DREG`/`MONO`/`RELN`/
`SDEG`/`SIG`/`ICEX` are Semaev and index-calculus machinery, while several
elliptic-sounding areas are deliberately excluded with a recorded reason.

    python3 tools/ecc_priority.py --list-areas
    python3 tools/ecc_priority.py --classify GOAL-MONO-001 RQ-PFDR-ae2fba
    python3 tools/ecc_priority.py --open-ideas [--area ECDLP] [--limit 40]
    python3 tools/ecc_priority.py --budget-violations
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:                                          # pragma: no cover
    print("PyYAML required", file=sys.stderr)
    raise SystemExit(2)

REPO = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO / "orchestration" / "research-priority.yaml"

# Matches the area token of any program identifier: GOAL-/RQ-/H-/EXP-/EV- carry
# the area second; IDEA-/DEC-/TASK- are date-keyed and carry no area, so those
# are classified through their `question_id` instead.
_AREA_RE = re.compile(r"^(?:GOAL|RQ|H|EXP|EV|RUN|KN)-([A-Z0-9]+)-")


def load_policy(path: Path | None = None) -> dict:
    p = path or POLICY_PATH
    with open(p) as fh:
        return yaml.safe_load(fh) or {}


def ecc_areas(policy: dict | None = None) -> set[str]:
    pol = policy if policy is not None else load_policy()
    return {str(a).strip() for a in (pol.get("ecc_areas") or [])}


def area_of(identifier: str) -> str | None:
    """Area token of an identifier, or None when it does not carry one."""
    m = _AREA_RE.match((identifier or "").strip())
    return m.group(1) if m else None


def is_ecc(identifier: str, policy: dict | None = None) -> bool:
    a = area_of(identifier)
    return a is not None and a in ecc_areas(policy)


def sort_key(identifier: str, policy: dict | None = None):
    """Sort key placing ECC records first. Use as `key=` on any goal listing."""
    return (0 if is_ecc(identifier, policy) else 1, identifier or "")


# --------------------------------------------------------------------------
# budget
# --------------------------------------------------------------------------

def unbounded_fields(policy: dict | None = None) -> list[str]:
    pol = policy if policy is not None else load_policy()
    return list((pol.get("budget") or {}).get("unbounded_fields") or [])


def budget_violations(policy: dict | None = None) -> list[tuple[str, str, object, str]]:
    """(goal_id, field, offending_value, path) for ECC goals with a finite budget.

    Only `active` and `draft` goals are checked. A terminal goal's budget is
    history and rewriting it would be a retroactive edit, not a policy fix.
    """
    pol = policy if policy is not None else load_policy()
    if not (pol.get("budget") or {}).get("ecc_unlimited"):
        return []
    fields = unbounded_fields(pol)
    out = []
    for p in _goal_files():
        goal = _goal_of(p)
        if not goal:
            continue
        gid = goal.get("id") or ""
        if not is_ecc(gid, pol):
            continue
        if goal.get("status") not in ("active", "draft"):
            continue
        budget = goal.get("campaign_budget") or {}
        if not isinstance(budget, dict):
            continue
        for f in fields:
            v = budget.get(f)
            if v is not None:
                out.append((gid, f, v, str(p)))
    return out


def _goal_files():
    base = REPO / "ledger" / "goals"
    return sorted(list(base.glob("*.yaml")) + list(base.glob("*/goal.yaml")))


def _goal_of(path):
    try:
        d = yaml.safe_load(Path(path).read_text())
    except Exception:
        return None
    g = (d or {}).get("research_goal") or d or {}
    return g if isinstance(g, dict) else None


# --------------------------------------------------------------------------
# open ideas
# --------------------------------------------------------------------------

def _rq_area_index() -> dict[str, str]:
    idx = {}
    for p in glob.glob(str(REPO / "ledger" / "questions" / "*.yaml")):
        try:
            with open(p) as fh:
                d = yaml.safe_load(fh)
        except Exception:
            continue
        q = (d or {}).get("research_question") or d or {}
        qid = (q or {}).get("id") if isinstance(q, dict) else None
        if qid:
            a = area_of(qid)
            if a:
                idx[qid] = a
    return idx


def _taken_idea_ids() -> set[str]:
    """Idea ids referenced by any hypothesis or experiment specification."""
    taken: set[str] = set()
    pat = re.compile(r"IDEA-\d{8}-[0-9a-zA-Z]{4,8}|[A-Z]+-IDEA-\d+")
    for g in ("ledger/hypotheses/*.yaml", "experiments/*/specification.yaml"):
        for p in glob.glob(str(REPO / g)):
            try:
                taken.update(pat.findall(Path(p).read_text()))
            except Exception:
                continue
    return taken


def open_ecc_ideas(policy: dict | None = None, area: str | None = None) -> list[dict]:
    """Open ECC ideas: status `proposed`, and no hypothesis/experiment cites them.

    These are ranked work under instruction 3, not backlog.
    """
    pol = policy if policy is not None else load_policy()
    areas = ecc_areas(pol)
    rq_area = _rq_area_index()
    taken = _taken_idea_ids()
    out = []
    for p in sorted(glob.glob(str(REPO / "ledger" / "proposals" / "*.yaml"))):
        try:
            with open(p) as fh:
                d = yaml.safe_load(fh)
        except Exception:
            continue
        i = (d or {}).get("idea") or d or {}
        if not isinstance(i, dict):
            continue
        iid = i.get("id")
        if not iid:
            continue
        status = i.get("status") or "proposed"
        if status != "proposed":
            continue
        qid = i.get("question_id") or ""
        a = rq_area.get(qid) or area_of(qid)
        if a not in areas:
            continue
        if area and a != area:
            continue
        if iid in taken:
            continue
        out.append({
            "id": iid,
            "area": a,
            "question_id": qid,
            "added": str(i.get("added") or ""),
            "title": (i.get("title") or "").replace("\n", " ").strip(),
            "path": os.path.relpath(p, REPO),
            "recommended_priority": i.get("recommended_priority"),
        })
    order = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda r: (order.get(str(r.get("recommended_priority")), 3),
                            r["area"], r["added"], r["id"]))
    return out


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--list-areas", action="store_true")
    ap.add_argument("--classify", nargs="+", metavar="ID")
    ap.add_argument("--open-ideas", action="store_true")
    ap.add_argument("--budget-violations", action="store_true")
    ap.add_argument("--area")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    pol = load_policy()

    if args.list_areas:
        areas = sorted(ecc_areas(pol))
        if args.json:
            print(json.dumps({"ecc_areas": areas,
                              "excluded": pol.get("excluded_areas", {})}, indent=1))
        else:
            print(f"# ECC areas ({len(areas)}) — {POLICY_PATH.relative_to(REPO)}")
            for a in areas:
                print(f"  {a}")
            print(f"\n# excluded, with reason ({len(pol.get('excluded_areas') or {})})")
            for a, why in (pol.get("excluded_areas") or {}).items():
                print(f"  {a:8s} {str(why).strip()}")
        return 0

    if args.classify:
        for ident in args.classify:
            a = area_of(ident)
            print(f"{ident:24s} area={a or '-':10s} "
                  f"{'ECC' if is_ecc(ident, pol) else 'non-ECC'}")
        return 0

    if args.budget_violations:
        v = budget_violations(pol)
        if args.json:
            print(json.dumps(v, indent=1, default=str))
        elif not v:
            print("OK: every active/draft ECC goal has an unlimited campaign budget.")
        else:
            print(f"{len(v)} ECC goal budget violation(s) — ECC budgets must be null:")
            for gid, f, val, path in v:
                print(f"  {gid:22s} {f} = {val!r}   ({path})")
        return 1 if v else 0

    if args.open_ideas:
        rows = open_ecc_ideas(pol, area=args.area)
        shown = rows[: args.limit] if args.limit else rows
        if args.json:
            print(json.dumps(shown, indent=1))
            return 0
        print(f"# Open ECC ideas: {len(rows)} "
              f"(status `proposed`, no hypothesis or experiment cites them)")
        print("# These are ranked work under instruction 3, not backlog.\n")
        by_area: dict[str, int] = {}
        for r in rows:
            by_area[r["area"]] = by_area.get(r["area"], 0) + 1
        for a, n in sorted(by_area.items(), key=lambda kv: -kv[1]):
            print(f"  {a:10s} {n:4d}")
        print()
        for r in shown:
            print(f"- {r['id']}  [{r['area']}]  {r['added']}  "
                  f"prio={r.get('recommended_priority')}")
            if r["title"]:
                print(f"    {r['title'][:150]}")
        if args.limit and len(rows) > args.limit:
            print(f"\n... {len(rows) - args.limit} more (raise --limit)")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
