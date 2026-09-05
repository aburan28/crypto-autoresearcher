"""Fast, shallow scanners over the on-disk research corpus.

WHY THIS IS NOT `yaml.safe_load` EVERYWHERE, STATED PLAINLY.
`ledger/` holds ~5,600 YAML records totalling ~82 MB. PyYAML's pure-Python
loader (no libyaml on the reference machine) parses that in ~54 seconds, and
reading the same bytes takes ~0.6. A dashboard that paid 54 s at startup, or
re-paid it on every refresh, would not be used.

So the corpus is read in two tiers, and the boundary between them is the one
thing a reader of this module has to understand:

  TIER 1 (this module) - every file is read and its *header fields* are
    extracted by a line-oriented shallow parser: the root key, the
    second-level scalar fields (`id`, `status`, `title`, dates), and every
    program identifier appearing anywhere in the text. This drives the
    lists, the boards, search, and the link graph. It is fast and it is
    approximate: a value this parser cannot represent is reported as
    STRUCTURED rather than guessed at.

  TIER 2 (`index.full_record`) - a real `yaml.safe_load`, done lazily for
    the one record a detail view asks for, and cached. Every field a reader
    actually inspects comes from here.

Goals are the exception and are fully parsed up front (there are ~100 of
them), because the portfolio board is the load-bearing view and its rows
must agree with the records byte for byte.

Nothing in this module writes anything. That is a hard property of the UI,
not an implementation detail: see ui/README.md.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, replace
from pathlib import Path

# ---------------------------------------------------------------------------
# Identifier grammar (CLAUDE.md "Conventions").
#
# Both the current random-token form (`GOAL-ECDLP-a93442`) and the legacy
# three-digit form (`GOAL-ECDLP-001`) are matched: legacy records are
# immutable and must never be renamed, so a UI that could not link them
# would be blind to most of the program's history.
# ---------------------------------------------------------------------------
KIND_PREFIXES = (
    "GOAL", "RQ", "IDEA", "H", "EXP", "RUN", "EV", "DEC",
    "TASK", "BATCH", "CORR", "KN",
)

# The second segment is an AREA token (`ECDLP`) for most kinds but a DATE
# (`20260904`) for the date-keyed ones and a bare token (`241d37`) for a
# batch, so it cannot be required to start with a letter -- requiring that
# silently excluded every decision, proposal, handoff and batch identifier
# from the link graph.
_ID_BODY = r"[A-Za-z0-9]{1,20}(?:-[A-Za-z0-9]{1,32}){0,2}"
RECORD_ID_RE = re.compile(rf"\b(?:{'|'.join(KIND_PREFIXES)})-{_ID_BODY}\b")

# `KN-LIT-...`/`KN-FIND-...` carry their family in the second position, so the
# area of a KN identifier is that family; everything else carries the area
# there, except the date-keyed kinds -- IDEA, DEC, TASK and CORR -- which
# carry a DATE there and therefore have no area at all. Reading one as an
# area fills the area filter with things like "20260724".
DATE_KEYED = {"IDEA", "DEC", "TASK", "CORR"}
_AREA_RE = re.compile(r"^[A-Z]+-([A-Z0-9]+)-")


def id_kind(record_id: str) -> str:
    """The kind prefix of an identifier.

    A goal checkpoint is named `<GOAL-ID>~<BATCH-ID>`; its kind is the part
    after the separator, not the goal prefix in front of it.
    """
    if "~" in record_id:
        record_id = record_id.split("~", 1)[1]
    return record_id.split("-", 1)[0]


def id_area(record_id: str) -> str | None:
    """Area token of an identifier, or None where the grammar defines none.

    Deliberately syntactic and deliberately NOT used to decide ECC
    membership -- that set is declared in
    `orchestration/research-priority.yaml` and read through
    `tools/ecc_priority.py`, which CLAUDE.md rule 11 requires.

    None for the date-keyed kinds, and none for an identifier outside the
    program's grammar entirely: a `VAL-20260802-8a4e15` validation report
    archived inside a correction has no area, and reading its date as one
    puts "20260802" in the area filter next to ECDLP.
    """
    kind = id_kind(record_id)
    if kind in DATE_KEYED or kind not in KIND_PREFIXES:
        return None
    m = _AREA_RE.match(record_id)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Shallow YAML header parsing.
# ---------------------------------------------------------------------------

STRUCTURED = "\x00structured"          # sentinel: a nested map/list, not a scalar

_BLOCK_INDICATORS = ("|", ">", "|-", ">-", "|+", ">+")
_KEY_RE = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_.\-]*):(?:\s+(.*))?$")


def _clean_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1]
        if value and "'" in value:
            value = value.replace("''", "'")
    return re.sub(r"\s+", " ", value).strip()


def _coerce_fields(body: dict) -> dict[str, str]:
    return {
        str(key): ("" if value is None else
                   STRUCTURED if isinstance(value, (dict, list)) else
                   _clean_scalar(str(value)))
        for key, value in body.items()
    }


def _parsed_fields(text: str, loader) -> tuple[str | None, dict[str, str]] | None:
    """Shared shape check for the two exact loaders below."""
    try:
        doc = loader(text)
    except Exception:                                 # noqa: BLE001 - caller falls back
        return None
    if not isinstance(doc, dict) or len(doc) != 1:
        return None
    root, body = next(iter(doc.items()))
    if not isinstance(body, dict):
        return None
    return str(root), _coerce_fields(body)


def _json_fields(text: str) -> tuple[str | None, dict[str, str]] | None:
    """Handle the ~50 ledger records written as JSON.

    JSON is valid YAML, so these are ordinary records that happen to have
    been emitted by a script rather than hand-written. `json.loads` is the C
    parser and costs nothing, so they are read exactly rather than
    approximately -- the line-oriented scanner below would see no keys at
    all in them.
    """
    return _parsed_fields(text, json.loads)


def shallow_fields(text: str) -> tuple[str | None, dict[str, str]]:
    """Return `(root_key, second_level_scalars)` for a single-document record.

    Every ledger record is one top-level key (`research_goal:`, `hypothesis:`,
    `coordinator_decision:`, ...) wrapping a map. This walks that map's
    direct children and returns the ones that are scalars, folding
    block and continued plain scalars onto one line. Children that open a
    nested map or list are reported as STRUCTURED, never guessed at.
    """
    if text.lstrip()[:1] == "{":
        parsed = _json_fields(text)
        if parsed is not None:
            return parsed

    lines = text.splitlines()
    root: str | None = None
    start = 0
    # Records come in three shapes and all three are load-bearing:
    #   wrapped   `hypothesis:` then two-space fields  (the overwhelming majority)
    #   flat      `decision_id: ...` at column zero    (a handful, no wrapper)
    #   flow      `coordinator_decision: {id: ..., ...}` on one line
    # Which one this is decides the indent the fields live at.
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped == "---":
            continue
        m = _KEY_RE.match(line)
        if m and not m.group(1):
            if not (m.group(3) or "").strip():
                root, start = m.group(2), i + 1     # wrapped
            elif (m.group(3) or "").lstrip().startswith("{"):
                root = None                          # flow: needs a real parse
                start = -1
            else:
                start = i                            # flat: fields at column zero
        break

    if start == -1:
        # A handful of records put the whole document in YAML flow style,
        # which a line-oriented scanner cannot see into. They are rare enough
        # to pay a real parse for, and reading them approximately would mean
        # showing a blank row for a decision that is perfectly well formed.
        import yaml                                   # local: keeps the hot path import-free

        return _parsed_fields(text, yaml.safe_load) or (None, {})

    field_indent = 2 if root is not None else 0
    fields: dict[str, str] = {}
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if root is not None and indent == 0:
            break                                   # a second document root
        if indent != field_indent:
            i += 1
            continue
        m = _KEY_RE.match(line)
        if not m:
            i += 1
            continue
        key, inline = m.group(2), (m.group(3) or "").strip()
        i += 1

        # Gather this key's value lines: anything indented deeper, plus block
        # sequence entries, which YAML permits at the KEY'S OWN indent --
        #     question_ids:
        #     - RQ-AES-002
        # Treating those as "nothing followed" would render a populated list
        # as an explicit null, which is the one reading a reader must not be
        # given.
        block: list[str] = []
        sequence = False
        while i < len(lines):
            nxt = lines[i]
            if not nxt.strip():
                block.append("")
                i += 1
                continue
            nxt_indent = len(nxt) - len(nxt.lstrip())
            if nxt_indent < field_indent:
                break
            if nxt_indent == field_indent:
                if not nxt.lstrip().startswith("- "):
                    break
                sequence = True
            block.append(nxt.strip())
            i += 1

        if inline in _BLOCK_INDICATORS or (inline.startswith(("|", ">")) and len(inline) <= 3):
            fields[key] = _clean_scalar(" ".join(p for p in block if p))
        elif not inline:
            # `key:` followed by deeper lines or by sequence entries is a
            # nested map or list; `key:` followed by nothing is an explicit
            # null.
            fields[key] = STRUCTURED if (block or sequence) else ""
        elif inline.startswith(("[", "{", "&", "*")):
            fields[key] = STRUCTURED
        else:
            # A plain or quoted scalar, possibly continued on deeper lines.
            continuation = [p for p in block if p and not p.startswith("#")]
            fields[key] = _clean_scalar(" ".join([inline, *continuation]))
    return root, fields


def front_matter(text: str) -> dict[str, str]:
    """Shallow-parse the YAML front matter of a knowledge markdown entry."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    body = text[text.find("\n") + 1: end]
    fields: dict[str, str] = {}
    for line in body.splitlines():
        m = _KEY_RE.match(line)
        if m and not m.group(1):
            fields[m.group(2)] = _clean_scalar(m.group(3) or "")
    return fields


# ---------------------------------------------------------------------------
# Corpus scanning.
# ---------------------------------------------------------------------------

# Which second-level field carries the record's own timestamp, per root key.
# Records disagree, so the scanner tries each in order and keeps the first hit.
DATE_FIELDS = (
    "decided_at", "recorded_at", "added", "updated_at", "created_at",
    "issued_at", "date", "raised_at",
)

TITLE_FIELDS = ("title", "objective", "statement", "claim", "question", "summary")

ROOT_KEY_TO_KIND = {
    "research_goal": "GOAL",
    "research_question": "RQ",
    "hypothesis": "H",
    "experiment": "EXP",
    "evidence": "EV",
    "coordinator_decision": "DEC",
    "decision": "DEC",
    "idea": "IDEA",
    "proposal": "IDEA",
    "handoff": "TASK",
    "correction": "CORR",
    "run": "RUN",
}


@dataclass(slots=True)
class RawRecord:
    """One scanned file. `text` is retained for search and link extraction."""

    record_id: str
    kind: str
    path: str
    root_key: str | None
    fields: dict[str, str]
    text: str
    parse_error: str | None = None
    refs: frozenset[str] = field(default_factory=frozenset)

    @property
    def area(self) -> str | None:
        return id_area(self.record_id)


def _pick(fields: dict[str, str], names) -> str:
    for name in names:
        value = fields.get(name)
        if value and value != STRUCTURED:
            return value
    return ""


def scan_file(path: Path, repo: Path) -> RawRecord:
    text = path.read_text(encoding="utf-8", errors="replace")
    root, fields = shallow_fields(text)
    declared = fields.get("id", "")
    if declared == STRUCTURED:
        declared = ""
    # The sharded goal layout names the file `goal.yaml`; its identity is the
    # parent directory (CLAUDE.md "Goal checkpoints are one file per batch").
    fallback = path.parent.name if path.name in ("goal.yaml",) else path.stem
    record_id = declared or fallback
    kind = ROOT_KEY_TO_KIND.get(root or "", id_kind(record_id))
    return RawRecord(
        record_id=record_id,
        kind=kind,
        path=str(path.relative_to(repo)),
        root_key=root,
        fields=fields,
        text=text,
        refs=frozenset(RECORD_ID_RE.findall(text)) - {record_id},
    )


# A goal's batch checkpoints are one write-once file per batch under the
# goal's own directory, so a shard's identity is the PAIR (goal, batch) --
# `BATCH-001.yaml` exists under a dozen different goals and those are not
# colliding identifiers. Naming them by the batch alone both hid every shard
# but the first and buried the duplicate-identifier report, which exists to
# catch real collisions, under ninety false ones.
CHECKPOINT_RE = re.compile(r"^ledger/goals/(GOAL-[^/]+)/checkpoints/")


def scan_ledger(repo: Path) -> list[RawRecord]:
    ledger = repo / "ledger"
    if not ledger.is_dir():
        return []
    records = []
    for path in sorted(ledger.rglob("*.yaml")):
        try:
            record = scan_file(path, repo)
            owner = CHECKPOINT_RE.match(record.path)
            if owner:
                record = replace(
                    record, kind="BATCH",
                    record_id=f"{owner.group(1)}~{record.record_id}")
            records.append(record)
        except OSError as exc:                        # unreadable, not unparseable
            records.append(RawRecord(
                record_id=path.stem, kind=id_kind(path.stem),
                path=str(path.relative_to(repo)), root_key=None, fields={},
                text="", parse_error=f"unreadable: {exc}",
            ))
    return records


def scan_knowledge(repo: Path, header_bytes: int = 6144) -> list[RawRecord]:
    """Scan `knowledge/` entries.

    Only the head of each file is read: the corpus is ~8,000 markdown files
    and the front matter that identifies an entry is always at the top. The
    full body is loaded on demand by the detail view.
    """
    root_dir = repo / "knowledge"
    if not root_dir.is_dir():
        return []
    records = []
    for path in sorted(root_dir.rglob("*.md")):
        if path.name in ("README.md", "SEEDING.md", "SOURCES.md") or path.name.startswith("TAG-"):
            continue
        try:
            with path.open(encoding="utf-8", errors="replace") as handle:
                head = handle.read(header_bytes)
        except OSError:
            continue
        fields = front_matter(head)
        record_id = fields.get("id") or path.stem
        records.append(RawRecord(
            record_id=record_id, kind="KN", path=str(path.relative_to(repo)),
            root_key="knowledge_entry", fields=fields, text=head,
            refs=frozenset(RECORD_ID_RE.findall(head)) - {record_id},
        ))
    return records
