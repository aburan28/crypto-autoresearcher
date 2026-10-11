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

--open-ideas honours committed `coordinator_decision.idea_dispositions` blocks
by explicit ID and always prints what they removed: on stdout in text mode, on
stderr in --json mode, so the --json stdout stays a plain list of open rows.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:                                          # pragma: no cover
    print("PyYAML required", file=sys.stderr)
    raise SystemExit(2)
try:  # libyaml, with the pure loader's errors (tools/fast_yaml.py)
    from fast_yaml import safe_load as _safe_load
except ImportError:  # pragma: no cover - imported from outside tools/
    _safe_load = yaml.safe_load

REPO = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO / "orchestration" / "research-priority.yaml"

# Matches the area token of any program identifier: GOAL-/RQ-/H-/EXP-/EV- carry
# the area second; IDEA-/DEC-/TASK- are date-keyed and carry no area, so those
# are classified through their `question_id` instead.
_AREA_RE = re.compile(r"^(?:GOAL|RQ|H|EXP|EV|RUN|KN)-([A-Z0-9]+)-")


def load_policy(path: Path | None = None) -> dict:
    p = path or POLICY_PATH
    with open(p) as fh:
        return _safe_load(fh) or {}


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
        d = _safe_load(Path(path).read_text())
    except Exception:
        return None
    g = (d or {}).get("research_goal") or d or {}
    return g if isinstance(g, dict) else None


# --------------------------------------------------------------------------
# committed decision blocks: idea_dispositions here, withheld_contracts and
# released_contracts in tools/newest_experiments.py
# --------------------------------------------------------------------------

DECISIONS_DIR = "ledger/decisions"
RULE_9_FIELDS = ("evidence", "budget", "test_boundary", "remaining_uncertainty",
                 "successor_or_revisit")
REOPENED = "reopened"
ORDERING_RULE = (
    "Blocks are applied in ascending (decided_at, decision id) order. decided_at "
    "is compared as an ISO-8601 string (a missing decided_at sorts first) and the "
    "decision id breaks ties. The last applied block that names an ID decides "
    "whether it is held. A block that fails its guards applies nothing.")


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                              text=True, check=False)
    except OSError:
        return None


def _is_git_toplevel(repo: Path) -> bool:
    p = _git(repo, "rev-parse", "--show-toplevel")
    return bool(p and p.returncode == 0 and p.stdout.strip()
                and Path(p.stdout.strip()).resolve() == repo.resolve())


def _is_yaml(rel: str) -> bool:
    return rel.endswith((".yaml", ".yml"))


def _warn_uncommitted(repo: Path, keys: tuple[str, ...], warn) -> None:
    changed: set[str] = set()
    for args in (("diff", "--name-only", "HEAD", "--", DECISIONS_DIR),
                 ("ls-files", "--others", "--exclude-standard", "--", DECISIONS_DIR)):
        p = _git(repo, *args)
        if p is not None and p.returncode == 0:
            changed.update(line for line in p.stdout.splitlines() if line)
    for rel in sorted(changed):
        path = repo / rel
        if not (_is_yaml(rel) and path.is_file()):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        found = [k for k in keys if k in text]
        if found:
            warn(f"{rel} carries {', '.join(found)} but is uncommitted or differs from "
                 "HEAD; only its committed version, if any, is honoured")


def committed_decision_blocks(keys, repo: Path = REPO, *, warn=warn) -> list[dict]:
    """Committed decisions whose `coordinator_decision` carries any of `keys`.

    In a git checkout only HEAD's blobs are read, so a decision exists here
    once it is committed. Outside a git checkout (a fixture tree) the working
    tree is the record, and a warning says so. A file that does not parse is
    skipped with a warning and contributes nothing. Returned in ORDERING_RULE
    order as {decision_id, decided_at, path, record} with record the
    `coordinator_decision` mapping.
    """
    repo = Path(repo).resolve()
    keys = tuple(keys)
    texts: list[tuple[str, str]] = []
    if _is_git_toplevel(repo):
        args = ["grep", "-l", "-F"]
        for k in keys:
            args += ["-e", k]
        p = _git(repo, *args, "HEAD", "--", DECISIONS_DIR)
        if p is None or p.returncode not in (0, 1):
            warn(f"git grep over HEAD:{DECISIONS_DIR} failed "
                 f"({(p.stderr.strip() if p else 'git unavailable')}); "
                 "no decision block is honoured")
            return []
        for line in p.stdout.splitlines():
            rel = line[len("HEAD:"):] if line.startswith("HEAD:") else line
            if not _is_yaml(rel):
                continue
            show = _git(repo, "show", f"HEAD:{rel}")
            if show is None or show.returncode != 0:
                warn(f"cannot read HEAD:{rel}; skipped, nothing in it is honoured")
                continue
            texts.append((rel, show.stdout))
        _warn_uncommitted(repo, keys, warn)
    else:
        warn(f"{repo} is not the top level of a git checkout; working-tree "
             f"decisions under {DECISIONS_DIR} are read as the record")
        for path in sorted((repo / DECISIONS_DIR).glob("*")):
            rel = path.relative_to(repo).as_posix()
            if not (_is_yaml(rel) and path.is_file()):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as error:
                warn(f"cannot read {rel} ({error}); skipped, nothing in it is honoured")
                continue
            if any(k in text for k in keys):
                texts.append((rel, text))

    out = []
    for rel, text in texts:
        try:
            doc = _safe_load(text)
        except Exception as error:
            warn(f"{rel} does not parse ({type(error).__name__}); skipped, "
                 "nothing in it is honoured")
            continue
        if not isinstance(doc, dict):
            warn(f"{rel} is not a mapping; skipped, nothing in it is honoured")
            continue
        stray = [k for k in keys if k in doc]
        if stray:
            warn(f"{rel}: {', '.join(stray)} at top level, not under "
                 "coordinator_decision; ignored")
        cd = doc.get("coordinator_decision")
        if not isinstance(cd, dict) or not any(k in cd for k in keys):
            continue
        decided = cd.get("decided_at")
        out.append({"decision_id": str(cd.get("id") or Path(rel).stem),
                    "decided_at": "" if decided is None else str(decided).replace(" ", "T"),
                    "path": rel, "record": cd})
    out.sort(key=decision_order_key)
    return out


def decision_order_key(decision: dict) -> tuple[str, str]:
    return (decision["decided_at"], decision["decision_id"])


def blocks_of(decision: dict, key: str, *, warn=warn) -> list[dict]:
    """The `key` block(s) of one decision: a mapping, or a list of mappings."""
    raw = decision["record"].get(key)
    if raw is None:
        return []
    items = raw if isinstance(raw, list) else [raw]
    good = [b for b in items if isinstance(b, dict)]
    if len(good) != len(items):
        warn(f"{decision['decision_id']}: {key} has a non-mapping entry; that entry is ignored")
    return good


def rule_9_missing(block: dict) -> list[str]:
    """rule_9_fields that are absent or empty; an empty list means the guard passes."""
    fields = block.get("rule_9_fields")
    if not isinstance(fields, dict):
        return list(RULE_9_FIELDS)
    return [f for f in RULE_9_FIELDS if not str(fields.get(f) or "").strip()]


def idea_disposition_state(repo: Path = REPO, *, warn=warn) -> dict[str, dict]:
    """Ideas disposed by committed decisions, keyed by explicit ID.

    Membership is `applies_to_exactly[*].id` only. A block is honoured only
    when every RULE_9_FIELDS entry is non-empty; otherwise it warns and
    disposes nothing. A block whose disposition is `reopened` restores its IDs
    and needs no guard, because restoring is what a failed guard does anyway.
    """
    state: dict[str, dict] = {}
    for dec in committed_decision_blocks(("idea_dispositions",), repo, warn=warn):
        did = dec["decision_id"]
        for block in blocks_of(dec, "idea_dispositions", warn=warn):
            entries = block.get("applies_to_exactly")
            if not isinstance(entries, list):
                warn(f"{did}: idea_dispositions has no applies_to_exactly list; "
                     "nothing in it is honoured")
                continue
            ids = []
            for e in entries:
                iid = e.get("id") if isinstance(e, dict) else None
                if isinstance(iid, str) and iid.strip():
                    ids.append(iid.strip())
                else:
                    warn(f"{did}: an applies_to_exactly entry carries no explicit id; ignored")
            disposition = str(block.get("disposition") or "").strip()
            if disposition == REOPENED:
                for iid in ids:
                    state.pop(iid, None)
                continue
            missing = rule_9_missing(block)
            if missing:
                warn(f"{did}: idea_dispositions not honoured, rule_9_fields empty or "
                     f"missing: {', '.join(missing)}; its {len(ids)} idea(s) stay open")
                continue
            if not disposition:
                warn(f"{did}: idea_dispositions names no disposition; "
                     f"not honoured, its {len(ids)} idea(s) stay open")
                continue
            for iid in ids:
                state[iid] = {"decision_id": did, "disposition": disposition,
                              "decided_at": dec["decided_at"]}
    return state


# --------------------------------------------------------------------------
# open ideas
# --------------------------------------------------------------------------

def _rq_area_index(repo: Path = REPO) -> dict[str, str]:
    idx = {}
    for p in glob.glob(str(repo / "ledger" / "questions" / "*.yaml")):
        try:
            with open(p) as fh:
                d = _safe_load(fh)
        except Exception:
            continue
        q = (d or {}).get("research_question") or d or {}
        qid = (q or {}).get("id") if isinstance(q, dict) else None
        if qid:
            a = area_of(qid)
            if a:
                idx[qid] = a
    return idx


def _taken_idea_ids(repo: Path = REPO) -> set[str]:
    """Idea ids referenced by any hypothesis or experiment specification."""
    taken: set[str] = set()
    # The legacy three-digit suffix (IDEA-20260801-002) STAYS VALID FOREVER --
    # those records are immutable and must not be renamed (CLAUDE.md
    # "Conventions"). An earlier version of this pattern required 4-8 suffix
    # characters and so silently missed every legacy-form idea, reporting ideas
    # that already had a hypothesis and a frozen contract as still needing
    # design. IDEA-20260801-002 (H-DREG-91be14 / EXP-DREG-620b15) is the case
    # that caught it. Match 3 characters and up.
    pat = re.compile(r"IDEA-\d{8}-[0-9a-zA-Z]{3,8}|[A-Z]+-IDEA-\d+")
    for g in ("ledger/hypotheses/*.yaml", "experiments/*/specification.yaml"):
        for p in glob.glob(str(repo / g)):
            try:
                taken.update(pat.findall(Path(p).read_text()))
            except Exception:
                continue
    return taken


# Proposals are supposed to live in ledger/proposals/ -- CLAUDE.md, AGENTS.md,
# templates/research-records.md and every skill say so, and nothing documents a
# second location. ledger/ideas/ exists anyway: a GOAL-ECQ batch filed eight
# rank>=32 proposals there on 2026-08-24 and the 2026-08-31 coverage-gap intake
# added six more. Fourteen well-formed ECC proposals were therefore invisible to
# this ranking -- eight for RQ-ECQ-e9b361 and six for RQ-AUXIN-f8d8c0, whose
# GOAL-AUXIN-a93442 names IDEA-20260831-df4197 in its own next_action. A goal
# pointing at work the harness cannot see is exactly the failure instruction 3
# is meant to prevent.
#
# They are READ from both places rather than moved, because seventeen committed
# records already bind the ledger/ideas/ path -- dispatch queues, task cards,
# handoffs and a goal record among them -- and moving a file that an archive
# receipt binds breaks the receipt. Reading both costs nothing and breaks
# nothing; consolidating is a Coordinator decision with superseding records.
PROPOSAL_DIRS = ("proposals", "ideas")


def _proposal_paths(repo: Path = REPO) -> list[str]:
    paths: list[str] = []
    for sub in PROPOSAL_DIRS:
        paths.extend(glob.glob(str(repo / "ledger" / sub / "*.yaml")))
    return sorted(paths)


def open_ecc_ideas(policy: dict | None = None, area: str | None = None,
                   *, repo: Path = REPO, honour_dispositions: bool = True,
                   disposed_out: list | None = None) -> list[dict]:
    """Open ECC ideas: status `proposed`, and no hypothesis/experiment cites them.

    These are ranked work under instruction 3, not backlog. An idea disposed
    by a committed decision (idea_disposition_state) is not open; its row,
    plus decision_id and disposition, goes to `disposed_out` when given.
    """
    pol = policy if policy is not None else load_policy(repo / "orchestration" / "research-priority.yaml")
    areas = ecc_areas(pol)
    rq_area = _rq_area_index(repo)
    taken = _taken_idea_ids(repo)
    disposals = idea_disposition_state(repo) if honour_dispositions else {}
    disposed = []
    out = []
    for p in _proposal_paths(repo):
        try:
            with open(p) as fh:
                d = _safe_load(fh)
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
        row = {
            "id": iid,
            "area": a,
            "question_id": qid,
            "added": str(i.get("added") or ""),
            "title": (i.get("title") or "").replace("\n", " ").strip(),
            "path": os.path.relpath(p, repo),
            "recommended_priority": i.get("recommended_priority"),
        }
        if iid in disposals:
            disposed.append({**row, "decision_id": disposals[iid]["decision_id"],
                             "disposition": disposals[iid]["disposition"]})
            continue
        out.append(row)
    order = {"high": 0, "medium": 1, "low": 2}
    for group in (out, disposed):
        group.sort(key=lambda r: (order.get(str(r.get("recommended_priority")), 3),
                                  r["area"], r["added"], r["id"]))
    if disposed_out is not None:
        disposed_out.extend(disposed)
    return out


def disposed_section(disposed: list[dict]) -> list[str]:
    lines = [f"# Disposed by decision: {len(disposed)} (removed from the open list by "
             "explicit ID in a committed coordinator_decision.idea_dispositions block)"]
    for r in disposed:
        lines.append(f"- {r['id']}  [{r['area']}]  {r['decision_id']}  {r['disposition']}")
    return lines


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
        disposed: list[dict] = []
        rows = open_ecc_ideas(pol, area=args.area, disposed_out=disposed)
        shown = rows[: args.limit] if args.limit else rows
        if args.json:
            print(json.dumps(shown, indent=1))
            print("\n".join(disposed_section(disposed)), file=sys.stderr)
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
        print()
        print("\n".join(disposed_section(disposed)))
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
