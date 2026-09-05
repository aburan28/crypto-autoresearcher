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
from .scan import STRUCTURED, RawRecord, id_area, id_kind

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
            parsed = (yaml.safe_load(text), None) if path.suffix == ".yaml" else (None, None)
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
        areas = Counter(r.area for r in self.records.values() if r.area)
        statuses = Counter(r.status for r in self.records.values() if r.status)
        return {
            "kinds": [
                {"key": k, "label": KIND_LABELS.get(k, k), "count": kinds.get(k, 0)}
                for k in KIND_ORDER if kinds.get(k)],
            "areas": [
                {"key": a, "count": n, "ecc": a in self.ecc_areas}
                for a, n in sorted(areas.items(), key=lambda kv: (-kv[1], kv[0]))],
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
