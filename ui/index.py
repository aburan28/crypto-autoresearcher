"""The in-memory, read-only index the dashboard serves from.

Built once at startup from `ledger/`, `experiments/` and `knowledge/`, and
rebuilt on demand (`POST /api/refresh`). It never writes to the repository:
no ledger record, no coordination state, no derived file on disk. The
dashboard is an observer of the research program and holds no authority in
it -- it cannot approve an experiment, move a hypothesis, or stand in as
evidence (AGENTS.md rule 1).

Two tiers, as `ui/scan.py` explains: header fields for every record (fast,
approximate, drives lists and search) and a real `yaml.safe_load` for the
one record a detail view asks for (exact, cached). `verified: true` on a
record payload means the caller is looking at tier 2.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import threading
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import scan
from .scan import RECORD_ID_RE, STRUCTURED, RawRecord, id_area, id_kind

# The lifecycle order records are presented in, everywhere. Not alphabetical:
# it is the order of CLAUDE.md "Typical loop", so a board read top to bottom
# reads as the program's own pipeline.
KIND_ORDER = ["GOAL", "RQ", "IDEA", "H", "EXP", "RUN", "EV", "DEC", "TASK",
              "BATCH", "CORR", "KN", "OTHER"]
KIND_LABELS = {
    "GOAL": "goals", "RQ": "questions", "IDEA": "proposals", "H": "hypotheses",
    "EXP": "experiments", "RUN": "runs", "EV": "evidence", "DEC": "decisions",
    "TASK": "handoffs", "BATCH": "checkpoints", "CORR": "corrections",
    "KN": "knowledge",
    # A handful of archived reports carry their own prefixes (`VAL-`, `RT-`,
    # `SG-`). They are real corpus content and get a bucket rather than being
    # dropped: a record the browser cannot reach may as well not exist.
    "OTHER": "other",
}

# A `KN-` identifier carries its FAMILY where every other kind carries a
# research area (`KN-FIND-001`, `KN-LIT-7580`). The families are not areas and
# must not appear in the area facet next to `ECDLP`; they get their own.
KNOWLEDGE_FAMILIES = {
    "FIND": "findings", "OPEN": "open problems", "TECH": "techniques",
    "LIT": "literature", "GATHER": "gathers",
}

# What reads as a record's "title" and "status" in a list, per kind.
#
# The families do not share a vocabulary and forcing them to would lose the
# most useful column on each: a decision's verdict lives in `decision`
# (expand / refine / reject_scoped / ...), an evidence record's in
# `strength` (replicated / suggestive / ...), and neither has a `status`
# field at all. A list that showed "--" for every decision and every
# evidence record would be technically correct and useless.
#
# Each tuple also carries the names used by the handful of FLAT records (no
# wrapping root key) that a later schema emitted -- `decision_type`,
# `what_was_measured`. Same family, different spelling; a reader does not
# care which schema generation wrote the file.
TITLE_BY_KIND = {
    "EV": ("scope_statement", "conclusion", "summary", "finding",
           "what_was_measured", "critical_finding", "title"),
    "DEC": ("decision_label", "context", "rationale", "summary", "title"),
    "TASK": ("objective", "uncertainty_reduced", "title"),
    "CORR": ("reason", "field", "title"),
    "H": ("statement", "title", "mechanism"),
    "IDEA": ("title", "claim", "mechanism"),
    "BATCH": ("summary", "title"),
}
STATUS_BY_KIND = {
    "DEC": ("decision", "decision_type", "status"),
    "EV": ("strength", "status"),
    "IDEA": ("status", "novelty_status"),
}

# Goal statuses. `paused` and `blocked` are absent on purpose and are flagged
# as integrity problems if they appear: CLAUDE.md rule 10 forbids both by name.
TERMINAL_GOAL_STATUSES = {"completed", "closed_at_budget", "cancelled"}
FORBIDDEN_GOAL_STATUSES = {"paused", "blocked"}


def _load_ecc_policy(repo: Path):
    """Import `tools/ecc_priority.py` for the declared ECC area set.

    CLAUDE.md rule 11: the ECC set is declared once in
    `orchestration/research-priority.yaml`, read through that module, and is
    NEVER inferred from an identifier prefix. So the UI imports the module
    rather than re-deriving anything. If it cannot be loaded the UI degrades
    to showing no ECC ordering at all, which is honest, rather than guessing
    a set, which would not be.
    """
    path = repo / "tools" / "ecc_priority.py"
    if not path.is_file():
        return set(), "tools/ecc_priority.py not found"
    previous = sys.dont_write_bytecode
    try:
        # Importing a module normally writes `__pycache__`. That is the one
        # way this tool could touch the repository, and it must not: the
        # dashboard's read-only property is asserted in the tests.
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location("_ui_ecc_priority", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules.setdefault("_ui_ecc_priority", module)
        spec.loader.exec_module(module)
        return set(module.ecc_areas(module.load_policy(repo / "orchestration" / "research-priority.yaml"))), None
    except Exception as exc:                          # noqa: BLE001 - reported, not raised
        return set(), f"{type(exc).__name__}: {exc}"
    finally:
        sys.dont_write_bytecode = previous


@dataclass(slots=True)
class Record:
    record_id: str
    kind: str
    path: str
    root_key: str | None
    title: str
    status: str
    date: str
    area: str | None
    fields: dict[str, str]
    refs: frozenset[str]
    haystack: bytes = b""            # lowercased text, for substring search
    size: int = 0

    def summary(self, index: "ResearchIndex") -> dict[str, Any]:
        return {
            "id": self.record_id,
            "kind": self.kind,
            "path": self.path,
            "title": self.title,
            "status": self.status,
            "date": self.date,
            "area": self.area,
            "ecc": self.area in index.ecc_areas if self.area else False,
            "refs": len(self.refs),
            "backlinks": len(index.backlinks.get(self.record_id, ())),
        }


@dataclass(slots=True)
class Goal:
    record_id: str
    title: str
    status: str
    objective: str
    next_action: str
    owner: str
    area: str | None
    ecc: bool
    path: str
    question_ids: list[str]
    active_hypothesis_ids: list[str]
    current_batch_id: str
    updated_at: str
    created_at: str
    budget: dict[str, Any]
    completion_criteria: list[Any]
    impediments: list[Any]
    checkpoints: list[dict[str, Any]]
    sharded: bool
    flags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Experiment:
    record_id: str
    title: str
    status: str
    area: str | None
    path: str
    hypothesis_id: str
    question_id: str
    frozen: str
    execution_authorized: str
    runs: list[dict[str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Findings, open problems and obstructions: the program's OUTPUT.
#
# Goals are fully parsed because the portfolio board is load-bearing. The
# findings board is load-bearing for the opposite reader -- the one asking
# "what has this program actually established?" -- and gets the same
# treatment. `knowledge/findings/` and `knowledge/open-problems/` are ~130
# small markdown files: their front matter is parsed exactly and the claim
# each one makes is excerpted from its body, so a board can show what was
# found rather than only what it was called. Literature (~7,900 entries)
# stays on the shallow tier; nobody reads a literature board.
#
# An obstruction is the quantified form of a negative result (AGENTS.md
# "Closure standard"; templates/research-records.md `evidence.obstruction`):
# what blocks an approach, as a measured number over a stated scope. It lives
# nested inside an evidence record, below what the shallow scan can see, so
# the few dozen records that carry one are parsed exactly.
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class Finding:
    record_id: str
    title: str
    path: str
    added: str
    status: str                  # current | superseded | withdrawn
    proof_status: str
    proof_refs: int
    confidence: str
    evidence_level: str
    claim_tier: str
    tags: list[str]
    superseded_by: str
    withdrawn_by: str
    refs: list[str]              # ledger identifiers named in the front matter
    goal_ids: list[str]
    areas: list[str]             # every research area its citations reach
    area: str | None             # the one it is filed under on a board
    excerpt: str
    non_claim: str = ""          # what the entry says it does NOT establish
    error: str | None = None     # front matter missing or unparseable


@dataclass(slots=True)
class OpenProblem:
    record_id: str
    title: str
    path: str
    added: str
    status: str
    tags: list[str]
    refs: list[str]
    goal_ids: list[str]
    areas: list[str]
    area: str | None
    statement: str
    current_state: str
    resolution: str
    error: str | None = None


@dataclass(slots=True)
class Obstruction:
    evidence_id: str
    hypothesis_id: str
    goal_id: str
    direction: str
    strength: str
    claim_tier: str
    statement: str
    quantity: str
    value: str
    scope: str
    measured_by: list[str]
    resource_examined: bool | None
    resource_reading: str
    spawned_ids: list[str]


_FRONT_MATTER_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)


def split_front_matter(text: str) -> tuple[dict | None, str, str | None]:
    """`(front_matter, markdown_body, error)`, with an EXACT parse of the block.

    The shallow `scan.front_matter` reads only top-level scalars and is what
    drives the lists; this is tier 2 for a knowledge entry, used where a
    reader will act on the values (the findings board, a detail view).
    """
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        return None, text, "no front matter"
    body = text[m.end():]
    try:
        front = yaml.safe_load(m.group(1))
    except Exception as exc:                          # noqa: BLE001 - reported, not raised
        return None, body, f"{type(exc).__name__}: {str(exc).splitlines()[0][:160]}"
    if not isinstance(front, dict):
        return None, body, "front matter is not a mapping"
    return front, body, None


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# Sections are the `#`/`##` divisions. A `###` is a subdivision of the section
# it sits in: an entry whose "Finding" is a lead sentence followed by two
# `###` halves has one finding, not a one-line finding and two strays.
_SECTION_RE = re.compile(r"^(#{1,2})\s+(.*?)\s*#*\s*$")


def md_sections(body: str) -> list[tuple[str, str]]:
    """`[(heading, text)]` in document order; text before any heading has ''."""
    sections: list[tuple[str, list[str]]] = [("", [])]
    fenced = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            sections[-1][1].append(line)
            continue
        m = None if fenced else _SECTION_RE.match(line)
        if m:
            sections.append((m.group(2).strip(), []))
        else:
            sections[-1][1].append(line)
    return [(heading, "\n".join(lines).strip()) for heading, lines in sections]


_MD_STRIP = (
    (re.compile(r"```.*?```", re.S), " "),                       # fenced code
    (re.compile(r"!\[[^\]]*\]\([^)]*\)"), ""),                   # images
    (re.compile(r"\[([^\]]+)\]\([^)]*\)"), r"\1"),               # links -> their text
    (re.compile(r"`([^`]*)`"), r"\1"),
    (re.compile(r"(\*\*|__)(.+?)\1", re.S), r"\2"),
    (re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", re.S), r"\1"),
    (re.compile(r"^[ \t]{0,3}>[ \t]?", re.M), ""),               # blockquote marks
    (re.compile(r"^[ \t]{0,3}(?:[-*+]|\d+[.)])[ \t]+", re.M), ""),  # list marks
)


def md_plain(text: str) -> str:
    """Markdown reduced to its words. Approximate on purpose: it feeds a
    one-paragraph excerpt, not a renderer."""
    for pattern, repl in _MD_STRIP:
        text = pattern.sub(repl, text)
    return text


def md_paragraphs(text: str) -> list[str]:
    out: list[str] = []
    for para in re.split(r"\n\s*\n", md_plain(text)):
        # Sub-headings are signposts, not prose; they do not belong in a claim.
        prose = [line for line in para.splitlines() if not _HEADING_RE.match(line)]
        flat = re.sub(r"\s+", " ", " ".join(prose)).strip()
        if flat and not flat.startswith(("|", "---", "<!--")):
            out.append(flat)
    return out


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:(") + "…"


# Section headings that carry an entry's own statement of itself, best first.
# Matched by prefix after a leading "3." style number is dropped.
FINDING_STATEMENT_HEADINGS = (
    "finding", "the finding", "statement", "scoped claim", "key claims", "claim",
    "result", "what this says", "summary",
)
OPEN_PROBLEM_STATEMENT_HEADINGS = ("statement", "the open question", "question")
# Where an entry says what it does NOT establish. The corpus's honesty
# discipline lives in these sections; a card that shows the claim without
# them shows half the finding.
NON_CLAIM_HEADINGS = (
    "not claimed", "non-claim", "non claims", "what this does not", "limits",
    "scope and limit", "what a successor must", "what this says",
)


def statement_excerpt(body: str, prefer=FINDING_STATEMENT_HEADINGS, limit: int = 700) -> str:
    """The entry's own statement of what it establishes, as plain text.

    Prefers the section an author labelled as the statement, and within it a
    blockquote if there is one -- that is the convention here for "the finding,
    in one sentence". Falls back to the first prose paragraph. Never invents
    a summary: everything returned is the entry's own words, clipped.
    """
    ranked = []
    for pos, (heading, text) in enumerate(md_sections(body)):
        key = re.sub(r"^\d+[.)]?\s*", "", heading).strip().lower()
        rank = next((i for i, p in enumerate(prefer) if key.startswith(p)), len(prefer))
        ranked.append((rank, pos, text))
    for _, _, text in sorted(ranked):
        quote: list[str] = []
        for line in text.splitlines():
            if line.lstrip().startswith(">"):
                quote.append(re.sub(r"^[ \t]{0,3}>[ \t]?", "", line))
            elif quote:
                break                                 # first blockquote only
        paragraphs = md_paragraphs("\n".join(quote)) if quote else md_paragraphs(text)
        if not paragraphs:
            continue
        # Join, then clip. Authors here often open a section with a one-line
        # framing sentence ("Two halves, of equal weight.") and put the claim
        # in the paragraph after it; stopping at the first paragraph kept the
        # framing and dropped the claim.
        return _clip(" ".join(paragraphs), limit)
    return ""


def section_text(body: str, prefixes, limit: int = 900) -> str:
    """Plain text of the first section whose heading starts with a prefix."""
    for heading, text in md_sections(body):
        key = re.sub(r"^\d+[.)]?\s*", "", heading).strip().lower()
        if any(key.startswith(p) for p in prefixes):
            return _clip(" ".join(md_paragraphs(text)), limit)
    return ""


def _first_heading(body: str) -> str:
    for line in body.splitlines():
        m = _HEADING_RE.match(line)
        if m:
            return m.group(2).strip()
    return ""


def _ordered_ids(text: str, exclude: str | None = None) -> list[str]:
    """Program identifiers in `text`, first mention first, deduplicated."""
    return [i for i in dict.fromkeys(RECORD_ID_RE.findall(text)) if i != exclude]


def _areas_of(ids: list[str]) -> list[str]:
    """Research areas of the ledger records named. A cited `KN-` entry's
    second segment is a family (TECH, LIT), not an area, and is skipped."""
    return sorted({a for a in (id_area(i) for i in ids if id_kind(i) != "KN") if a})


def _primary_area(goal_ids: list[str], refs: list[str]) -> str | None:
    """The one area an entry is filed under on a board.

    Its goal's area when it has a goal; otherwise the area of the first
    ledger record it cites, in the order the author cited them. An entry can
    reach several areas through its citations, and `areas` keeps all of
    them, but a board that showed it under each would count it several
    times.
    """
    for goal_id in goal_ids:
        if id_area(goal_id):
            return id_area(goal_id)
    for ref in refs:
        if id_kind(ref) != "KN" and id_area(ref):
            return id_area(ref)
    return None


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _as_list(value: Any) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _text(value: Any, limit: int = 4000) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()[:limit]


class ResearchIndex:
    """A snapshot of the corpus. Immutable once built; rebuild to refresh."""

    def __init__(self, repo: Path) -> None:
        self.repo = repo.resolve()
        self.records: dict[str, Record] = {}
        self.by_kind: dict[str, list[Record]] = defaultdict(list)
        self.backlinks: dict[str, set[str]] = defaultdict(set)
        self.goals: list[Goal] = []
        self.experiments: list[Experiment] = []
        self.findings: list[Finding] = []
        self.open_problems: list[OpenProblem] = []
        self.obstructions: list[Obstruction] = []
        self.ecc_areas: set[str] = set()
        self.ecc_error: str | None = None
        self.integrity: dict[str, list] = {}
        self.built_at: float = 0.0
        self.build_seconds: float = 0.0
        self.duplicate_paths: dict[str, list[str]] = {}
        self._full_cache: dict[str, Any] = {}
        self._lock = threading.Lock()
        # The exact-parse sweep is slow (~55 s on the reference corpus) and
        # runs behind the served index rather than in front of it. See
        # `start_deep_scan`.
        self.deep_scan_state = "idle"
        self.deep_scan_seconds = 0.0

    # -- build ------------------------------------------------------------
    def build(self) -> "ResearchIndex":
        started = time.time()
        self.ecc_areas, self.ecc_error = _load_ecc_policy(self.repo)

        raw = scan.scan_ledger(self.repo)
        raw += scan.scan_knowledge(self.repo)
        raw += self._scan_experiment_specs()

        seen: dict[str, list[str]] = defaultdict(list)
        for item in raw:
            seen[item.record_id].append(item.path)
            self._add(item)
        self.duplicate_paths = {k: v for k, v in seen.items() if len(v) > 1}

        for record in self.records.values():
            for ref in record.refs:
                self.backlinks[ref].add(record.record_id)

        self._build_goals()
        self._build_experiments()
        self._build_findings()
        self._build_open_problems()
        self._build_obstructions()
        self._check_integrity()
        self.start_deep_scan()

        for bucket in self.by_kind.values():
            bucket.sort(key=lambda r: (r.date or "", r.record_id), reverse=True)
        self.built_at = time.time()
        self.build_seconds = self.built_at - started
        return self

    def _add(self, item: RawRecord) -> None:
        fields = item.fields
        kind = item.kind if item.kind in KIND_LABELS else "OTHER"
        title = scan._pick(fields, TITLE_BY_KIND.get(kind, ()) + scan.TITLE_FIELDS)
        status = _short_status(fields, STATUS_BY_KIND.get(kind, ("status",)))
        record = Record(
            record_id=item.record_id,
            kind=kind,
            path=item.path,
            root_key=item.root_key,
            title=title,
            status=status,
            date=scan._pick(fields, scan.DATE_FIELDS),
            area=id_area(item.record_id),
            fields=fields,
            refs=item.refs,
            haystack=(item.record_id + " " + title + " " + item.text).lower().encode(
                "utf-8", "replace"),
            size=len(item.text),
        )
        # A duplicated identifier keeps its first sighting; the collision is
        # reported under integrity rather than silently resolved.
        if record.record_id not in self.records:
            self.records[record.record_id] = record
            self.by_kind[record.kind].append(record)

    def _scan_experiment_specs(self) -> list[RawRecord]:
        out = []
        base = self.repo / "experiments"
        if not base.is_dir():
            return out
        for spec in sorted(base.glob("*/specification.yaml")):
            try:
                out.append(scan.scan_file(spec, self.repo))
            except OSError:
                continue
        return out

    # -- goals ------------------------------------------------------------
    def _goal_paths(self) -> list[tuple[Path, bool]]:
        base = self.repo / "ledger" / "goals"
        if not base.is_dir():
            return []
        flat = [(p, False) for p in sorted(base.glob("GOAL-*.yaml"))]
        sharded = [(p, True) for p in sorted(base.glob("GOAL-*/goal.yaml"))]
        return flat + sharded

    def _build_goals(self) -> None:
        """Goals are FULLY parsed, not header-scanned.

        There are ~100 of them, they carry the numbers a reader will act on
        (budget, criteria, impediments), and the portfolio board is the view
        most likely to be trusted without opening the record. Approximating
        it would be the wrong trade.
        """
        for path, sharded in self._goal_paths():
            goal_id = path.parent.name if sharded else path.stem
            try:
                doc = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
                body = (doc or {}).get("research_goal", doc) if isinstance(doc, dict) else {}
                if not isinstance(body, dict):
                    body = {}
                flags: list[str] = []
            except Exception as exc:                  # noqa: BLE001
                body, flags = {}, [f"unparseable: {type(exc).__name__}"]

            status = _text(body.get("status")) or ("unparseable" if flags else "")
            if status in FORBIDDEN_GOAL_STATUSES:
                flags.append(
                    f"status '{status}' is forbidden (CLAUDE.md rule 10: goals are never paused)")
            area = id_area(goal_id)
            budget = body.get("campaign_budget") if isinstance(body.get("campaign_budget"), dict) else {}
            if area in self.ecc_areas and status not in TERMINAL_GOAL_STATUSES:
                for bounded in ("maximum_batches", "total_wall_clock_seconds"):
                    if budget.get(bounded) is not None:
                        flags.append(
                            f"ECC goal with bounded {bounded}={budget[bounded]!r} "
                            "(CLAUDE.md rule 11 requires null)")

            self.goals.append(Goal(
                record_id=_text(body.get("id")) or goal_id,
                title=_text(body.get("title"), 400),
                status=status,
                objective=_text(body.get("objective"), 6000),
                next_action=_text(body.get("next_action"), 6000),
                owner=_text(body.get("owner")),
                area=area,
                ecc=area in self.ecc_areas if area else False,
                path=str(path.relative_to(self.repo)),
                question_ids=[str(q) for q in _as_list(body.get("question_ids"))],
                active_hypothesis_ids=[str(h) for h in _as_list(body.get("active_hypothesis_ids"))],
                current_batch_id=_text(body.get("current_batch_id")),
                updated_at=_text(body.get("updated_at")),
                created_at=_text(body.get("created_at")),
                budget={k: budget.get(k) for k in (
                    "maximum_batches", "total_wall_clock_seconds", "max_concurrent",
                    "spent_wall_clock_seconds", "batches_used")},
                completion_criteria=_as_list(body.get("completion_criteria")),
                impediments=_as_list(body.get("impediments")),
                checkpoints=self._goal_checkpoints(path, sharded, body),
                sharded=sharded,
                flags=flags,
            ))
        self.goals.sort(key=self._goal_sort_key)

    def _goal_sort_key(self, goal: Goal):
        # CLAUDE.md rule 11: ECC goals are selected before all others at every
        # selection point. The board is a selection point, so ECC sorts first;
        # then active before terminal, then most recently updated.
        return (
            not goal.ecc,
            goal.status in TERMINAL_GOAL_STATUSES,
            goal.status != "active",
            _neg_date(goal.updated_at),
            goal.record_id,
        )

    def _goal_checkpoints(self, path: Path, sharded: bool, body: dict) -> list[dict[str, Any]]:
        """Batch checkpoints, from either layout.

        Sharded goals keep one write-once file per batch under
        `checkpoints/`; flat goals keep an in-record list. Both are read so a
        half-converted portfolio still renders (CLAUDE.md: "convert a goal
        when you next have it open, and never in bulk").
        """
        out: list[dict[str, Any]] = []
        if sharded:
            for shard in sorted((path.parent / "checkpoints").glob("*.yaml")):
                try:
                    doc = yaml.safe_load(shard.read_text(encoding="utf-8", errors="replace")) or {}
                except Exception:                     # noqa: BLE001
                    out.append({"batch_id": shard.stem, "error": "unparseable"})
                    continue
                entry = doc.get("checkpoint", doc) if isinstance(doc, dict) else {}
                if not isinstance(entry, dict):
                    entry = {}
                out.append({
                    "batch_id": _text(entry.get("batch_id")) or shard.stem,
                    "recorded_at": _text(entry.get("recorded_at") or entry.get("completed_at")),
                    "summary": _text(entry.get("summary") or entry.get("outcome"), 2000),
                    "path": str(shard.relative_to(self.repo)),
                })
        for entry in _as_list(body.get("batch_checkpoints")) + _as_list(body.get("checkpoints")):
            if isinstance(entry, dict):
                out.append({
                    "batch_id": _text(entry.get("batch_id") or entry.get("id")),
                    "recorded_at": _text(entry.get("recorded_at") or entry.get("completed_at")),
                    "summary": _text(entry.get("summary") or entry.get("outcome"), 2000),
                    "path": None,
                })
        return out

    # -- experiments ------------------------------------------------------
    def _build_experiments(self) -> None:
        base = self.repo / "experiments"
        if not base.is_dir():
            return
        for spec in sorted(base.glob("*/specification.yaml")):
            record = self.records.get(spec.parent.name)
            fields = record.fields if record else {}
            runs = []
            for run_dir in sorted((spec.parent / "runs").glob("*")):
                # `runs/` holds run DIRECTORIES. A `.gitkeep` placeholder is
                # how an experiment with no runs at all is committed, and
                # counting it as a run made 232 unexecuted contracts look
                # like they had produced something. An `_`-prefixed directory
                # is shared code the runs import, not a run either.
                if not run_dir.is_dir() or run_dir.name[:1] in (".", "_"):
                    continue
                runs.append({"id": run_dir.name, "status": _run_status(run_dir)})
            self.experiments.append(Experiment(
                record_id=spec.parent.name,
                title=fields.get("title", ""),
                status=fields.get("status", ""),
                area=id_area(spec.parent.name),
                path=str(spec.relative_to(self.repo)),
                hypothesis_id=fields.get("hypothesis_id", ""),
                question_id=fields.get("question_id", ""),
                frozen=fields.get("frozen", ""),
                execution_authorized=fields.get("execution_authorized", ""),
                runs=runs,
            ))
        self.experiments.sort(key=lambda e: (not e.runs, e.record_id))

    # -- findings, open problems, obstructions ------------------------------
    def _knowledge_family(self, family: str) -> list[tuple[Path, str, dict, str, str | None]]:
        """Every entry of one `knowledge/<family>/` directory, exactly parsed:
        `(path, text, front_matter, body, error)`."""
        base = self.repo / "knowledge" / family
        if not base.is_dir():
            return []
        out = []
        for path in sorted(base.glob("*.md")):
            text = _read(path)
            front, body, error = split_front_matter(text)
            out.append((path, text, front or {}, body, error))
        return out

    def _build_findings(self) -> None:
        for path, text, front, body, error in self._knowledge_family("findings"):
            record_id = _text(front.get("id")) or path.stem
            head = self.records.get(record_id)
            title = (_text(front.get("title"), 600) or _first_heading(body)
                     or (head.title if head else "") or record_id)
            refs = _ordered_ids(text[:len(text) - len(body)], exclude=record_id)
            superseded_by = _text(front.get("superseded_by"))
            withdrawn_by = _text(front.get("withdrawn_by"))
            raw_status = _text(front.get("status"))
            if withdrawn_by or raw_status.lower().startswith("withdrawn"):
                status = "withdrawn"
            elif superseded_by:
                status = "superseded"
            else:
                status = "current"
            goal_ids = self._attribute_goals(record_id, refs, text)
            self.findings.append(Finding(
                record_id=record_id,
                title=title,
                path=str(path.relative_to(self.repo)),
                added=_text(front.get("added")),
                status=status,
                proof_status=_text(front.get("proof_status"), 60),
                proof_refs=len(_as_list(front.get("proof_refs"))),
                confidence=_text(front.get("confidence"), 120),
                evidence_level=_text(front.get("evidence_level"), 120),
                claim_tier=_text(front.get("claim_tier"), 80),
                tags=[str(t) for t in _as_list(front.get("tags"))][:24],
                superseded_by=superseded_by,
                withdrawn_by=withdrawn_by,
                refs=refs,
                goal_ids=goal_ids,
                areas=_areas_of(refs + goal_ids),
                area=_primary_area(goal_ids, refs),
                excerpt=statement_excerpt(body),
                non_claim=section_text(body, NON_CLAIM_HEADINGS, 420),
                error=error,
            ))
        self.findings.sort(key=lambda f: (_neg_date(f.added), f.record_id))

    def _attribute_goals(self, record_id: str, refs: list[str], text: str) -> list[str]:
        """The goals a knowledge entry belongs to.

        A finding names its goal in about half the corpus. The rest are
        reached through the evidence or decision that promoted them, which
        carry `goal_id`, or failing that through whichever record cites the
        entry and carries one. Reported as "goals named", not "owner": an
        entry may mention a sibling campaign's goal in passing.
        """
        goals = [r for r in _ordered_ids(text) if id_kind(r) == "GOAL"]
        for pool in (refs, sorted(self.backlinks.get(record_id, ()))):
            if goals:
                break
            for other in pool:
                record = self.records.get(other)
                goal_id = record.fields.get("goal_id", "") if record else ""
                if goal_id and goal_id != STRUCTURED and id_kind(goal_id) == "GOAL":
                    goals.append(goal_id)
        return list(dict.fromkeys(goals))

    def _build_open_problems(self) -> None:
        for path, text, front, body, error in self._knowledge_family("open-problems"):
            record_id = _text(front.get("id")) or path.stem
            head = self.records.get(record_id)
            refs = _ordered_ids(text[:len(text) - len(body)], exclude=record_id)
            goal_ids = self._attribute_goals(record_id, refs, text)
            self.open_problems.append(OpenProblem(
                record_id=record_id,
                title=(_text(front.get("title"), 600) or _first_heading(body)
                       or (head.title if head else "") or record_id),
                path=str(path.relative_to(self.repo)),
                added=_text(front.get("added")),
                status=_text(front.get("status"), 60),
                tags=[str(t) for t in _as_list(front.get("tags"))][:24],
                refs=refs,
                goal_ids=goal_ids,
                areas=_areas_of(refs + goal_ids),
                area=_primary_area(goal_ids, refs),
                statement=statement_excerpt(body, OPEN_PROBLEM_STATEMENT_HEADINGS),
                current_state=section_text(body, ("current state",)),
                resolution=section_text(
                    body, ("what would resolve", "what would close", "cheapest next step")),
                error=error,
            ))
        self.open_problems.sort(key=lambda p: (p.status != "open", _neg_date(p.added), p.record_id))

    def _build_obstructions(self) -> None:
        """Exactly parse the evidence records that carry an `obstruction` block.

        Cheap: the shallow scan already holds every record's text, so only the
        few dozen that mention the key are parsed, and `full_record` caches
        the parse for the detail view.
        """
        for record in self.by_kind.get("EV", []):
            if b"obstruction:" not in record.haystack:
                continue
            parsed, _error = self.full_record(record.record_id)
            body = parsed.get("evidence", parsed) if isinstance(parsed, dict) else None
            block = body.get("obstruction") if isinstance(body, dict) else None
            if not isinstance(block, dict) or not _text(block.get("statement")):
                continue
            check = block.get("resource_check")
            check = check if isinstance(check, dict) else {}
            examined = check.get("examined")
            self.obstructions.append(Obstruction(
                evidence_id=record.record_id,
                hypothesis_id=_text(body.get("hypothesis_id"), 60),
                goal_id=_text(body.get("goal_id"), 60),
                direction=_text(body.get("direction"), 40),
                strength=_text(body.get("strength"), 40),
                claim_tier=_text(body.get("claim_tier"), 60),
                statement=_text(block.get("statement"), 1200),
                quantity=_text(block.get("quantity"), 600),
                value=_text(block.get("value"), 600),
                scope=_text(block.get("scope"), 800),
                measured_by=[str(x) for x in _as_list(block.get("measured_by"))][:20],
                resource_examined=examined if isinstance(examined, bool) else None,
                resource_reading=_text(check.get("reading"), 800),
                spawned_ids=[str(x) for x in _as_list(check.get("spawned_ids"))][:20],
            ))
        self.obstructions.sort(
            key=lambda o: (_neg_date(self.records[o.evidence_id].date), o.evidence_id))

    # -- integrity --------------------------------------------------------
    def _check_integrity(self) -> None:
        """Flag, never fix.

        Every item here is something `/research-status` step 3 asks a reader
        to notice. The UI reports it and stops: a record is immutable and a
        correction supersedes it (AGENTS.md rule 2), which is a Coordinator
        act, not a dashboard's.
        """
        id_mismatch = [
            {"path": r.path, "id": r.record_id, "stem": Path(r.path).stem}
            for r in self.records.values()
            if r.path.startswith("ledger/")
            and Path(r.path).name != "goal.yaml"
            and Path(r.path).stem != r.record_id
        ]

        # A dangling reference is an identifier that is well-formed for a
        # ledger kind and named by some record, but has no record of its own.
        # RUN, BATCH and TASK identifiers are excluded: runs live under
        # `experiments/*/runs/`, batches under `coordination/`, and handoffs
        # legitimately name tasks that no ledger file records.
        resolvable = {"GOAL", "RQ", "H", "EXP", "EV", "DEC", "IDEA", "KN"}
        dangling: Counter = Counter()
        for record in self.records.values():
            for ref in record.refs:
                if id_kind(ref) in resolvable and ref not in self.records:
                    dangling[ref] += 1

        self.integrity = {
            # Filled in by `start_deep_scan`; `unparseable_state` says whether
            # this list is trustworthy yet. An empty list under state
            # "running" means "not measured", NOT "nothing broken", and the
            # UI must render it that way -- reporting a clean sweep that has
            # not happened would be the exact failure AGENTS.md rule 5 names.
            "unparseable": [],
            "unparseable_state": "pending",
            "dangling_refs_total": len(dangling),
            "duplicate_ids": [
                {"id": k, "paths": v} for k, v in sorted(self.duplicate_paths.items())],
            "id_path_mismatch": sorted(id_mismatch, key=lambda d: d["path"]),
            "dangling_refs": [
                {"id": k, "cited_by": n} for k, n in dangling.most_common(500)],
            "goal_flags": [
                {"id": g.record_id, "flags": g.flags} for g in self.goals if g.flags],
            "ecc_policy_error": self.ecc_error,
        }

    def start_deep_scan(self) -> None:
        """Exactly parse every ledger record, in the background.

        The header scan cannot tell a malformed record from a well-formed
        one -- it is line-oriented and reads what it recognizes. Only a real
        parse can, and a real parse of the whole ledger costs about a minute,
        which no reader should wait on before seeing the portfolio. So the
        dashboard serves immediately and this sweep lands under
        `/api/integrity` when it finishes.
        """
        if self.deep_scan_state == "running":
            return
        self.deep_scan_state = "running"
        self.integrity["unparseable_state"] = "running"
        threading.Thread(target=self._deep_scan, daemon=True, name="ui-deep-scan").start()

    def _deep_scan(self) -> None:
        started = time.time()
        found: list[dict[str, str]] = []
        for path in sorted((self.repo / "ledger").rglob("*.yaml")):
            try:
                yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
            except Exception as exc:                  # noqa: BLE001
                found.append({
                    "path": str(path.relative_to(self.repo)),
                    "error": str(exc).splitlines()[0][:200],
                })
        with self._lock:
            self.integrity["unparseable"] = found
            self.integrity["unparseable_state"] = "complete"
            self.deep_scan_seconds = time.time() - started
            self.deep_scan_state = "complete"

    # -- queries ----------------------------------------------------------
    def full_record(self, record_id: str) -> tuple[Any, str | None]:
        """Tier 2: the real parse. Cached, because it is the expensive one."""
        with self._lock:
            if record_id in self._full_cache:
                return self._full_cache[record_id]
        record = self.records.get(record_id)
        if record is None:
            return None, "unknown record"
        path = self.repo / record.path
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            if path.suffix == ".yaml":
                parsed = (yaml.safe_load(text), None)
            elif path.suffix == ".md":
                # A knowledge entry's exact form is its front matter plus its
                # body. The body is the content -- an entry page without it
                # is a title and nothing else -- so it travels with the record.
                front, body, error = split_front_matter(text)
                parsed = ({"front_matter": front or {}, "markdown": body}, error)
            else:
                parsed = (None, None)
        except Exception as exc:                      # noqa: BLE001
            parsed = (None, f"{type(exc).__name__}: {exc}")
        with self._lock:
            self._full_cache[record_id] = parsed
        return parsed

    def raw_text(self, record_id: str) -> str:
        record = self.records.get(record_id)
        if record is None:
            return ""
        try:
            return (self.repo / record.path).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"# unreadable: {exc}"

    def search(self, query: str, kinds=None, areas=None, statuses=None,
               limit: int = 200, offset: int = 0) -> tuple[list[Record], int]:
        needle = query.strip().lower().encode("utf-8", "replace")
        hits: list[Record] = []
        for record in self.records.values():
            if kinds and record.kind not in kinds:
                continue
            if areas and record.area not in areas:
                continue
            if statuses and record.status not in statuses:
                continue
            if needle and needle not in record.haystack:
                continue
            hits.append(record)
        hits.sort(key=lambda r: (_rank(r, needle), _neg_date(r.date), r.record_id))
        return hits[offset:offset + limit], len(hits)

    def facets(self) -> dict[str, Any]:
        kinds = Counter(r.kind for r in self.records.values())
        # A KN identifier's second segment is its family, not a research area
        # (`KN-LIT-7580`), and 7,900 literature entries under an "area" called
        # LIT drowned the real areas. Families get their own facet.
        areas = Counter(r.area for r in self.records.values() if r.area and r.kind != "KN")
        families = Counter(r.area for r in self.records.values() if r.area and r.kind == "KN")
        statuses = Counter(r.status for r in self.records.values() if r.status)
        return {
            "kinds": [
                {"key": k, "label": KIND_LABELS.get(k, k), "count": kinds.get(k, 0)}
                for k in KIND_ORDER if kinds.get(k)],
            "areas": [
                {"key": a, "count": n, "ecc": a in self.ecc_areas}
                for a, n in sorted(areas.items(), key=lambda kv: (-kv[1], kv[0]))],
            "knowledge": [
                {"key": f, "label": KNOWLEDGE_FAMILIES.get(f, f.lower()), "count": n}
                for f, n in sorted(families.items(), key=lambda kv: (-kv[1], kv[0]))],
            "statuses": [
                {"key": s, "count": n}
                for s, n in sorted(statuses.items(), key=lambda kv: (-kv[1], kv[0]))],
        }

    def neighbourhood(self, record_id: str) -> dict[str, Any]:
        """One hop out and one hop in, grouped by kind.

        Deliberately one hop. The link graph is dense enough that two hops
        from an active goal reaches most of the corpus, which shows a reader
        nothing.
        """
        record = self.records.get(record_id)
        if record is None:
            return {"out": [], "in": []}
        out = [self.records[r].summary(self) for r in sorted(record.refs) if r in self.records]
        inbound = [self.records[r].summary(self)
                   for r in sorted(self.backlinks.get(record_id, ())) if r in self.records]
        return {"out": out, "in": inbound}


# A status is a controlled token (`active`, `refine`, `replicated`). A few
# records built on a later schema put a sentence in the field instead. Such a
# value is not a status, and rendering it as one turns a table row into a
# paragraph, so it is dropped here and left to be found in the record body.
MAX_STATUS_CHARS = 40


def _short_status(fields: dict[str, str], names) -> str:
    for name in names:
        value = fields.get(name)
        if value and value != STRUCTURED and len(value) <= MAX_STATUS_CHARS:
            return value
    return ""


# A run manifest is `manifest.yaml` for most runs and `manifest.json` for a
# couple of dozen; both are the run's own terminal-status record, and reading
# only one of them reports live runs as having no manifest at all.
MANIFEST_NAMES = ("manifest.yaml", "manifest.json")


def _run_status(run_dir: Path) -> str:
    for name in MANIFEST_NAMES:
        manifest = run_dir / name
        if not manifest.is_file():
            continue
        try:
            _, fields = scan.shallow_fields(
                manifest.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            return "unreadable"
        return fields.get("status", "") or "unstated"
    return "no-manifest"


def _neg_date(value: str) -> str:
    """Sort key that puts newer dates first without reversing the whole tuple.

    Digits are complemented against `z`, so `2026-09-04` sorts before
    `2026-08-31`. An ABSENT date must sort LAST, not first: undated records
    are the oldest and least interesting rows in the corpus, and returning a
    low key floated every one of them to the top of every list. `~` is above
    every character this mapping can produce.
    """
    if not value:
        return "~"
    return "".join(chr(ord("z") - (ord(c) - ord("0")) if c.isdigit() else ord(c))
                   for c in value[:10])


def _rank(record: Record, needle: bytes) -> int:
    """Identifier and title matches outrank a hit buried in the body."""
    if not needle:
        return 1
    if needle in record.record_id.lower().encode():
        return 0
    if needle in record.title.lower().encode("utf-8", "replace"):
        return 1
    return 2
