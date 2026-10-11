#!/usr/bin/env python3
"""Collect and score a `tune-skill` batch from the ledger, reproducibly.

`.claude/skills/tune-skill/SKILL.md` steps 3 and 4 describe a chain walk
(IDEA -> H -> EXP -> EV -> DEC) and a reward table that an agent used to run
by hand with grep. Done by hand the batch is not reproducible: a second
session cannot tell whether it under-counted the same records the first one
did. This tool is the walk, written down:

    python3 tools/tune_skill_batch.py propose-ideas [--since DATE] [--until DATE]
    python3 tools/tune_skill_batch.py design-experiment --write-round coordination/skill-tuning

It reads the derived index (`tools/build_ledger_index.py`, rebuilt if absent)
for proposals, hypotheses and experiments, and parses `ledger/evidence/` and
`ledger/decisions/` directly because those are the terminal records. Two
passes, in the skill's order and kept visibly separate in the output:

- **structured**: `H.proposal_id`, `EXP.derived_from_idea`, `EXP.hypothesis_id`,
  `EV.hypothesis_id` / `EV.experiment_ids`, `DEC.evidence_refs`;
- **free_text**: the item's literal id anywhere in an `EV-*` or `DEC-*` file,
  for items the structured pass left unresolved. These are *candidates*: the
  skill requires a human to read the surrounding text before trusting one, so
  they carry `needs_review: true` and never merge into the structured count.

Scoring follows the skill exactly: `strong`/`replicated` +2,
`preliminary`/`anecdotal` +1, `inconclusive`/`contradictory` 0, anything else
`unscored` with its literal value kept; `direction` is ignored. The thin-data
rule (fewer than five *scored* terminal items, or one area) is reported, not
decided -- the round's `decision` is the user's.

Receipts (`tools/session_receipt.py`) bound the batch where they exist; where
none cover the window the round says so instead of estimating.
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO = Path(__file__).resolve().parents[1]
INDEX_DIR = Path("ledger") / ".index"
ID_RE = re.compile(r"\b(?:IDEA|EXP)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b")

SKILLS = {
    "propose-ideas": {"item_kind": "proposals", "item_prefix": "IDEA-"},
    "design-experiment": {"item_kind": "experiments", "item_prefix": "EXP-"},
}

REWARD = {
    "strong": 2, "replicated": 2,
    "preliminary": 1, "anecdotal": 1,
    "inconclusive": 0, "contradictory": 0,
}
HISTOGRAM_KEY = {2: "plus2", 1: "plus1", 0: "zero"}
THIN_SCORED_MIN = 5
DIAGNOSTIC_FLAGS = ("overclaim", "dominated_by", "heuristic_assumptions")


# --------------------------------------------------------------------------- loading

def load_index(repo_root: Path, kind: str) -> list[dict[str, Any]]:
    path = repo_root / INDEX_DIR / f"{kind}.jsonl"
    if not path.exists():
        import build_ledger_index
        build_ledger_index.build(repo_root)
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _body(doc: Any, *keys: str) -> dict[str, Any] | None:
    if not isinstance(doc, dict):
        return None
    for key in keys:
        if isinstance(doc.get(key), dict):
            return doc[key]
    return doc


def load_yaml_dir(repo_root: Path, rel: str, *body_keys: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse every record under `rel`; return (records, unreadable paths).

    Each record keeps `_text` (the raw file) for the free-text pass and
    `_path` for citations. Unparseable files are listed, not dropped
    silently: a record the walk cannot read is a record it cannot score.
    """
    records, unreadable = [], []
    for path in sorted((repo_root / rel).glob("*.yaml")):
        raw = path.read_text(encoding="utf-8", errors="replace")
        try:
            doc = yaml.safe_load(raw)
        except yaml.YAMLError:
            unreadable.append(str(path.relative_to(repo_root)))
            continue
        body = _body(doc, *body_keys)
        if body is None:
            unreadable.append(str(path.relative_to(repo_root)))
            continue
        rec = dict(body)
        rec.setdefault("id", path.stem)
        rec["_text"] = raw
        rec["_path"] = str(path.relative_to(repo_root))
        records.append(rec)
    return records, unreadable


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if isinstance(v, (str, int))]
    return []


# --------------------------------------------------------------------------- window

def in_window(date: str | None, since: str | None, until: str | None) -> bool:
    """Undated records are kept when there is no lower bound, because a
    missing date is a corpus defect and dropping them would hide it."""
    if date is None:
        return since is None
    if since and date < since:
        return False
    if until and date > until:
        return False
    return True


def item_date(kind: str, row: dict[str, Any]) -> str | None:
    if kind == "experiments" and row.get("designed_at"):
        return str(row["designed_at"])[:10]
    return row.get("date")


# --------------------------------------------------------------------------- chain walk

class Chain:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.hyps = load_index(repo_root, "hypotheses")
        self.exps = load_index(repo_root, "experiments")
        self.evidence, ev_bad = load_yaml_dir(repo_root, "ledger/evidence", "evidence")
        self.decisions, dec_bad = load_yaml_dir(repo_root, "ledger/decisions", "decision", "coordinator_decision")
        self.unreadable = ev_bad + dec_bad

        self.h_by_idea: dict[str, list[str]] = defaultdict(list)
        for h in self.hyps:
            if h.get("proposal_id"):
                self.h_by_idea[str(h["proposal_id"])].append(h["id"])
        self.exp_by_idea: dict[str, list[str]] = defaultdict(list)
        self.exp_by_h: dict[str, list[str]] = defaultdict(list)
        for e in self.exps:
            if e.get("derived_from_idea"):
                self.exp_by_idea[str(e["derived_from_idea"])].append(e["id"])
            if e.get("hypothesis_id"):
                self.exp_by_h[str(e["hypothesis_id"])].append(e["id"])
        self.ev_by_h: dict[str, list[dict]] = defaultdict(list)
        self.ev_by_exp: dict[str, list[dict]] = defaultdict(list)
        for ev in self.evidence:
            if ev.get("hypothesis_id"):
                self.ev_by_h[str(ev["hypothesis_id"])].append(ev)
            for x in _as_list(ev.get("experiment_ids")):
                self.ev_by_exp[x].append(ev)
        self.dec_by_ev: dict[str, list[dict]] = defaultdict(list)
        for dec in self.decisions:
            for ref in _as_list(dec.get("evidence_refs")):
                self.dec_by_ev[ref].append(dec)
        # Free-text pass as one inverted index: every record id mentioned
        # anywhere in an EV/DEC file, built in a single scan of the texts
        # instead of one regex search per (item, file) pair.
        self.mentions_ev: dict[str, list[dict]] = defaultdict(list)
        self.mentions_dec: dict[str, list[dict]] = defaultdict(list)
        for ev in self.evidence:
            for rid in set(ID_RE.findall(ev["_text"])):
                self.mentions_ev[rid].append(ev)
        for dec in self.decisions:
            for rid in set(ID_RE.findall(dec["_text"])):
                self.mentions_dec[rid].append(dec)

    def structured(self, skill: str, item_id: str) -> dict[str, Any]:
        if skill == "propose-ideas":
            hs = sorted(set(self.h_by_idea.get(item_id, [])))
            exps = set(self.exp_by_idea.get(item_id, []))
            for h in hs:
                exps.update(self.exp_by_h.get(h, []))
            exps = sorted(exps)
        else:
            hs, exps = [], [item_id]
        evs: dict[str, dict] = {}
        for h in hs:
            for ev in self.ev_by_h.get(h, []):
                evs[ev["id"]] = ev
        for x in exps:
            for ev in self.ev_by_exp.get(x, []):
                evs[ev["id"]] = ev
        decs: dict[str, dict] = {}
        for ev_id in evs:
            for dec in self.dec_by_ev.get(ev_id, []):
                decs[dec["id"]] = dec
        return {"H": hs, "EXP": exps if skill == "propose-ideas" else [],
                "EV": sorted(evs), "DEC": sorted(decs),
                "_ev": list(evs.values()), "_dec": list(decs.values())}

    def free_text(self, item_id: str) -> dict[str, Any]:
        evs = self.mentions_ev.get(item_id, [])
        decs = self.mentions_dec.get(item_id, [])
        return {"EV": sorted(ev["id"] for ev in evs), "DEC": sorted(d["id"] for d in decs),
                "_ev": evs, "_dec": decs}


def score_evidence(evs: Iterable[dict]) -> dict[str, Any]:
    """Return the item's best reward and every literal strength seen.

    An item with several EV records is scored on its most decisive one,
    because the question is whether the chain *ever* discriminated; the
    full list stays in the row so nothing is hidden by the max.
    """
    strengths, scored = [], []
    for ev in evs:
        s = ev.get("strength")
        literal = s if isinstance(s, str) else (None if s is None else json.dumps(s, default=str))
        strengths.append({"ev": ev["id"], "strength": literal, "direction": ev.get("direction")})
        if isinstance(s, str) and s.strip().lower() in REWARD:
            scored.append(REWARD[s.strip().lower()])
    return {
        "reward": max(scored) if scored else None,
        "strengths": strengths,
        "unscored_values": sorted({x["strength"] if x["strength"] is not None else "null"
                                   for x in strengths
                                   if not (isinstance(x["strength"], str) and x["strength"].strip().lower() in REWARD)}),
    }


def decision_flags(decs: Iterable[dict]) -> list[dict[str, Any]]:
    flagged = []
    for dec in decs:
        text = " ".join(str(dec.get(k) or "") for k in ("rationale", "limitations"))
        hits = [f for f in DIAGNOSTIC_FLAGS if f in text]
        if hits:
            flagged.append({"dec": dec["id"], "flags": hits})
    return flagged


# --------------------------------------------------------------------------- batch

def collect(skill: str, repo_root: Path, since: str | None, until: str | None) -> dict[str, Any]:
    spec = SKILLS[skill]
    kind = spec["item_kind"]
    chain = Chain(repo_root)
    items = [r for r in load_index(repo_root, kind) if in_window(item_date(kind, r), since, until)]

    rows: list[dict[str, Any]] = []
    hist: Counter = Counter()
    unscored_values: Counter = Counter()
    areas: Counter = Counter()
    status_n: Counter = Counter()
    by_method: Counter = Counter()
    for it in items:
        iid = it["id"]
        s = chain.structured(skill, iid)
        method, evs, decs = "structured", s["_ev"], s["_dec"]
        reached = bool(s["H"] or s["EXP"]) if skill == "propose-ideas" else True
        if not evs:
            ft = chain.free_text(iid)
            if ft["_ev"] or ft["_dec"]:
                method, evs, decs = "free_text", ft["_ev"], ft["_dec"]
        row: dict[str, Any] = {
            "id": iid, "area": it.get("area"), "date": item_date(kind, it),
            "excerpt": it.get("claim") or it.get("title") or it.get("success_criterion"),
            "chain": {"H": s["H"], "EXP": s["EXP"], "EV": sorted(e["id"] for e in evs),
                      "DEC": sorted(d["id"] for d in decs)},
            "match_method": method if evs or decs else None,
            "needs_review": method == "free_text",
        }
        if evs:
            sc = score_evidence(evs)
            row["terminal"] = True
            row["reward"] = sc["reward"]
            row["strengths"] = sc["strengths"]
            row["status"] = "terminal"
            if sc["reward"] is None:
                row["status"] = "terminal_unscored"
                for v in sc["unscored_values"]:
                    unscored_values[v] += 1
            else:
                hist[HISTOGRAM_KEY[sc["reward"]]] += 1
                # IDEA ids carry no area; the evidence record that scored
                # the item does (EV-<AREA>-...), so read it from there.
                area = it.get("area")
                if not area:
                    m = re.match(r"EV-([A-Z0-9]+)-", evs[0]["id"])
                    area = m.group(1) if m else "?"
                areas[area] += 1
            by_method[method] += 1
        elif decs and method == "free_text" and not reached:
            # A decision that names the item without any evidence record
            # behind it: typically a ranking or deprioritisation decision
            # listing the ideas it considered. Not in flight, not uncovered,
            # and never scored.
            row["status"] = "mentioned_only"
        elif reached and skill == "propose-ideas":
            row["status"] = "in_flight"
        elif skill == "design-experiment":
            row["status"] = "in_flight" if it.get("status") in {"approved", "running", "completed"} else "uncovered"
        else:
            row["status"] = "uncovered"
        row["decision_flags"] = decision_flags(decs)
        status_n[row["status"]] += 1
        rows.append(row)

    scored_n = sum(hist.values())
    terminal_n = status_n["terminal"] + status_n["terminal_unscored"]
    thin_reasons = []
    if scored_n < THIN_SCORED_MIN:
        thin_reasons.append(f"{scored_n} scored terminal item(s) < {THIN_SCORED_MIN}")
    if scored_n and len(areas) == 1:
        thin_reasons.append(f"all scored items in one area ({next(iter(areas))})")
    return {
        "skill": skill,
        "items": rows,
        "reward_summary": {
            "batch_n": len(rows),
            "terminal_n": terminal_n,
            "scored_n": scored_n,
            "in_flight_n": status_n["in_flight"],
            "mentioned_only_n": status_n["mentioned_only"],
            "uncovered_n": status_n["uncovered"],
            "unscored_n": status_n["terminal_unscored"],
            "unscored_values": [{"value": v, "n": n} for v, n in unscored_values.most_common()],
            "histogram": {"plus2": hist["plus2"], "plus1": hist["plus1"], "zero": hist["zero"]},
            "by_match_method": dict(by_method),
            "scored_by_area": dict(areas.most_common()),
            "coverage_reached_exp": (sum(1 for r in rows if r["chain"]["EXP"] or skill == "design-experiment")
                                     / len(rows)) if rows else None,
        },
        "thin": bool(thin_reasons),
        "thin_reasons": thin_reasons,
        "unreadable": chain.unreadable,
    }


# --------------------------------------------------------------------------- receipts

def receipts_for(skill: str, repo_root: Path, since: str | None, until: str | None) -> dict[str, Any]:
    import session_receipt
    rows = [r for r in session_receipt.load_all(repo_root) if r.get("skill") == skill]
    rows = [r for r in rows if in_window(str(r.get("recorded_at") or "")[:10] or None, since, until)]
    bounced = sum(int(r.get("bounced") or 0) for r in rows)
    return {"sessions": len(rows), "bounced": bounced,
            "outcomes": dict(Counter(r.get("outcome") or "?" for r in rows))}


# --------------------------------------------------------------------------- output

def _git(repo_root: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(["git", *args], cwd=repo_root, text=True,
                                       stderr=subprocess.DEVNULL).strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def render(batch: dict[str, Any], receipts: dict[str, Any]) -> str:
    rs = batch["reward_summary"]
    lines = [f"tune-skill batch: {batch['skill']}",
             f"  items {rs['batch_n']}: terminal {rs['terminal_n']} (scored {rs['scored_n']}, "
             f"unscored {rs['unscored_n']}), in flight {rs['in_flight_n']}, "
             f"mentioned only {rs['mentioned_only_n']}, uncovered {rs['uncovered_n']}",
             f"  histogram +2 {rs['histogram']['plus2']}  +1 {rs['histogram']['plus1']}  0 {rs['histogram']['zero']}",
             f"  terminal items by match method: {rs['by_match_method']}",
             "  unscored strength values: " + (", ".join(
                 f"{(u['value'][:40] + '…') if len(u['value']) > 40 else u['value']!r}x{u['n']}"
                 for u in rs["unscored_values"]) or "none"),
             f"  receipts for skill in window: {receipts['sessions']} session(s), bounced {receipts['bounced']}",
             f"  thin: {batch['thin']} {batch['thin_reasons']}"]
    if batch["unreadable"]:
        lines.append(f"  unreadable terminal records: {len(batch['unreadable'])}")
    lines.append("  terminal items:")
    for r in batch["items"]:
        if r["status"].startswith("terminal"):
            st = ";".join(f"{s['strength']}/{s['direction']}" for s in r["strengths"])
            lines.append(f"    {r['id']}  {r['status']:17} reward={r.get('reward')}  {r['match_method']:10} "
                         f"EV={','.join(r['chain']['EV'])}  [{st}]")
    return "\n".join(lines)


def round_record(batch: dict[str, Any], receipts: dict[str, Any], *, repo_root: Path,
                 since: str | None, until: str | None, decision: str, decided_by: str,
                 caveats: list[str], rationale: list[str], argv: list[str]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    # Only terminal items are written out in full: they are what the score
    # rests on. In-flight, mentioned-only and uncovered items are counted in
    # reward_summary and re-listed by the recorded command; writing their
    # chains made a first draft of this record 600 KB.
    kept = []
    for r in batch["items"]:
        if not r["status"].startswith("terminal"):
            continue
        row = {"id": r["id"], "status": r["status"], "match_method": r["match_method"],
               "reward": r.get("reward"), "ev": r["chain"]["EV"],
               "strength": [s["strength"] for s in r["strengths"]],
               "direction": [s["direction"] for s in r["strengths"]]}
        if r["needs_review"]:
            row["needs_review"] = True
        if r["decision_flags"]:
            row["decision_flags"] = r["decision_flags"]
        kept.append(row)
    batch_argv = [a for a in argv if a in SKILLS or a in ("--since", "--until")
                  or (argv.index(a) > 0 and argv[argv.index(a) - 1] in ("--since", "--until"))]
    all_caveats = list(caveats)
    if batch["thin"]:
        all_caveats.append("batch below thin-data threshold: " + "; ".join(batch["thin_reasons"]))
    if receipts["sessions"] == 0:
        all_caveats.append("no session receipts cover this window; the number of sessions that ran the skill is unknown, not estimated")
    if batch["unreadable"]:
        all_caveats.append(f"{len(batch['unreadable'])} evidence/decision file(s) unreadable and therefore unscored")
    fm = batch["reward_summary"]["by_match_method"].get("free_text", 0)
    if fm:
        all_caveats.append(f"{fm} terminal item(s) matched by free text only and need a reader's confirmation before they are trusted")
    rs = dict(batch["reward_summary"])
    return {"round": {
        "id": "round-" + secrets.token_hex(3),
        "skill": batch["skill"],
        "files_changed": [],
        "batch_window": {"since": since, "until": until or now.date().isoformat(),
                         "origin_main_sha": _git(repo_root, "rev-parse", "origin/main")},
        "batch_source": {"tool": "tools/tune_skill_batch.py", "argv": batch_argv + ["--json"],
                         "uncovered_ids_omitted": True,
                         "note": "batch_items lists terminal items only; re-run argv to list the in-flight, mentioned-only and uncovered rows"},
        "batch_items": kept,
        "reward_summary": rs,
        "receipts": receipts,
        "diff_summary": None,
        "decision": decision,
        "rationale": rationale,
        "caveats": all_caveats,
        "decided_by": decided_by,
        "decided_at": now.isoformat(),
    }}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("skill", choices=sorted(SKILLS))
    parser.add_argument("--repo-root", type=Path, default=REPO)
    parser.add_argument("--since", help="ISO date lower bound on the item's date (inclusive)")
    parser.add_argument("--until", help="ISO date upper bound (inclusive)")
    parser.add_argument("--json", action="store_true", help="print the full batch as JSON")
    parser.add_argument("--write-round", type=Path, metavar="DIR",
                        help="write coordination/skill-tuning/<skill>/round-<tok>.yaml under DIR")
    parser.add_argument("--decision", choices=("applied", "rejected", "deferred"), default="deferred")
    parser.add_argument("--decided-by", default="user")
    parser.add_argument("--caveat", action="append", default=[])
    parser.add_argument("--rationale", action="append", default=[])
    args = parser.parse_args(argv)

    batch = collect(args.skill, args.repo_root, args.since, args.until)
    receipts = receipts_for(args.skill, args.repo_root, args.since, args.until)
    if args.json:
        print(json.dumps({"batch": batch, "receipts": receipts}, indent=2, default=str))
    else:
        print(render(batch, receipts))
    if args.write_round:
        rec = round_record(batch, receipts, repo_root=args.repo_root, since=args.since, until=args.until,
                           decision=args.decision, decided_by=args.decided_by, caveats=args.caveat,
                           rationale=args.rationale, argv=list(argv if argv is not None else sys.argv[1:]))
        out_dir = args.write_round / args.skill
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{rec['round']['id']}.yaml"
        path.write_text("# tune-skill round record; written by tools/tune_skill_batch.py, not evidence.\n"
                        + yaml.safe_dump(rec, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
        print(f"\nround record: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
