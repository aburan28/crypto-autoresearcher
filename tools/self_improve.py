#!/usr/bin/env python3
"""The recursive self-improvement loop over skill instructions.

`tune-skill` proposes one citation-backed diff to one skill's instructions,
scored by that skill's downstream ledger records. On its own it is a single
step: nothing chose the target, nothing measured whether an applied diff
helped, and nothing tuned the tuner. This tool closes the loop:

    plan     state of every target and the one next action
             (revert > measure > tune > wait)
    measure  outcome of an applied round: the target's score on items
             produced after the change against items produced before it, at
             the same evidence horizon, with a bootstrap interval and a
             difference-in-differences against an untouched control skill
    guard    refuse a tuning diff that edits anything outside the target's
             files, edits a frozen region, or is not minimal
    curve    every measured round, per target: the learning curve
    placebo  the same measurement at dates where nothing changed: how often
             the comparison declares a change that is not there

    python3 tools/self_improve.py plan
    python3 tools/self_improve.py measure round-1a2b3c --write
    python3 tools/self_improve.py guard --target propose-ideas --base origin/main

The recursion: `tune-skill` is itself a target. Its items are the outcome
records this tool writes, so the tuner is rewarded for diffs that measurably
improved the skill they changed. What it may not touch is the reward: the
scorer (`tools/tune_skill_batch.py`), this file, the eval suites and graders
are outside every target's write scope, and the reward table, hard
constraints and loop gates in the tune-skill file sit in `frozen:` regions
that `guard` compares byte for byte. A human merging the PR stays the only
approval; the loop opens PRs, it never merges its own tuning.

Rounds are records (`coordination/skill-tuning/<skill>/round-*.yaml`), never
edited. A round is *applied* when its record is on `origin/main`; its
applied date is the first-parent commit that added it. Outcomes are new
records (`outcome-*.yaml`) naming the round. Nothing here is evidence about
ECDLP; it is evidence about the harness (docs/measuring-the-harness.md).
"""

from __future__ import annotations

import argparse
import json
import random
import re
import secrets
import subprocess
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tune_skill_batch as tsb

REPO = Path(__file__).resolve().parents[1]
TUNING_DIR = Path("coordination") / "skill-tuning"
BRANCH_PREFIX = "skill-tuning/"

# Each target's write scope. Authority-bearing contracts (agents/coordinator.md,
# dispatched by design-experiment) are deliberately absent: a loop that can
# rewrite who approves what is not tuning a skill.
TARGETS: dict[str, dict[str, Any]] = {
    "propose-ideas": {
        "files": [".claude/skills/propose-ideas/SKILL.md", ".agents/skills/propose-ideas/SKILL.md",
                  "agents/idea-generator.md", ".claude/agents/idea-generator.md"],
        "control": "design-experiment",
    },
    "design-experiment": {
        "files": [".claude/skills/design-experiment/SKILL.md", ".agents/skills/design-experiment/SKILL.md"],
        "control": "propose-ideas",
    },
    "tune-skill": {
        "files": [".claude/skills/tune-skill/SKILL.md", ".agents/skills/tune-skill/SKILL.md"],
        "control": None,
        "meta": True,
    },
}
GENERATED = {".claude/agents/idea-generator.md"}  # mirrors; not counted in the line budget

MAX_DIFF_LINES = 60            # "minimal, targeted": added + deleted lines over the target's files
MIN_SCORED = tsb.THIN_SCORED_MIN
MIN_CLUSTERS = 4               # per arm; below it a cluster bootstrap is anticonservative (placebo, 2026-10-20)
MIN_HORIZON_DAYS = 7
CENSOR_DAYS = 90               # an applied round still unmeasurable after this is closed as insufficient_data
STALE_PROPOSAL_DAYS = 30       # an open tuning branch older than this no longer blocks its target
BOOTSTRAP_B = 10_000
META_REWARD = {"improved": 2, "no_change_detectable": 0, "regressed": -2}
FROZEN_RE = re.compile(r"<!-- frozen:([a-z0-9-]+) -->(.*?)<!-- /frozen:\1 -->", re.DOTALL)


# --------------------------------------------------------------------------- git

def _git(repo: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False,
                              timeout=60).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _main_ref(repo: Path) -> str:
    return "origin/main" if _git(repo, "rev-parse", "--verify", "-q", "origin/main") else "HEAD"


# --------------------------------------------------------------------------- records

def load_records(repo: Path, skill: str, kind: str) -> list[dict[str, Any]]:
    out = []
    for path in sorted((repo / TUNING_DIR / skill).glob(f"{kind}-*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        body = doc.get("round" if kind == "round" else "outcome")
        if isinstance(body, dict):
            out.append({**body, "_path": str(path.relative_to(repo))})
    return out


def applied_date(repo: Path, rec: dict[str, Any]) -> str | None:
    """Date the round's record reached main, or None while it has not.

    Only a round that changed files can be applied; a rejected or deferred
    round on main changed nothing. `applied_at`, when a test or a backfill
    sets it explicitly, wins over git.
    """
    if rec.get("decision") not in ("proposed", "applied") or not rec.get("files_changed"):
        return None
    if rec.get("applied_at"):
        return str(rec["applied_at"])[:10]
    ref = _main_ref(repo)
    out = _git(repo, "log", ref, "--first-parent", "--diff-filter=A", "--format=%cI", "--", rec["_path"])
    return out.splitlines()[-1][:10] if out else None


def open_proposals(repo: Path, today: date) -> dict[str, list[dict[str, Any]]]:
    """Tuning branches (`skill-tuning/<skill>-<round>`) not yet merged."""
    out: dict[str, list[dict[str, Any]]] = {}
    ref = _main_ref(repo)
    listing = _git(repo, "for-each-ref", "--format=%(refname:short)\t%(committerdate:short)",
                   f"refs/remotes/origin/{BRANCH_PREFIX}")
    for line in listing.splitlines():
        name, _, when = line.partition("\t")
        branch = name.split("/", 1)[1] if name.startswith("origin/") else name
        rest = branch[len(BRANCH_PREFIX):]
        skill = next((t for t in TARGETS if rest.startswith(t + "-")), None)
        if not skill or not when:
            continue
        if subprocess.run(["git", "merge-base", "--is-ancestor", name, ref], cwd=repo, check=False,
                          capture_output=True).returncode == 0:
            continue  # merged: its round is judged from main
        age = (today - date.fromisoformat(when)).days
        out.setdefault(skill, []).append({"branch": branch, "last_commit": when, "age_days": age,
                                          "stale": age > STALE_PROPOSAL_DAYS})
    return out


# --------------------------------------------------------------------------- scoring

Arm = list[tuple[str, float]]   # (cluster, reward) per scored item


def _clusters(arm: Arm) -> list[list[float]]:
    by: dict[str, list[float]] = {}
    for key, r in arm:
        by.setdefault(key, []).append(r)
    return [by[k] for k in sorted(by)]


def bootstrap_diff(post: Arm, pre: Arm, *, ctrl_post: Arm | None = None,
                   ctrl_pre: Arm | None = None, seed: int = 0) -> dict[str, Any]:
    """Cluster bootstrap of mean(post) - mean(pre), minus the same for the
    control when given (difference in differences).

    Clusters, not items, are resampled: items in one area share evidence
    records and reviewers (eleven EXP-ALBIN-* experiments score from one
    EV-ALBIN-001), so an item bootstrap counts one observation eleven times.
    The placebo run that found this: docs/self-improvement-loop.md. Seeded,
    so re-running a measurement reproduces its interval exactly.
    """
    rng = random.Random(seed)
    arms = [_clusters(a) if a is not None else None for a in (post, pre, ctrl_post, ctrl_pre)]

    def mean(cl: list[list[float]]) -> float:
        flat = [x for c in cl for x in c]
        return sum(flat) / len(flat)

    def stat(a, b, c, d) -> float:
        v = mean(a) - mean(b)
        return v - (mean(c) - mean(d)) if c is not None else v

    point = stat(*arms)
    draws = []
    for _ in range(BOOTSTRAP_B):
        rs = lambda cl: [cl[rng.randrange(len(cl))] for _ in cl] if cl is not None else None
        draws.append(stat(*(rs(a) for a in arms)))
    draws.sort()
    return {"estimate": round(point, 4), "ci95": [round(draws[int(0.025 * BOOTSTRAP_B)], 4),
                                                  round(draws[int(0.975 * BOOTSTRAP_B) - 1], 4)],
            "clusters": [len(a) for a in arms if a is not None]}


def verdict(ci: list[float]) -> str:
    if ci[0] > 0:
        return "improved"
    if ci[1] < 0:
        return "regressed"
    return "no_change_detectable"


def object_cohort(skill: str, repo: Path, chain: tsb.Chain, start: str, end: str,
                  horizon: int) -> dict[str, Any]:
    batch = tsb.collect(skill, repo, start, end, chain=chain, evidence_horizon_days=horizon)
    scored = [r for r in batch["items"] if r["status"] == "terminal"]

    def cluster(r: dict[str, Any]) -> str:
        # The area, read like tune_skill_batch does when the item has none:
        # from the evidence id that scored it (EV-<AREA>-...).
        if r.get("area"):
            return str(r["area"])
        m = re.match(r"EV-([A-Z0-9]+)-", (r["chain"]["EV"] or ["?"])[0])
        return m.group(1) if m else r["chain"]["EV"][0]

    return {"window": [start, end], "items": len(batch["items"]),
            "scored": len(scored),
            "rewards": [(cluster(r), r["reward"]) for r in scored],
            "rewards_structured": [(cluster(r), r["reward"]) for r in scored
                                   if r["match_method"] == "structured"],
            "mean": round(sum(r["reward"] for r in scored) / len(scored), 4) if scored else None,
            "resolution_rate": round(len(scored) / len(batch["items"]), 4) if batch["items"] else None}


def meta_items(repo: Path) -> list[dict[str, Any]]:
    """Every outcome record of an object-level round: the tuner's batch."""
    items = []
    for skill, spec in TARGETS.items():
        if spec.get("meta"):
            continue
        rounds = {r["id"]: r for r in load_records(repo, skill, "round")}
        for oc in load_records(repo, skill, "outcome"):
            rnd = rounds.get(oc.get("round_id"), {})
            # Dated by when the tuner produced the round, not when it merged:
            # the tuner version that wrote it is the one being scored.
            produced = str(rnd.get("decided_at") or oc.get("applied_at") or "")[:10] or None
            items.append({"id": oc.get("round_id"), "skill": skill, "date": produced,
                          "verdict": oc.get("verdict"), "reward": META_REWARD.get(oc.get("verdict")),
                          "tuner_blob": rnd.get("tuner_blob")})
    return items


def meta_cohort(repo: Path, start: str, end: str) -> dict[str, Any]:
    rows = [i for i in meta_items(repo) if i["date"] and start <= i["date"] <= end]
    rewards = [(i["skill"], i["reward"]) for i in rows if i["reward"] is not None]
    return {"window": [start, end], "items": len(rows), "scored": len(rewards), "rewards": rewards,
            "rewards_structured": rewards,
            "mean": round(sum(r for _, r in rewards) / len(rewards), 4) if rewards else None,
            "resolution_rate": round(len(rewards) / len(rows), 4) if rows else None}


# --------------------------------------------------------------------------- measure

def measure(repo: Path, skill: str, rnd: dict[str, Any], today: date, *,
            horizon_days: int | None = None, chain: tsb.Chain | None = None) -> dict[str, Any]:
    """Pre/post comparison at equal horizon and equal window length.

    With H = today - applied and h = H // 2 (or `horizon_days`): post items
    are those dated in [applied, today - h], so each has had h full days to
    reach evidence; pre items are those dated in [applied - (H - h), applied),
    scored only on evidence dated within h days of the item. Both windows
    have the same length and every item the same horizon, so a cohort that
    is merely younger does not look worse.
    """
    applied = applied_date(repo, rnd)
    base = {"round_id": rnd["id"], "skill": skill, "applied_at": applied}
    if applied is None:
        return {**base, "verdict": "not_applied"}
    a = date.fromisoformat(applied)
    span = (today - a).days
    h = horizon_days if horizon_days is not None else span // 2
    if h < MIN_HORIZON_DAYS or span - h < 1:
        return {**base, "verdict": "insufficient_data", "censored": span > CENSOR_DAYS,
                "reason": f"{span} day(s) since applied; horizon {h} < {MIN_HORIZON_DAYS}"}
    win = span - h
    pre_w = ((a - timedelta(days=win)).isoformat(), (a - timedelta(days=1)).isoformat())
    post_w = (a.isoformat(), (today - timedelta(days=h)).isoformat())
    meta = TARGETS[skill].get("meta")
    if not meta:
        chain = chain or tsb.Chain(repo)

    def cohort(s: str, w: tuple[str, str]) -> dict[str, Any]:
        return meta_cohort(repo, *w) if meta else object_cohort(s, repo, chain, w[0], w[1], h)

    pre, post = cohort(skill, pre_w), cohort(skill, post_w)
    out = {**base, "horizon_days": h, "window_days": win, "pre": pre, "post": post, "caveats": []}
    def enough(c: dict[str, Any], key: str = "rewards") -> bool:
        return len(c[key]) >= MIN_SCORED and len({k for k, _ in c[key]}) >= MIN_CLUSTERS

    if not (enough(pre) and enough(post)):
        out["verdict"] = "insufficient_data"
        out["censored"] = span > CENSOR_DAYS
        out["reason"] = (f"scored pre {pre['scored']} in {len({k for k, _ in pre['rewards']})} cluster(s), "
                         f"post {post['scored']} in {len({k for k, _ in post['rewards']})}; each arm needs "
                         f"{MIN_SCORED} items in {MIN_CLUSTERS} clusters")
        return out
    raw = bootstrap_diff(post["rewards"], pre["rewards"])
    out["raw"] = {**raw, "verdict": verdict(raw["ci95"])}
    if enough(pre, "rewards_structured") and enough(post, "rewards_structured"):
        s = bootstrap_diff(post["rewards_structured"], pre["rewards_structured"])
        out["structured_only"] = {**s, "verdict": verdict(s["ci95"])}
    else:
        out["caveats"].append("structured-only sensitivity not computable: too few structured matches")
    ctrl = TARGETS[skill].get("control")
    ctrl_clean = ctrl and not any(
        (d := applied_date(repo, r)) and pre_w[0] <= d <= today.isoformat()
        for r in load_records(repo, ctrl, "round"))
    if ctrl_clean:
        cpre, cpost = cohort(ctrl, pre_w), cohort(ctrl, post_w)
        out["control"] = {"skill": ctrl, "pre": cpre, "post": cpost}
        if enough(cpre) and enough(cpost):
            did = bootstrap_diff(post["rewards"], pre["rewards"],
                                 ctrl_post=cpost["rewards"], ctrl_pre=cpre["rewards"])
            out["did"] = {**did, "verdict": verdict(did["ci95"])}
            out["caveats"].append(f"control {ctrl} shares the pipeline, so a spillover from the change "
                                  "into the control biases the difference in differences toward zero")
        else:
            out["caveats"].append(f"control {ctrl} too thin for difference in differences")
    elif ctrl:
        out["caveats"].append(f"control {ctrl} was itself changed inside the windows; no control")
    if "did" not in out:
        out["caveats"].append("uncontrolled for program-wide drift between the two windows")
    out["verdict"] = out.get("did", out["raw"])["verdict"]
    return out


def outcome_record(m: dict[str, Any], today: date, argv: list[str]) -> dict[str, Any]:
    rec = {k: v for k, v in m.items() if k not in ("pre", "post", "control")}
    for arm in ("pre", "post"):
        if arm in m:
            rec[arm] = {k: v for k, v in m[arm].items() if not k.startswith("rewards")}
    if "control" in m:
        rec["control"] = {"skill": m["control"]["skill"],
                          **{arm: {k: v for k, v in m["control"][arm].items() if not k.startswith("rewards")}
                             for arm in ("pre", "post")}}
    rec.update({"id": "outcome-" + secrets.token_hex(3), "measured_at": today.isoformat(),
                "source": {"tool": "tools/self_improve.py", "argv": argv}})
    return {"outcome": rec}


# --------------------------------------------------------------------------- plan

def target_state(repo: Path, skill: str, today: date, proposals: dict[str, list],
                 chain: tsb.Chain | None) -> dict[str, Any]:
    rounds = load_records(repo, skill, "round")
    outcomes = {o.get("round_id"): o for o in load_records(repo, skill, "outcome")}
    rounds.sort(key=lambda r: str(r.get("decided_at") or ""))
    state: dict[str, Any] = {"skill": skill, "rounds": len(rounds), "outcomes": len(outcomes)}
    live = [p for p in proposals.get(skill, []) if not p["stale"]]
    if live:
        return {**state, "action": "wait_review", "detail": live}
    stale = [p for p in proposals.get(skill, []) if p["stale"]]
    if stale:
        state["stale_proposals"] = stale

    applied = [r for r in rounds if applied_date(repo, r)]
    for r in applied:
        oc = outcomes.get(r["id"])
        if oc and oc.get("verdict") == "regressed" and not any(x.get("reverts") == r["id"] for x in rounds):
            return {**state, "action": "revert", "round": r["id"], "files": r.get("files_changed"),
                    "outcome": oc["_path"]}
    pending = [r for r in applied if r["id"] not in outcomes]
    if pending:
        r = pending[-1]
        m = measure(repo, skill, r, today, chain=chain)
        if m["verdict"] != "insufficient_data" or m.get("censored"):
            return {**state, "action": "measure", "round": r["id"], "preview": m["verdict"]}
        return {**state, "action": "wait_outcomes", "round": r["id"], "reason": m.get("reason")}

    since = None
    if rounds:
        until = (rounds[-1].get("batch_window") or {}).get("until")
        since = (date.fromisoformat(str(until)[:10]) + timedelta(days=1)).isoformat() if until else None
    if TARGETS[skill].get("meta"):
        c = meta_cohort(repo, since or "0000-00-00", today.isoformat())
        scored, thin = c["scored"], c["scored"] < MIN_SCORED
    else:
        batch = tsb.collect(skill, repo, since, None, chain=chain)
        scored, thin = batch["reward_summary"]["scored_n"], batch["thin"]
    state.update({"since": since, "new_scored": scored})
    return {**state, "action": "idle" if thin else "tune"}


ACTION_RANK = {"revert": 0, "measure": 1, "tune": 2, "wait_outcomes": 3, "wait_review": 4, "idle": 5}


def plan(repo: Path, today: date) -> list[dict[str, Any]]:
    proposals = open_proposals(repo, today)
    chain = tsb.Chain(repo)
    states = [target_state(repo, s, today, proposals, chain) for s in TARGETS]
    return sorted(states, key=lambda s: (ACTION_RANK[s["action"]], -s.get("new_scored", 0)))


# --------------------------------------------------------------------------- guard

def _show(repo: Path, ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=repo, capture_output=True, text=True, check=False)
    return r.stdout if r.returncode == 0 else None


def guard(repo: Path, target: str, base: str, head: str = "HEAD") -> dict[str, Any]:
    allowed = set(TARGETS[target]["files"])
    record_dir = f"{TUNING_DIR.as_posix()}/{target}/"
    violations, lines = [], 0
    status = _git(repo, "diff", "--name-status", f"{base}...{head}")
    for row in status.splitlines():
        code, *paths = row.split("\t")
        path = paths[-1]
        if path.startswith(record_dir) and code == "A" and re.search(r"/(round|outcome)-[0-9a-f]{6}\.yaml$", path):
            continue
        if path not in allowed:
            violations.append(f"{code} {path}: outside {target}'s write scope")
            continue
        if path not in GENERATED:
            num = _git(repo, "diff", "--numstat", f"{base}...{head}", "--", path).split()
            lines += int(num[0]) + int(num[1]) if len(num) >= 2 and num[0].isdigit() else 0
        merge_base = _git(repo, "merge-base", base, head)
        old, new = _show(repo, merge_base, path) or "", _show(repo, head, path) or ""
        before, after = dict(FROZEN_RE.findall(old)), dict(FROZEN_RE.findall(new))
        for name in sorted(set(before) | set(after)):
            if before.get(name) != after.get(name):
                violations.append(f"{path}: frozen region '{name}' changed")
    if lines > MAX_DIFF_LINES:
        violations.append(f"{lines} changed lines > {MAX_DIFF_LINES}: not a minimal diff")
    sys.path.insert(0, str(REPO))
    from orchestration.eval.fingerprint import TRACKED
    changed = [r.split("\t")[-1] for r in status.splitlines()]
    eval_needed = sorted(set(changed) & set(TRACKED))
    return {"target": target, "base": base, "changed_lines": lines, "ok": not violations,
            "violations": violations, "eval_required": eval_needed}


# --------------------------------------------------------------------------- curve

def curve(repo: Path) -> list[dict[str, Any]]:
    rows = []
    for skill in TARGETS:
        rounds = {r["id"]: r for r in load_records(repo, skill, "round")}
        for oc in load_records(repo, skill, "outcome"):
            est = oc.get("did") or oc.get("raw") or {}
            rows.append({"skill": skill, "round": oc.get("round_id"), "applied_at": oc.get("applied_at"),
                         "verdict": oc.get("verdict"), "estimate": est.get("estimate"), "ci95": est.get("ci95"),
                         "controlled": "did" in oc, "pre_mean": (oc.get("pre") or {}).get("mean"),
                         "post_mean": (oc.get("post") or {}).get("mean"),
                         "diff_summary": (rounds.get(oc.get("round_id")) or {}).get("diff_summary")})
    return sorted(rows, key=lambda r: (r["skill"], str(r["applied_at"])))


# --------------------------------------------------------------------------- placebo

def placebo(repo: Path, skill: str, start: date, end: date, step_days: int, today: date) -> dict[str, Any]:
    """Measure fake rounds "applied" every `step_days` between start and end.

    No instruction changed at these dates, so every conclusive verdict is a
    false positive of the instrument (drift, cohort mix), not of a change.
    """
    chain = None if TARGETS[skill].get("meta") else tsb.Chain(repo)
    rows, d = [], start
    while d <= end:
        fake = {"id": f"placebo-{d.isoformat()}", "decision": "proposed", "files_changed": ["-"],
                "applied_at": d.isoformat(), "_path": "-"}
        m = measure(repo, skill, fake, today, chain=chain)
        rows.append({"date": d.isoformat(), "verdict": m["verdict"],
                     "raw": (m.get("raw") or {}).get("verdict"), "did": (m.get("did") or {}).get("verdict"),
                     "pre_scored": (m.get("pre") or {}).get("scored"),
                     "post_scored": (m.get("post") or {}).get("scored")})
        d += timedelta(days=step_days)
    conclusive = [r for r in rows if r["raw"]]

    def fp(key: str) -> dict[str, Any]:
        xs = [r[key] for r in conclusive if r[key]]
        return {"n": len(xs), "false_positive": sum(v != "no_change_detectable" for v in xs)}

    return {"skill": skill, "dates": len(rows), "measurable": len(conclusive),
            "raw": fp("raw"), "did": fp("did"), "rows": rows}


# --------------------------------------------------------------------------- cli

def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", type=Path, default=REPO)
    ap.add_argument("--today", help="ISO date to measure at (default: UTC today)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("measure")
    p.add_argument("round_id")
    p.add_argument("--horizon-days", type=int)
    p.add_argument("--write", action="store_true", help="write the outcome record (only when conclusive or censored)")
    p = sub.add_parser("guard")
    p.add_argument("--target", required=True, choices=sorted(TARGETS))
    p.add_argument("--base", default="origin/main")
    p.add_argument("--head", default="HEAD")
    p = sub.add_parser("placebo")
    p.add_argument("--target", required=True, choices=sorted(TARGETS))
    p.add_argument("--from", dest="start", required=True)
    p.add_argument("--to", dest="end", required=True)
    p.add_argument("--step-days", type=int, default=7)
    p = sub.add_parser("curve")
    p.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root
    today = date.fromisoformat(args.today) if args.today else datetime.now(UTC).date()

    if args.cmd == "plan":
        states = plan(repo, today)
        if args.json:
            print(json.dumps(states, indent=2, default=str))
        else:
            for s in states:
                extra = {k: v for k, v in s.items() if k not in ("skill", "action")}
                print(f"{s['action']:14} {s['skill']:18} {json.dumps(extra, default=str)}")
            print(f"\nnext: {states[0]['action']} {states[0]['skill']}")
        return 0

    if args.cmd == "measure":
        found = [(s, r) for s in TARGETS for r in load_records(repo, s, "round") if r.get("id") == args.round_id]
        if not found:
            print(f"no round record {args.round_id}", file=sys.stderr)
            return 2
        skill, rnd = found[0]
        if any(o.get("round_id") == rnd["id"] for o in load_records(repo, skill, "outcome")):
            print(f"{rnd['id']} already has an outcome record; outcomes are immutable", file=sys.stderr)
            return 2
        m = measure(repo, skill, rnd, today, horizon_days=args.horizon_days)
        print(json.dumps({k: v for k, v in m.items()}, indent=2, default=str))
        if args.write:
            if m["verdict"] == "not_applied" or (m["verdict"] == "insufficient_data" and not m.get("censored")):
                print(f"not written: {m['verdict']} and not yet censored ({CENSOR_DAYS} days)", file=sys.stderr)
                return 1
            rec = outcome_record(m, today, argv)
            path = repo / TUNING_DIR / skill / f"{rec['outcome']['id']}.yaml"
            path.write_text("# self-improvement outcome; written by tools/self_improve.py, not evidence.\n"
                            + yaml.safe_dump(rec, sort_keys=False, allow_unicode=True, width=100),
                            encoding="utf-8")
            print(f"outcome record: {path.relative_to(repo)}")
        return 0

    if args.cmd == "guard":
        g = guard(repo, args.target, args.base, args.head)
        print(json.dumps(g, indent=2))
        return 0 if g["ok"] else 1

    if args.cmd == "placebo":
        print(json.dumps(placebo(repo, args.target, date.fromisoformat(args.start),
                                 date.fromisoformat(args.end), args.step_days, today), indent=2))
        return 0

    rows = curve(repo)
    if args.json:
        print(json.dumps(rows, indent=2, default=str))
    else:
        print("| skill | round | applied | pre | post | estimate [95% CI] | controlled | verdict |")
        print("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for r in rows:
            print(f"| {r['skill']} | {r['round']} | {r['applied_at']} | {r['pre_mean']} | {r['post_mean']} | "
                  f"{r['estimate']} {r['ci95']} | {r['controlled']} | {r['verdict']} |")
        if not rows:
            print("| (no measured rounds yet) | | | | | | | |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
