#!/usr/bin/env python3
"""Check, search and report the ECDLP lead atlas (knowledge/leads/ecdlp/).

The known-results map (knowledge/frontiers/ecdlp/) says what the LITERATURE
established. The lead atlas says what THIS PROGRAM has done: one row per
mechanism family that might make ECDLP cheaper, its disposition, the
obstruction that closed it or the next step that would decide it, and the
evidence in all four repositories (crypto-autoresearcher, crypto,
cryptanalysis, ecc-challenges). Its review state pins the commit each repository
was examined at, so a fresh clone can tell at once whether anything has
happened since: "already done" becomes a computed answer, not a re-reading.

    python3 tools/lead_atlas.py --brief          # session-start summary (never fails)
    python3 tools/lead_atlas.py --check          # CI: schema, refs, evidence paths, coverage
    python3 tools/lead_atlas.py --match "TEXT"   # rank leads and KR rows against an idea
    python3 tools/lead_atlas.py --delta          # what changed since the last review
    python3 tools/lead_atlas.py --coverage       # ECC ledger records not mapped to a lead
    python3 tools/lead_atlas.py --render [--out PATH]   # ATLAS.md (derived)
    python3 tools/lead_atlas.py --stamp          # record a completed review (REVIEW_STATE.json)

The atlas is a derived index of committed evidence. It changes no hypothesis,
experiment or goal status (AGENTS.md "Research states"); a disposition here
cites the record that decided it. Saturation (no open lead without a decided
next step, no unexamined lead, no unmapped record, no delta since review) is a
reporting state, never a reason to stop a goal (AGENTS.md "Goals are never
paused").
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import re
import subprocess
import sys
from typing import Any

import yaml

LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATLAS = os.path.join(REPO, "knowledge", "leads", "ecdlp")
STATE = os.path.join(ATLAS, "REVIEW_STATE.json")
COVERAGE = os.path.join(ATLAS, "coverage.tsv")
LEDGER = os.path.join(REPO, "ledger")

# Sibling checkouts are looked up next to this one (../crypto, ...) or under
# LEAD_ATLAS_<NAME> (dashes as underscores, upper case).
REPOS = ("crypto-autoresearcher", "crypto", "cryptanalysis", "ecc-challenges")

FAMILIES = {
    "generic": "RHO",
    "ic-binary": "ICB",
    "ic-engine": "ICE",
    "ic-prime": "ICP",
    "transfer": "TRF",
    "structure": "STR",
    "exotic": "EXO",
}
CLOSED = ("closed_obstructed", "closed_known", "closed_dominated",
          "exhausted_at_scale")
OPEN = ("open_next_step", "open_blocked", "open_unexamined")
DISPOSITIONS = CLOSED + OPEN
OBSTRUCTION_KINDS = {"theorem", "proof", "measured", "literature",
                     "cost_model"}
LEAD_ID = re.compile(r"^LEAD-([A-Z]+)-[a-z0-9][a-z0-9-]{1,47}$")
LEDGER_REF = re.compile(
    r"^(H|IDEA|EV|DEC|GOAL|RQ|EXP|CORR|HO)-[A-Za-z0-9-]+$")
REQUIRED = ("id", "family", "title", "mechanism", "disposition", "evidence",
            "forecloses", "areas", "last_reviewed")

# Paths whose change after the review means "something may be new". Each
# repository lists the roots where research results and ideas land; churn in
# tooling, CI or receipts is not a new lead.
WATCHED = {
    "crypto-autoresearcher": ("ledger/hypotheses/", "ledger/proposals/",
                              "ledger/evidence/", "ledger/decisions/",
                              "ideas/", "knowledge/findings/",
                              "knowledge/open-problems/",
                              "knowledge/frontiers/ecdlp/", "problems/"),
    "crypto": ("RESEARCH_", "research_notes/", "reports/", "problems/",
               "benchmarks/README.md", "docs/ic/LEADERBOARD.md",
               "docs/bounds/FRONTIER.md"),
    "cryptanalysis": ("problems/", "research/", "docs/"),
    "ecc-challenges": ("problems/", "docs/"),
}
WATCHED_SUFFIXES = (".md", ".yaml", ".yml", ".json")


# ---------------------------------------------------------------- loading


def repo_root(name: str) -> str | None:
    if name == "crypto-autoresearcher":
        return REPO
    env = os.environ.get("LEAD_ATLAS_" + name.replace("-", "_").upper())
    cand = env or os.path.join(os.path.dirname(REPO), name)
    return cand if os.path.isdir(cand) else None


def lead_paths() -> list[str]:
    return sorted(glob.glob(os.path.join(ATLAS, "*", "LEAD-*.yaml")))


def load_leads() -> list[dict[str, Any]]:
    rows = []
    for p in lead_paths():
        with open(p, encoding="utf-8") as fh:
            row = yaml.load(fh, Loader=LOADER)
        if isinstance(row, dict):
            row["_path"] = os.path.relpath(p, REPO)
            rows.append(row)
    return rows


def load_state() -> dict[str, Any]:
    if not os.path.exists(STATE):
        return {}
    with open(STATE, encoding="utf-8") as fh:
        return json.load(fh)


def load_coverage() -> dict[str, str]:
    out: dict[str, str] = {}
    if not os.path.exists(COVERAGE):
        return out
    with open(COVERAGE, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            rec, _, lead = line.rstrip("\n").partition("\t")
            out[rec.strip()] = lead.strip()
    return out


_LEDGER_IDS: set[str] | None = None


def ledger_ids() -> set[str]:
    """Every record id under ledger/, read from file names (cheap)."""
    global _LEDGER_IDS
    if _LEDGER_IDS is None:
        ids = set()
        for root, _dirs, files in os.walk(LEDGER):
            for f in files:
                if f.endswith((".yaml", ".yml", ".json", ".md")):
                    ids.add(os.path.splitext(f)[0])
            for d in _dirs:
                if LEDGER_REF.match(d):
                    ids.add(d)
        exp = os.path.join(REPO, "experiments")
        if os.path.isdir(exp):
            ids.update(d for d in os.listdir(exp) if d.startswith("EXP-"))
        _LEDGER_IDS = ids
    return _LEDGER_IDS


def kr_ids() -> set[str]:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_frontier_map  # noqa: E402  (sibling tool, no package)
    return build_frontier_map.row_ids()


# ---------------------------------------------------------------- checking


def check_leads(rows: list[dict[str, Any]], *, strict_paths: bool = False
                ) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Missing sibling repos warn, never fail."""
    errors: list[str] = []
    warnings: list[str] = []
    ids = [str(r.get("id")) for r in rows]
    known = set(ids)
    dup = {i for i in ids if ids.count(i) > 1}
    for i in sorted(dup):
        errors.append(f"duplicate lead id {i}")
    ledger = ledger_ids()
    krs = kr_ids()
    roots = {n: repo_root(n) for n in REPOS}
    for r in rows:
        p = r["_path"]
        rid = str(r.get("id"))

        def err(msg: str, _p: str = p) -> None:
            errors.append(f"{_p}: {msg}")

        for k in REQUIRED:
            if r.get(k) in (None, "", []):
                err(f"missing required field '{k}'")
        m = LEAD_ID.match(rid)
        fam = r.get("family")
        if not m:
            err(f"id '{rid}' must match LEAD-<FAM>-<kebab-slug>")
        elif fam in FAMILIES and m.group(1) != FAMILIES[fam]:
            err(f"id code {m.group(1)} does not match family {fam} "
                f"({FAMILIES[fam]})")
        if fam not in FAMILIES:
            err(f"family '{fam}' not one of {sorted(FAMILIES)}")
        elif os.path.basename(os.path.dirname(p)) != fam:
            err(f"file is under {os.path.dirname(p)}, family is {fam}")
        if os.path.splitext(os.path.basename(p))[0] != rid:
            err("file name must equal the id")
        disp = r.get("disposition")
        if disp not in DISPOSITIONS:
            err(f"disposition '{disp}' not one of {list(DISPOSITIONS)}")
        obs = r.get("obstruction")
        nxt = r.get("next_action")
        if disp in CLOSED:
            # AGENTS.md: premature closure fails like overclaiming; a closure
            # names its obstruction.
            if not isinstance(obs, dict):
                err(f"{disp} requires an obstruction block")
            else:
                if obs.get("kind") not in OBSTRUCTION_KINDS:
                    err(f"obstruction.kind must be one of "
                        f"{sorted(OBSTRUCTION_KINDS)}")
                for k in ("statement", "revisit_when"):
                    if not str(obs.get(k) or "").strip():
                        err(f"obstruction.{k} is required")
            if disp == "closed_dominated":
                dom = str(r.get("dominated_by") or
                          (obs or {}).get("dominated_by") or "")
                if dom and dom not in known:
                    err(f"dominated_by '{dom}' is not a lead id")
        if disp in OPEN:
            if not isinstance(nxt, dict) or not str(nxt.get("step") or
                                                    "").strip():
                err(f"{disp} requires next_action.step")
            elif disp == "open_blocked" and not str(nxt.get("blocked_by")
                                                    or "").strip():
                err("open_blocked requires next_action.blocked_by")
        fc = r.get("forecloses") or []
        if not isinstance(fc, list) or len(fc) < 3:
            err("forecloses needs >= 3 phrases")
        ev = r.get("evidence") or []
        if not isinstance(ev, list):
            err("evidence must be a list")
            ev = []
        for i, e in enumerate(ev):
            if not isinstance(e, dict) or e.get("repo") not in REPOS or \
                    not e.get("path"):
                err(f"evidence[{i}] needs repo (one of {list(REPOS)}) and "
                    "path")
                continue
            root = roots.get(e["repo"])
            if root is None:
                warnings.append(f"{p}: evidence[{i}] {e['repo']} not checked "
                                "out; path unverified")
                continue
            full = os.path.join(root, str(e["path"]))
            if e.get("ref"):
                # Evidence that lives on another branch or an older commit.
                ok = subprocess.run(
                    ["git", "-C", root, "cat-file", "-e",
                     f"{e['ref']}:{e['path']}"],
                    capture_output=True).returncode == 0
                if not ok:
                    warnings.append(f"{p}: evidence[{i}] {e['repo']}:"
                                    f"{e['ref']}:{e['path']} not found "
                                    "(ref not fetched?)")
                continue
            if not os.path.exists(full):
                # A sparse checkout can leave a committed path off disk.
                tracked = _git_tracked(root, str(e["path"]))
                if not tracked:
                    msg = f"evidence[{i}] {e['repo']}:{e['path']} does not exist"
                    if strict_paths or e["repo"] == "crypto-autoresearcher":
                        err(msg)
                    else:
                        warnings.append(f"{p}: {msg}")
        for ref in r.get("ledger_refs") or []:
            ref = str(ref)
            if not LEDGER_REF.match(ref) or ref not in ledger:
                err(f"ledger_ref '{ref}' is not a ledger record on disk")
        for ref in r.get("known_results") or []:
            if str(ref) not in krs:
                err(f"known_result '{ref}' is not a KR row")
        for ref in r.get("related") or []:
            if str(ref) not in known:
                err(f"related '{ref}' is not a lead id")
    return errors, warnings


def _git_tracked(root: str, path: str) -> bool:
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", "--", path],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    return bool(out.stdout.strip())


# ---------------------------------------------------------------- coverage


def ecc_areas() -> set[str]:
    with open(os.path.join(REPO, "orchestration", "research-priority.yaml"),
              encoding="utf-8") as fh:
        doc = yaml.load(fh, Loader=LOADER)
    return {str(a) for a in doc.get("ecc_areas") or []}


# ECC areas that are not about the elliptic-curve DISCRETE LOG: isogeny-based
# schemes, rank records and signature implementations. Records there need no
# lead; the atlas lists them so the exclusion is visible, not silent.
NON_ECDLP_AREAS = {"SSI", "SSIQ", "P13", "CSIDH", "SQISIGN", "ECQ", "ECRANK",
                   "ECDSA", "EDDSA", "TECDSA"}
_H_AREA = re.compile(r"^H-([A-Z0-9]+)-")


def ecdlp_records() -> dict[str, str]:
    """{record id: area} for hypotheses and ideas in ECDLP areas."""
    areas = ecc_areas() - NON_ECDLP_AREAS
    out: dict[str, str] = {}
    for p in glob.glob(os.path.join(LEDGER, "hypotheses", "H-*.yaml")):
        rid = os.path.splitext(os.path.basename(p))[0]
        m = _H_AREA.match(rid)
        if m and m.group(1) in areas:
            out[rid] = m.group(1)
            continue
        # A hypothesis whose id prefix is not an area token (H-PFIVE under
        # RQ-PFDR, H-SEMAEV under RQ-ECDLP) belongs to its question's area.
        area = _record_area(p)
        if area in areas:
            out[rid] = area
    for p in (glob.glob(os.path.join(LEDGER, "proposals", "IDEA-*.*"))
              + glob.glob(os.path.join(LEDGER, "ideas", "IDEA-*.*"))):
        if not p.endswith((".yaml", ".yml", ".md", ".json")):
            continue
        area = _idea_area(p)
        if area in areas:
            out[os.path.splitext(os.path.basename(p))[0]] = area
    return out


_AREA_LINE = re.compile(
    r"^\s{0,4}[\"*-]*\s*(?:area|question_id|Area|Question)[\"*]*:[*]*\s*"
    r"[`'\"]?([A-Z][A-Z0-9-]*)")


# The same keys anywhere in the text, for records written as one-line JSON.
_AREA_KEY = re.compile(
    r"[\"']?(?:area|question_id)[\"']?\s*:\s*[\"'`]?([A-Z][A-Z0-9-]*)")


def _area_token(val: str) -> str:
    parts = val.split("-")
    if len(parts) > 1 and parts[0] in ("RQ", "SG", "GOAL", "Q"):
        return parts[1]
    return val


def _idea_area(path: str) -> str | None:
    """The idea's area from its first area/question_id line (no full parse).

    Falls back to a key search over the head of the file, so ideas stored as
    one-line JSON are classified too."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        head = fh.read(16384)
    for line in head.splitlines()[:80]:
        m = _AREA_LINE.match(line)
        if m:
            return _area_token(m.group(1))
    return _record_area_text(head)


def _record_area(path: str) -> str | None:
    """A ledger record's area from its first area or question_id key."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        return _record_area_text(fh.read(16384))


def _record_area_text(text: str) -> str | None:
    m = _AREA_KEY.search(text)
    return _area_token(m.group(1)) if m else None


def coverage_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    leads = {str(r.get("id")) for r in rows}
    cov = load_coverage()
    recs = ecdlp_records()
    unmapped = sorted(r for r in recs if r not in cov)
    dangling = sorted(f"{rec} -> {lead}" for rec, lead in cov.items()
                      if lead not in leads and lead != "NONE")
    by_lead: dict[str, int] = {}
    for rec, lead in cov.items():
        by_lead[lead] = by_lead.get(lead, 0) + 1
    return {"records": len(recs), "mapped": len(recs) - len(unmapped),
            "unmapped": unmapped, "dangling": dangling, "by_lead": by_lead}


# ---------------------------------------------------------------- delta


def head(root: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def changed_since(root: str, base: str, name: str) -> list[str] | None:
    """Watched paths ADDED or MODIFIED since `base`; None if base unknown."""
    if subprocess.run(["git", "-C", root, "cat-file", "-e", base + "^{commit}"],
                      capture_output=True).returncode != 0:
        return None
    out = subprocess.run(["git", "-C", root, "diff", "--name-only",
                          "--diff-filter=AM", base, "HEAD"],
                         capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        return None
    pre = WATCHED[name]
    return [p for p in out.stdout.splitlines()
            if p.startswith(pre) and p.endswith(WATCHED_SUFFIXES)
            and not p.startswith("knowledge/leads/")]


def delta() -> dict[str, Any]:
    state = load_state()
    heads = state.get("repos") or {}
    res: dict[str, Any] = {}
    for name in REPOS:
        root = repo_root(name)
        if root is None:
            res[name] = {"status": "not_checked_out"}
            continue
        base = (heads.get(name) or {}).get("commit")
        now = head(root)
        if not base:
            res[name] = {"status": "never_reviewed", "head": now}
            continue
        if base == now:
            res[name] = {"status": "current", "head": now, "changed": []}
            continue
        ch = changed_since(root, base, name)
        if ch is None:
            res[name] = {"status": "base_unreachable", "head": now,
                         "base": base}
        else:
            res[name] = {"status": "current" if not ch else "changed",
                         "head": now, "base": base, "changed": ch}
    return res


# ---------------------------------------------------------------- summary


def tally(rows: list[dict[str, Any]]) -> dict[str, int]:
    t = {d: 0 for d in DISPOSITIONS}
    for r in rows:
        if r.get("disposition") in t:
            t[r["disposition"]] += 1
    return t


def saturation(rows: list[dict[str, Any]], cov: dict[str, Any],
               dl: dict[str, Any]) -> dict[str, Any]:
    t = tally(rows)
    new_paths = sum(len(v.get("changed") or []) for v in dl.values())
    unreviewed = [n for n, v in dl.items()
                  if v.get("status") in ("never_reviewed", "base_unreachable")]
    gates = {
        "every_lead_examined": t["open_unexamined"] == 0,
        "every_record_mapped": not cov["unmapped"],
        "nothing_new_since_review": new_paths == 0 and not unreviewed,
    }
    return {"saturated": all(gates.values()), "gates": gates,
            "open_steps": t["open_next_step"], "blocked": t["open_blocked"],
            "new_paths": new_paths, "unreviewed_repos": unreviewed}


def brief() -> str:
    rows = load_leads()
    if not rows:
        return "Lead atlas: empty (knowledge/leads/ecdlp/)."
    t = tally(rows)
    cov = coverage_report(rows)
    dl = delta()
    sat = saturation(rows, cov, dl)
    state = load_state()
    closed = sum(t[d] for d in CLOSED)
    lines = [
        f"ECDLP lead atlas (knowledge/leads/ecdlp/, reviewed "
        f"{state.get('reviewed_at', 'never')}): {len(rows)} leads, "
        f"{closed} closed with a named obstruction, "
        f"{t['open_next_step']} open with a decided next step, "
        f"{t['open_blocked']} blocked, {t['open_unexamined']} unexamined. "
        f"{cov['mapped']}/{cov['records']} ECDLP ledger records mapped to a "
        "lead."]
    absent = [n for n, v in dl.items() if v.get("status") == "not_checked_out"]
    if sat["gates"]["nothing_new_since_review"]:
        seen = [n for n in REPOS if n not in absent]
        lines.append(f"Nothing in the watched paths of {', '.join(seen)} "
                     "changed since that review: every lead and idea there has "
                     "already been examined. Work is the open next steps "
                     "(`python3 tools/lead_atlas.py --render`), or a NEW lead "
                     "that `--match` does not find.")
        if absent:
            lines.append(f"Not checked out, so unverified: {', '.join(absent)}.")
    else:
        parts = []
        for n, v in dl.items():
            if v.get("changed"):
                parts.append(f"{n}: {len(v['changed'])} paths")
            elif v.get("status") in ("never_reviewed", "base_unreachable"):
                parts.append(f"{n}: {v['status']}")
        lines.append("Changed since the review: " + "; ".join(parts) +
                     ". Run `python3 tools/lead_atlas.py --delta`, fold the "
                     "new records into leads (skill `lead-atlas`), then "
                     "`--stamp`.")
    if cov["unmapped"]:
        lines.append(f"{len(cov['unmapped'])} ECDLP records have no lead: "
                     "`python3 tools/lead_atlas.py --coverage`.")
    lines.append("Before proposing an ECDLP idea: `python3 tools/lead_atlas.py "
                 "--match \"<idea>\"`; if a lead matches, advance its "
                 "next_action instead of filing a duplicate.")
    return " ".join(lines)


# ---------------------------------------------------------------- match


STOP = set("a an and are as at be by for from in into is it its of on or "
           "over the to under via with without using use than that this "
           "these those we our curve curves ecdlp elliptic".split())


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9^/+\-]+", text.lower())
            if t not in STOP and len(t) > 2}


def match(query: str, limit: int = 8) -> list[tuple[float, str, str, str]]:
    """Rank leads (and KR rows) against an idea. Low scores prove nothing."""
    q = _tokens(query)
    ql = " ".join(query.lower().split())
    out = []
    for r in load_leads():
        fc = [str(x) for x in r.get("forecloses") or []]
        hits = [x for x in fc if " ".join(x.lower().split()) in ql]
        score = (3 * len(q & _tokens(" ".join(fc)))
                 + 2 * len(q & _tokens(str(r.get("title") or "")))
                 + len(q & _tokens(str(r.get("mechanism") or "")))
                 + 5 * len(hits))
        if score:
            out.append((float(score), str(r["id"]), str(r.get("disposition")),
                        str(r.get("title"))))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_frontier_map as bfm  # noqa: E402
    for score, row, _hits in bfm.match(bfm.load_rows(), query, limit):
        out.append((score, str(row.get("id")), "known_result",
                    str(row.get("title"))))
    out.sort(key=lambda t: (-t[0], t[1]))
    return out[:limit]


# ---------------------------------------------------------------- render


def _one(x: Any) -> str:
    return " ".join(str(x or "").split()).replace("|", "\\|")


def render(rows: list[dict[str, Any]]) -> str:
    t = tally(rows)
    cov = coverage_report(rows)
    state = load_state()
    out = ["# ECDLP lead atlas", "",
           "GENERATED by `python3 tools/lead_atlas.py --render`; the rows in "
           "`knowledge/leads/ecdlp/<family>/` are the source of truth.", "",
           f"Last review stamp {state.get('reviewed_at', 'never')}. "
           f"Current committed rows: {len(rows)} leads: "
           + ", ".join(f"{k} {v}" for k, v in t.items())
           + f". Ledger coverage {cov['mapped']}/{cov['records']}.", ""]
    out += ["## Open next steps", "",
            "| lead | disposition | next step | best measured |",
            "|:--|:--|:--|:--|"]
    for r in sorted(rows, key=lambda r: (OPEN.index(r["disposition"])
                                         if r.get("disposition") in OPEN
                                         else 9, r["id"])):
        if r.get("disposition") not in OPEN:
            continue
        nx = r.get("next_action") or {}
        step = _one(nx.get("step"))
        if nx.get("blocked_by"):
            step += f" (blocked by: {_one(nx['blocked_by'])})"
        out.append(f"| `{r['id']}` {_one(r.get('title'))} | "
                   f"{r['disposition']} | {step} | "
                   f"{_one(r.get('best_measured')) or '—'} |")
    for fam in FAMILIES:
        fr = [r for r in rows if r.get("family") == fam]
        if not fr:
            continue
        out += ["", f"## {fam}", "",
                "| lead | disposition | obstruction or next step |",
                "|:--|:--|:--|"]
        for r in sorted(fr, key=lambda r: (DISPOSITIONS.index(
                r.get("disposition")) if r.get("disposition") in DISPOSITIONS
                else 99, r["id"])):
            if r.get("disposition") in CLOSED:
                o = r.get("obstruction") or {}
                why = f"[{o.get('kind')}] {_one(o.get('statement'))}"
            else:
                why = _one((r.get("next_action") or {}).get("step"))
            out.append(f"| `{r['id']}` {_one(r.get('title'))} | "
                       f"{r.get('disposition')} | {why} |")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- stamp


def reviewed_commit(root: str) -> str | None:
    """The default-branch commit the review saw: merge-base(HEAD, origin/main).

    A review runs on a work branch whose own commits may never merge; the
    default-branch commit stays reachable for every later clone. Without an
    origin/main ref the HEAD itself is pinned.
    """
    for ref in ("origin/main", "origin/master"):
        out = subprocess.run(["git", "-C", root, "merge-base", "HEAD", ref],
                             capture_output=True, text=True, timeout=60)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    return head(root)


def stamp(reviewer: str) -> dict[str, Any]:
    rows = load_leads()
    cov = coverage_report(rows)
    repos = {}
    for name in REPOS:
        root = repo_root(name)
        if root is not None:
            repos[name] = {"commit": reviewed_commit(root)}
    state = {
        "schema": "lead-atlas-review/v1",
        "reviewed_at": _dt.date.today().isoformat(),
        "reviewed_by": reviewer,
        "repos": repos,
        "leads": len(rows),
        "tally": tally(rows),
        "coverage": {"records": cov["records"], "mapped": cov["mapped"]},
        "note": ("The default-branch commit each repository was examined "
                 "at (merge-base with origin/main). --delta lists watched "
                 "paths added or modified since, ignoring knowledge/leads/."),
    }
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return state


# ---------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python3 tools/lead_atlas.py",
                                 description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--brief", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--match", metavar="TEXT")
    g.add_argument("--delta", action="store_true")
    g.add_argument("--coverage", action="store_true")
    g.add_argument("--render", action="store_true")
    g.add_argument("--stamp", metavar="REVIEWER")
    ap.add_argument("--out", metavar="PATH")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--strict-paths", action="store_true",
                    help="sibling evidence paths that do not exist fail")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.brief:
        try:
            print(brief())
        except Exception as exc:  # session start must never fail on this
            print(f"Lead atlas: summary unavailable ({exc}); run "
                  "python3 tools/lead_atlas.py --check")
        return 0
    if a.check:
        rows = load_leads()
        errors, warnings = check_leads(rows, strict_paths=a.strict_paths)
        cov = coverage_report(rows)
        for d in cov["dangling"]:
            errors.append(f"coverage.tsv: {d} is not a lead id")
        for w in warnings:
            print("warning: " + w, file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        if errors:
            print(f"{len(errors)} error(s) in {len(rows)} leads",
                  file=sys.stderr)
            return 1
        print(f"lead atlas OK: {len(rows)} leads {tally(rows)}; coverage "
              f"{cov['mapped']}/{cov['records']} "
              f"({len(cov['unmapped'])} unmapped)")
        return 0
    if a.match:
        res = match(a.match, a.limit)
        if a.json:
            print(json.dumps(res, indent=1))
        elif not res:
            print("no lead or known result shares vocabulary with this idea; "
                  "a low score is not novelty: read ATLAS.md by family")
        for score, rid, disp, title in res:
            print(f"{score:5.0f}  {rid:44s} {disp:18s} {title}")
        return 0
    if a.delta:
        dl = delta()
        if a.json:
            print(json.dumps(dl, indent=1))
            return 0
        for n, v in dl.items():
            ch = v.get("changed") or []
            print(f"{n}: {v['status']}" + (f", {len(ch)} watched paths "
                                           "added or modified" if ch else ""))
            for p in ch[:200]:
                print(f"  {p}")
            if len(ch) > 200:
                print(f"  ... {len(ch) - 200} more")
        return 0
    if a.coverage:
        cov = coverage_report(load_leads())
        if a.json:
            print(json.dumps(cov, indent=1))
            return 0
        print(f"{cov['mapped']}/{cov['records']} ECDLP records mapped")
        for r in cov["unmapped"]:
            print(f"unmapped  {r}")
        for d in cov["dangling"]:
            print(f"dangling  {d}")
        return 0
    if a.render:
        text = render(load_leads())
        if a.out:
            with open(a.out, "w", encoding="utf-8") as fh:
                fh.write(text)
        else:
            sys.stdout.write(text)
        return 0
    if a.stamp:
        st = stamp(a.stamp)
        print(json.dumps(st, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
