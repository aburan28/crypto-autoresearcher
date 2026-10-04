"""Strict, schema-bound CM cost record carriers.

This layer validates record shape and lexical form. Whole-ledger identity,
capture, resource and accounting semantics are separate required checks; a
shape-valid record is never a certificate or run-admission assertion.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import math
from typing import Any, Iterable, Iterator, TextIO

import jsonschema
import yaml

CONTRACT_SHA256 = "2a7ec3075a59055404a33ceefe0b5531a63e464ed31e1d2a9cb736d584187237"
SCHEMA_SHA256 = "62060930e01b80306a7458623399555dedc80c61f6c77761f72ec2ee7884db3a"
RUNTIME_BINDING_SHA256 = "b4919db935d24e7ec756daaf9c59cbbf2e663407f2c621b3e752d2b25bded27f"
PUBLIC_KEY_SHA256 = "fa31ffa49bb6f0b464d1b3dd8085d771f77e553985596ff6f7266cc1575b7d0d"
COST_HEADER = ("record_type", "record_json")
DISPLAY_FLOAT_PATHS = frozenset({("run", "timing", "wall_seconds"), ("run", "resources", "cpu_seconds")})


class CostError(ValueError):
    """A typed record/contract failure, without embedding unbounded input data."""

    def __init__(self, code: str, path: tuple[Any, ...] = (), detail: str = "") -> None:
        self.code = code
        self.path = path
        self.detail = detail
        super().__init__(code + (": " + detail if detail else ""))


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CostError("duplicate_json_key", (key,))
        result[key] = value
    return result


def _decimal_integer(token: str) -> int:
    # Preserve arbitrary-precision integer semantics without changing the
    # interpreter's process-wide decimal conversion guard.
    negative = token.startswith("-")
    digits = token[1:] if negative else token
    value = 0
    for offset in range(0, len(digits), 9):
        part = digits[offset:offset + 9]
        value = value * (10 ** len(part)) + int(part)
    return -value if negative else value


def _integer_token(value: int) -> str:
    if value == 0:
        return "0"
    negative = value < 0
    value = -value if negative else value
    parts: list[int] = []
    while value:
        value, part = divmod(value, 1_000_000_000)
        parts.append(part)
    token = str(parts[-1]) + "".join(str(part).zfill(9) for part in reversed(parts[:-1]))
    return "-" + token if negative else token


def _compare_integer_tokens(left: str, right: str) -> int:
    # Index tokens are canonical output of _integer_token. Nonnegative clock
    # tokens compare by decimal length, then lexically, without repeated big
    # integer parsing during every SQLite B-tree comparison.
    if left.startswith("-") or right.startswith("-"):
        a, b = _decimal_integer(left), _decimal_integer(right)
        return (a > b) - (a < b)
    if len(left) != len(right):
        return (len(left) > len(right)) - (len(left) < len(right))
    return (left > right) - (left < right)


def _check_json_tree(value: Any, *, manifest: bool = False) -> None:
    stack = [((), value)]
    while stack:
        path, item = stack.pop()
        typ = type(item)
        if item is None or typ in (bool, int):
            continue
        if typ is str:
            try:
                item.encode("utf-8", errors="strict")
            except UnicodeError as exc:
                raise CostError("invalid_unicode", path) from exc
        elif typ is float:
            if not manifest or path not in DISPLAY_FLOAT_PATHS or not math.isfinite(item):
                raise CostError("forbidden_float", path)
        elif typ is list:
            stack.extend((path + (index,), child) for index, child in enumerate(item))
        elif typ is dict:
            for key, child in item.items():
                if type(key) is not str:
                    raise CostError("non_text_object_key", path)
                try:
                    key.encode("utf-8", errors="strict")
                except UnicodeError as exc:
                    raise CostError("invalid_unicode_key", path) from exc
                stack.append((path + (key,), child))
        else:
            raise CostError("non_json_value", path)


def _parse_json(data: bytes | str, *, manifest: bool) -> Any:
    if type(data) not in (bytes, str):
        raise CostError("json_input_requires_bytes_or_text")
    try:
        text = data.decode("utf-8", errors="strict") if type(data) is bytes else data
        text.encode("utf-8", errors="strict")
        if text.startswith("\ufeff"):
            raise CostError("json_bom_forbidden")
        def floating(token: str) -> float:
            if not manifest:
                raise CostError("forbidden_float")
            value = float(token)
            if not math.isfinite(value):
                raise CostError("nonfinite_number")
            return value
        def nonfinite(_token: str) -> None:
            raise CostError("nonfinite_number")
        value = json.loads(text, object_pairs_hook=_pairs, parse_int=_decimal_integer,
                           parse_float=floating, parse_constant=nonfinite)
        _check_json_tree(value, manifest=manifest)
        return value
    except CostError:
        raise
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise CostError("invalid_json_encoding_or_syntax", detail=type(exc).__name__) from exc


def strict_json_loads(data: bytes | str) -> Any:
    """Parse a cost-domain JSON value; floating lexical tokens are forbidden."""
    return _parse_json(data, manifest=False)


def parse_manifest_json(data: bytes | str) -> Any:
    """Only the two frozen display fields may contain finite float tokens."""
    return _parse_json(data, manifest=True)


def _canonical(value: Any, *, manifest: bool) -> bytes:
    _check_json_tree(value, manifest=manifest)
    def tokens(item: Any) -> Iterator[str]:
        if item is None:
            yield "null"
        elif type(item) is bool:
            yield "true" if item else "false"
        elif type(item) is int:
            yield _integer_token(item)
        elif type(item) in (str, float):
            yield json.dumps(item, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        elif type(item) is list:
            yield "["
            for index, child in enumerate(item):
                if index:
                    yield ","
                yield from tokens(child)
            yield "]"
        else:
            yield "{"
            for index, key in enumerate(sorted(item)):
                if index:
                    yield ","
                yield json.dumps(key, ensure_ascii=False) + ":"
                yield from tokens(item[key])
            yield "}"
    try:
        return ("".join(tokens(value)) + "\n").encode("utf-8", errors="strict")
    except (RecursionError, UnicodeError) as exc:
        raise CostError("canonical_encoding_failed", detail=type(exc).__name__) from exc


def canonical_json(value: Any) -> bytes:
    return _canonical(value, manifest=False)


def canonical_manifest_json(value: Any) -> bytes:
    return _canonical(value, manifest=True)


class CostContract:
    """A fixed, offline schema binding; record shape is only one validation layer."""

    def __init__(self, contract_bytes: bytes, schema_bytes: bytes) -> None:
        if type(contract_bytes) is not bytes or type(schema_bytes) is not bytes:
            raise CostError("contract_inputs_require_bytes")
        if hashlib.sha256(contract_bytes).hexdigest() != CONTRACT_SHA256:
            raise CostError("contract_hash_mismatch")
        if hashlib.sha256(schema_bytes).hexdigest() != SCHEMA_SHA256:
            raise CostError("schema_hash_mismatch")
        if importlib.metadata.version("PyYAML") != "6.0.3" or importlib.metadata.version("jsonschema") != "4.26.0":
            raise CostError("checker_dependency_version_mismatch")
        self.contract = yaml.safe_load(contract_bytes)["effective_contract"]
        self.schema = json.loads(schema_bytes.decode("utf-8", errors="strict"))
        stack = [self.schema]
        while stack:
            node = stack.pop()
            if type(node) is dict:
                for key, value in node.items():
                    if key in {"$ref", "$dynamicRef", "$recursiveRef"} and (type(value) is not str or not value.startswith("#")):
                        raise CostError("external_schema_reference_forbidden")
                    stack.append(value)
            elif type(node) is list:
                stack.extend(node)
        self._validators = {}
        for domain in ("raw_cost", "allocation_edge", "manifest"):
            wrapped = {"$schema": "https://json-schema.org/draft/2020-12/schema",
                       "$defs": self.schema["$defs"], "$ref": "#/$defs/" + domain}
            self._validators[domain] = jsonschema.Draft202012Validator(wrapped)
        rows = self.contract["cost_contract"]["component_crosswalk"]["rows"]
        self.crosswalk = {row["component"]: row for row in rows}
        if len(self.crosswalk) != len(rows):
            raise CostError("duplicate_contract_component")

    def validate_record_shape(self, record: Any) -> dict[str, Any]:
        _check_json_tree(record)
        if type(record) is not dict:
            raise CostError("cost_record_requires_object")
        domain = record.get("record_type")
        if domain not in ("raw_cost", "allocation_edge"):
            raise CostError("unknown_cost_record_type")
        try:
            error = next(self._validators[domain].iter_errors(record), None)
        except (ValueError, TypeError, RecursionError) as exc:
            raise CostError("cost_schema_validation_failed", detail=type(exc).__name__) from exc
        if error is not None:
            raise CostError("cost_record_schema_error", tuple(error.absolute_path), str(error.validator))
        # Return a detached JSON value, not an enduring claim about mutable input.
        return strict_json_loads(canonical_json(record))

    def validate_manifest_shape(self, manifest: Any) -> dict[str, Any]:
        _check_json_tree(manifest, manifest=True)
        try:
            error = next(self._validators["manifest"].iter_errors(manifest), None)
        except (ValueError, TypeError, RecursionError) as exc:
            raise CostError("manifest_schema_validation_failed", detail=type(exc).__name__) from exc
        if error is not None:
            raise CostError("manifest_schema_error", tuple(error.absolute_path), str(error.validator))
        return parse_manifest_json(canonical_manifest_json(manifest))

    def validate_manifest_local_relations(self, manifest: Any) -> dict[str, Any]:
        """Closed metadata relations; no external admission facts are inferred."""
        checked = self.validate_manifest_shape(manifest)
        run = checked["run"]
        timing, resources = run["timing"], run["resources"]
        if _utc_instant(timing["finished_at"]) < _utc_instant(timing["started_at"]):
            raise CostError("manifest_time_regressed")
        _display_seconds(timing["wall_seconds"], timing["wall_nanoseconds"], "wall")
        for value, reason in (("peak_rss_bytes", "peak_rss_unavailable_reason"), ("cpu_nanoseconds", "cpu_unavailable_reason")):
            if (resources[value] is None) != (resources[reason] is not None):
                raise CostError("manifest_resource_reason_pair", (value,))
        if resources["cpu_nanoseconds"] is None:
            if resources["cpu_seconds"] is not None:
                raise CostError("manifest_unknown_cpu_has_display_value")
        else:
            _display_seconds(resources["cpu_seconds"], resources["cpu_nanoseconds"], "cpu")
        inference = run["inference"]
        if inference["model_provenance"] == "not-applicable" and "resolution_error" not in inference:
            if inference["requested_policy"] != inference["canonical_policy"]:
                raise CostError("deterministic_policy_alias_mismatch")
        result = run["result"]
        if "resolution_error" in inference and (result["reason_code"] != "POLICY_RESOLUTION_FAILED" or
                result["stage"] != "authorize_and_claim_nonce" or run["status"] != "refused_before_run"):
            raise CostError("inference_resolution_failure_outcome_mismatch")
        rules = self.contract["artifact_custody"]["outcome_relation"]
        matching = [rule for rule in rules if rule["reason_code"] == result["reason_code"]]
        if len(matching) != 1:
            raise CostError("manifest_outcome_reason")
        rule = matching[0]
        if (run["status"] != rule["status"] or result["valid"] is not rule["valid"] or
                result["stage"] not in rule["stages"] or result["metrics"]["branch"] not in rule["branches"]):
            raise CostError("manifest_outcome_relation")
        if result["invalid_reason"] != (None if run["status"] == "completed_valid" else result["reason_code"]):
            raise CostError("manifest_invalid_reason_relation")
        return checked

    def iter_cost_csv(self, stream: Iterable[str | bytes]) -> Iterator[dict[str, Any]]:
        """Read physical lines incrementally; each record_json must be canonical."""
        def lines() -> Iterator[str]:
            for line in stream:
                if type(line) is bytes:
                    try:
                        line = line.decode("utf-8", errors="strict")
                    except UnicodeError as exc:
                        raise CostError("csv_invalid_utf8") from exc
                if type(line) is not str or "\r" in line:
                    raise CostError("csv_requires_lf_text_lines")
                yield line
        try:
            reader = csv.reader(lines(), strict=True)
            if next(reader, None) != list(COST_HEADER):
                raise CostError("cost_csv_header_mismatch")
            edges_started = False
            for fields in reader:
                if len(fields) != 2:
                    raise CostError("cost_csv_column_count")
                record = self.validate_record_shape(strict_json_loads(fields[1]))
                if fields[0] != record["record_type"]:
                    raise CostError("cost_csv_record_type_mismatch")
                if record["record_type"] == "allocation_edge":
                    edges_started = True
                elif edges_started:
                    raise CostError("raw_record_after_allocation_edges")
                if canonical_json(record)[:-1].decode("utf-8") != fields[1]:
                    raise CostError("cost_csv_noncanonical_record_json")
                yield record
        except csv.Error as exc:
            raise CostError("malformed_cost_csv") from exc

    def write_cost_csv(self, records: Iterable[dict[str, Any]], stream: TextIO) -> None:
        writer = csv.writer(stream, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(COST_HEADER)
        edges_started = False
        for original in records:
            record = self.validate_record_shape(original)
            if record["record_type"] == "allocation_edge":
                edges_started = True
            elif edges_started:
                raise CostError("raw_record_after_allocation_edges")
            writer.writerow((record["record_type"], canonical_json(record)[:-1].decode("utf-8")))


RESOURCE_REASON_FIELDS = (
    ("CPU_nanoseconds", "CPU_unavailable_reason"),
    ("wall_nanoseconds", "wall_unavailable_reason"),
    ("process_group_peak_RSS_bytes", "RSS_unavailable_reason"),
    ("operation_counts", "operation_counts_unavailable_reason"),
)


def _utc_instant(value: str) -> Any:
    """Compare UTC instants with exact fractional seconds, not string order."""
    from datetime import datetime, timezone
    from fractions import Fraction
    import re
    match = re.fullmatch(r"(\d{4}-\d{2}-\d{2})[Tt](\d{2}:\d{2}:\d{2})(?:\.(\d+))?(?:Z|\+00:00)", value)
    if match is None:
        raise CostError("manifest_utc_timestamp")
    try:
        base = datetime.fromisoformat(match[1]+"T"+match[2]).replace(tzinfo=timezone.utc)
        delta = base - datetime(1970, 1, 1, tzinfo=timezone.utc)
    except ValueError as exc:
        raise CostError("manifest_utc_timestamp") from exc
    digits = match[3]
    fraction = Fraction(_decimal_integer(digits), 10**len(digits)) if digits else Fraction(0)
    return Fraction(delta.days*86400 + delta.seconds) + fraction


def _display_seconds(display: Any, nanoseconds: int, label: str) -> None:
    from fractions import Fraction
    if type(display) is int:
        agrees = display*1000000000 == nanoseconds
    elif type(display) is float and math.isfinite(display):
        try:
            agrees = display == float(Fraction(nanoseconds, 1000000000))
        except OverflowError:
            agrees = False
    else:
        agrees = False
    if not agrees:
        raise CostError("manifest_display_seconds_mismatch", (label,))
IDENTITY_AXES = ("interval", "fixture", "kernel", "class", "endpoint", "coordinate", "plane", "seed", "q", "arm", "block", "repetition", "owner")


class CostInfrastructureError(CostError):
    """The component could not complete its check; not a data or science verdict."""


class CostCancelled(CostInfrastructureError):
    """A requested checkpoint stop; retained observations are not a failure claim."""


class CostCheckpoint:
    """Cooperative cancellation without replaceable algorithm callbacks.

    The invoking layer persists snapshot() in its custody record. This object
    is process-local state, not a durable receipt or a hard watchdog.
    """

    def __init__(self) -> None:
        import threading
        self._lock = threading.Lock()
        self._requested = False
        self._boundaries = 0
        self._last_phase = None

    def request_stop(self) -> None:
        with self._lock:
            self._requested = True

    def check(self, phase: str) -> None:
        if type(phase) is not str or not phase:
            raise CostError("checkpoint_phase")
        with self._lock:
            self._boundaries += 1
            self._last_phase = phase
            requested = self._requested
        if requested:
            error = CostCancelled("cooperative_checkpoint_stop")
            error.checkpoint = self.snapshot()
            raise error

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {"stop_requested": self._requested, "boundaries_reached": self._boundaries,
                    "last_phase": self._last_phase, "durable_receipt": False}


def checkpoint_boundary(checkpoint: CostCheckpoint | None, phase: str) -> None:
    if checkpoint is not None:
        if type(checkpoint) is not CostCheckpoint:
            raise CostError("checkpoint_requires_fixed_type")
        CostCheckpoint.check(checkpoint, phase)


def validate_raw_semantics(contract: CostContract, original: Any) -> dict[str, Any]:
    row = contract.validate_record_shape(original)
    if row["record_type"] != "raw_cost":
        raise CostError("expected_raw_cost")
    entry = contract.crosswalk[row["component"]]
    if row["scope"] not in entry["allowed_scopes"] or row["phase"] not in entry["allowed_phases"]:
        raise CostError("component_scope_phase_mismatch")
    contexts = entry["allowed_plane_arm"]
    if type(contexts) is list and not any(
        row.get("plane") == allowed["plane"] and type(row.get("arm")) is int and row["arm"] in allowed["arms"]
        for allowed in contexts
    ):
        raise CostError("component_plane_arm_mismatch")
    if row["scope"] == "scaffolding" and row["scaffold_kind"] != row["component"]:
        raise CostError("scaffolding_component_mismatch")
    for value_field, reason_field in RESOURCE_REASON_FIELDS:
        value, reason = row[value_field], row[reason_field]
        if (value is None) != (reason is not None):
            raise CostError("resource_reason_pair_mismatch", (value_field,))
    refs = row["source_leaf_ids"]
    if len(refs) != len(set(refs)):
        raise CostError("duplicate_rollup_reference")
    capture = row["capture_interval"]
    for clock in ("cpu", "wall"):
        begin, end = capture[clock + "_started_ns"], capture[clock + "_finished_ns"]
        if (begin is None) != (end is None):
            raise CostError("partial_clock_pair", ("capture_interval", clock))
        if begin is not None and end < begin:
            raise CostError("clock_runs_backwards", ("capture_interval", clock))
    if row["component"] in {"level_and_multiplicity_certificate", "all_six_algorithm_selection_trials"} and row["charge_kind"] != "derived_rollup":
        raise CostError("aggregate_component_must_be_uncharged_rollup")
    if row["charge_kind"] == "exclusive_leaf":
        if capture["reason"] == "derived_rollup":
            raise CostError("exclusive_capture_uses_rollup_reason")
        for _, reason_field in RESOURCE_REASON_FIELDS:
            if row[reason_field] == "derived_rollup":
                raise CostError("exclusive_leaf_uses_rollup_reason", (reason_field,))
        if row["status"] in ("complete", "below_resolution"):
            if any(row[key] is None for key, _ in RESOURCE_REASON_FIELDS[:3]):
                raise CostError("complete_leaf_missing_resource")
            if capture["process_group_id"] is None or any(capture[key] is None for key in (
                "cpu_started_ns", "cpu_finished_ns", "wall_started_ns", "wall_finished_ns")):
                raise CostError("complete_leaf_missing_capture")
            if capture["reason"] is not None:
                raise CostError("complete_capture_has_unavailability_reason")
    else:
        if not refs:
            raise CostError("rollup_without_leaves")
        for value_field, reason_field in RESOURCE_REASON_FIELDS[:2]:
            if row[value_field] is not None or row[reason_field] != "derived_rollup":
                raise CostError("rollup_has_independent_charge", (value_field,))
    return row


def logical_capture_key(row: dict[str, Any]) -> bytes:
    """Use every actual scope/owner axis and the declared capture stream."""
    return canonical_json({
        "scope": row["scope"],
        "axes": {key: row[key] for key in IDENTITY_AXES if key in row},
        "component": row["component"], "phase": row["phase"],
        "event_ordinal": row["event_ordinal"],
        "capture_stream": row["capture_interval"]["stream_id"],
    })


class CostLedger:
    """An owned temporary index over immutable input records.

    The caller supplies the trusted spool parent and owns eventual cleanup.
    The index is deliberately retained after errors for custody. Finalization
    establishes internal consistency only; expected scientific coverage and
    authentic capture/certificate facts require later checks.
    """

    def __init__(self, contract: CostContract, spool_parent: Any, *, checkpoint: CostCheckpoint | None = None) -> None:
        import sqlite3
        import tempfile
        from pathlib import Path
        self.contract = contract
        checkpoint_boundary(checkpoint, "ledger_initialize")
        self.checkpoint = checkpoint
        self._sqlite3 = sqlite3
        self._count = 0
        self._finished = False
        self._inventory_checked = False
        self._failed = False
        self._closed = False
        self.cleanup_errors: list[dict[str, str]] = []
        self.directory = None
        self.path = None
        self._db = None
        try:
            parent = Path(spool_parent).resolve(strict=True)
            if not parent.is_dir():
                raise CostInfrastructureError("spool_parent_is_not_directory")
            self.directory = Path(tempfile.mkdtemp(prefix="cm-cost-index-", dir=parent))
            self.path = self.directory / "ledger.sqlite3"
            self._db = sqlite3.connect(self.path)
            self._db.create_collation("EXACT_INT", _compare_integer_tokens)
            # This is a rebuildable computational index, not the durable evidence.
            self._db.execute("PRAGMA journal_mode=MEMORY")
            self._db.execute("PRAGMA synchronous=OFF")
            self._db.executescript('''
                CREATE TABLE raw_rows (
                    ordinal INTEGER PRIMARY KEY, row_id TEXT NOT NULL UNIQUE,
                    physical_id TEXT NOT NULL, kind TEXT NOT NULL,
                    logical_key BLOB NOT NULL UNIQUE, payload BLOB NOT NULL, payload_sha256 TEXT NOT NULL
                );
                CREATE UNIQUE INDEX unique_physical_leaf ON raw_rows(physical_id) WHERE kind='exclusive_leaf';
                CREATE TABLE leaf_refs (rollup_id TEXT NOT NULL, leaf_id TEXT NOT NULL, UNIQUE(rollup_id,leaf_id));
                CREATE TABLE selection_owners (row_id TEXT PRIMARY KEY, interval TEXT NOT NULL, coordinate INTEGER NOT NULL);
                CREATE INDEX selection_stratum ON selection_owners(interval,coordinate);
            CREATE TABLE ordinal_heads (domain BLOB PRIMARY KEY, last_ordinal TEXT NOT NULL);
                CREATE TABLE spans (
                    process_group TEXT NOT NULL, clock TEXT NOT NULL,
                    first TEXT COLLATE EXACT_INT NOT NULL, last TEXT COLLATE EXACT_INT NOT NULL,
                    row_id TEXT NOT NULL
                );
                CREATE INDEX span_start ON spans(process_group,clock,first COLLATE EXACT_INT);
            ''')
        except Exception as primary:
            if self._db is not None:
                try:
                    self._db.close()
                    self._closed = True
                except Exception as secondary:
                    self.cleanup_errors.append({"phase": "index_initialization_cleanup", "type": type(secondary).__name__, "detail": str(secondary)})
            failure = CostInfrastructureError("ledger_index_initialization_failed", detail=type(primary).__name__)
            failure.primary_error = {"type": type(primary).__name__, "detail": str(primary)}
            failure.cleanup_errors = list(self.cleanup_errors)
            failure.retained_directory = str(self.directory) if self.directory is not None else None
            raise failure from primary

    def _require_open(self) -> None:
        if self._closed:
            raise CostInfrastructureError("ledger_index_closed")
        if self._failed:
            raise CostError("ledger_has_prior_failure")

    def add(self, original: Any) -> None:
        self._require_open()
        checkpoint_boundary(self.checkpoint, "ledger_add")
        if self._finished:
            raise CostError("ledger_already_finalized")
        try:
            row = validate_raw_semantics(self.contract, original)
            with self._db:
                domain = canonical_json({"candidate_interval": row["interval"]}) if row["scope"] == "interval" else canonical_json({"capture_stream": row["capture_interval"]["stream_id"]})
                head = self._db.execute("SELECT last_ordinal FROM ordinal_heads WHERE domain=?", (domain,)).fetchone()
                if head is not None and row["event_ordinal"] < _decimal_integer(head[0]):
                    raise CostError("raw_capture_order_regressed", (row["raw_cost_row_id"],))
                self._db.execute("INSERT INTO ordinal_heads VALUES (?,?) ON CONFLICT(domain) DO UPDATE SET last_ordinal=excluded.last_ordinal", (domain, _integer_token(row["event_ordinal"])))
                self._db.execute("INSERT INTO raw_rows VALUES (?,?,?,?,?,?,?)", (
                    self._count, row["raw_cost_row_id"], row["physical_event_id"],
                    row["charge_kind"], logical_capture_key(row), canonical_json(row), hashlib.sha256(canonical_json(row)).hexdigest()))
                if row["charge_kind"] == "derived_rollup":
                    self._db.executemany("INSERT INTO leaf_refs VALUES (?,?)", (
                        (row["raw_cost_row_id"], leaf) for leaf in row["source_leaf_ids"]))
                else:
                    if row.get("plane") == "selection":
                        self._db.execute("INSERT INTO selection_owners VALUES (?,?,?)", (
                            row["raw_cost_row_id"], row["fixture"][:2], row["coordinate"]))
                    capture = row["capture_interval"]
                    group = capture["process_group_id"]
                    for clock in ("cpu", "wall"):
                        first, last = capture[clock + "_started_ns"], capture[clock + "_finished_ns"]
                        if group is None or first is None or first == last:
                            continue
                        # Accepted spans are pairwise disjoint. A new span
                        # overlaps iff its predecessor extends past its start,
                        # or its successor starts before its end. Two indexed
                        # neighbour lookups avoid scanning every prior span.
                        first_token, last_token = _integer_token(first), _integer_token(last)
                        owner = (_integer_token(group), clock, first_token)
                        previous = self._db.execute(
                            "SELECT row_id,last FROM spans WHERE process_group=? AND clock=? AND first<=? COLLATE EXACT_INT ORDER BY first COLLATE EXACT_INT DESC LIMIT 1", owner).fetchone()
                        successor = self._db.execute(
                            "SELECT row_id,first FROM spans WHERE process_group=? AND clock=? AND first>? COLLATE EXACT_INT ORDER BY first COLLATE EXACT_INT ASC LIMIT 1", owner).fetchone()
                        conflict = previous if previous and _compare_integer_tokens(previous[1], first_token) > 0 else None
                        if conflict is None and successor and _compare_integer_tokens(successor[1], last_token) < 0:
                            conflict = successor
                        if conflict:
                            raise CostError("overlapping_exclusive_capture", (row["raw_cost_row_id"], clock), conflict[0])
                        # A stream label does not exempt overlapping observations
                        # of the same process-group clock from double-charge checks.
                        self._db.execute("INSERT INTO spans VALUES (?,?,?,?,?)", (
                            _integer_token(group), clock, _integer_token(first), _integer_token(last), row["raw_cost_row_id"]))
            self._count += 1
        except self._sqlite3.IntegrityError as exc:
            self._failed = True
            raise CostError("duplicate_ledger_identity") from exc
        except self._sqlite3.Error as exc:
            self._failed = True
            raise CostInfrastructureError("ledger_storage_failure", detail=type(exc).__name__) from exc
        except BaseException:
            self._failed = True
            raise

    def finalize(self) -> dict[str, Any]:
        self._require_open()
        try:
            broken = self._db.execute('''
                SELECT refs.rollup_id, refs.leaf_id
                FROM leaf_refs AS refs LEFT JOIN raw_rows AS leaf ON leaf.row_id=refs.leaf_id
                WHERE leaf.row_id IS NULL OR leaf.kind!='exclusive_leaf' LIMIT 1
            ''').fetchone()
            if broken:
                self._failed = True
                raise CostError("rollup_reference_is_not_exclusive_leaf", tuple(broken))
            # Resolve component-specific summaries against their actual leaves.
            # An existing leaf ID alone does not establish the stated summary.
            for rollup_payload, leaf_payload in self._db.execute('''
                SELECT parent.payload, leaf.payload FROM leaf_refs AS refs
                JOIN raw_rows AS parent ON parent.row_id=refs.rollup_id
                JOIN raw_rows AS leaf ON leaf.row_id=refs.leaf_id
            '''):
                checkpoint_boundary(self.checkpoint, "ledger_rollup_join")
                parent = strict_json_loads(rollup_payload)
                leaf = strict_json_loads(leaf_payload)
                if parent["component"] == "level_and_multiplicity_certificate":
                    if leaf["component"] not in ("level_source_certificate", "class_multiplicity_certificate", "within_pair_isomorphism"):
                        self._failed = True
                        raise CostError("level_rollup_wrong_component", (parent["raw_cost_row_id"], leaf["raw_cost_row_id"]))
                    if leaf.get("fixture") != parent["fixture"] or (
                        parent["scope"] == "class" and leaf["scope"] == "class" and leaf["class"] != parent["class"]
                    ):
                        self._failed = True
                        raise CostError("level_rollup_wrong_owner", (parent["raw_cost_row_id"], leaf["raw_cost_row_id"]))
                elif parent["component"] == "all_six_algorithm_selection_trials":
                    if (leaf.get("plane") != "selection" or leaf.get("fixture") not in
                        (parent["interval"] + "F0", parent["interval"] + "F1") or
                        leaf.get("coordinate") != parent["coordinate"]):
                        self._failed = True
                        raise CostError("selection_rollup_wrong_owner", (parent["raw_cost_row_id"], leaf["raw_cost_row_id"]))
            for (payload,) in self._db.execute("SELECT payload FROM raw_rows WHERE kind='derived_rollup'"):
                checkpoint_boundary(self.checkpoint, "selection_rollup_completeness")
                parent = strict_json_loads(payload)
                if parent["component"] != "all_six_algorithm_selection_trials":
                    continue
                omitted = self._db.execute('''
                    SELECT owned.row_id FROM selection_owners AS owned
                    LEFT JOIN leaf_refs AS refs ON refs.leaf_id=owned.row_id AND refs.rollup_id=?
                    WHERE owned.interval=? AND owned.coordinate=? AND refs.leaf_id IS NULL LIMIT 1
                ''', (parent["raw_cost_row_id"], parent["interval"], parent["coordinate"])).fetchone()
                if omitted:
                    self._failed = True
                    raise CostError("selection_rollup_omits_retained_trial_leaf", (parent["raw_cost_row_id"], omitted[0]))
            self._db.commit()
            self._finished = True
            return {"indexed_rows": self._count, "ledger_identity_and_capture_consistent": True,
                    "scientific_coverage_verified": False, "capture_authenticity_verified": False}
        except self._sqlite3.Error as exc:
            self._failed = True
            raise CostInfrastructureError("ledger_finalize_failed", detail=type(exc).__name__) from exc

    def iter_rows(self) -> Iterator[dict[str, Any]]:
        self._require_open()
        if not self._finished:
            raise CostError("ledger_not_finalized")
        try:
            for (payload,) in self._db.execute("SELECT payload FROM raw_rows ORDER BY ordinal"):
                checkpoint_boundary(self.checkpoint, "ledger_iterate")
                yield strict_json_loads(payload)
        except self._sqlite3.Error as exc:
            self._failed = True
            raise CostInfrastructureError("ledger_iteration_failed", detail=type(exc).__name__) from exc

    def get(self, row_id: str) -> dict[str, Any]:
        self._require_open()
        if not self._finished:
            raise CostError("ledger_not_finalized")
        if type(row_id) is not str:
            raise CostError("row_id_requires_text")
        try:
            result = self._db.execute("SELECT payload FROM raw_rows WHERE row_id=?", (row_id,)).fetchone()
        except self._sqlite3.Error as exc:
            self._failed = True
            raise CostInfrastructureError("ledger_lookup_failed", detail=type(exc).__name__) from exc
        if result is None:
            raise CostError("unknown_raw_row", (row_id,))
        return strict_json_loads(result[0])

    @property
    def capture_inventory_compared(self) -> bool:
        self._require_open()
        return self._finished and self._inventory_checked

    def compare_capture_inventory(self, entries: Iterable[dict[str, Any]]) -> dict[str, Any]:
        """Compare a separately supplied inventory; authentication is external.

        The invoking layer must bind this inventory to its retained capture
        journal. Deriving it from this same untrusted ledger would add no
        evidence about omitted charges, and is not an authenticated invocation.
        """
        import re
        self._require_open()
        if not self._finished or self._inventory_checked:
            raise CostError("capture_inventory_comparison_state")
        count = 0
        try:
            with self._db:
                self._db.execute("CREATE TABLE expected_capture (row_id TEXT PRIMARY KEY, digest TEXT NOT NULL)")
                for entry in entries:
                    checkpoint_boundary(self.checkpoint, "capture_inventory_entry")
                    _check_json_tree(entry)
                    if type(entry) is not dict or set(entry) != {"raw_cost_row_id", "canonical_record_sha256"}:
                        raise CostError("capture_inventory_entry_fields")
                    key, digest = entry["raw_cost_row_id"], entry["canonical_record_sha256"]
                    if type(key) is not str or not key or type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                        raise CostError("capture_inventory_entry_domain")
                    self._db.execute("INSERT INTO expected_capture VALUES (?,?)", (key, digest))
                    count += 1
                mismatch = self._db.execute("SELECT expected.row_id FROM expected_capture AS expected LEFT JOIN raw_rows AS raw ON raw.row_id=expected.row_id WHERE raw.row_id IS NULL OR raw.payload_sha256!=expected.digest LIMIT 1").fetchone()
                extra = self._db.execute("SELECT raw.row_id FROM raw_rows AS raw LEFT JOIN expected_capture AS expected ON expected.row_id=raw.row_id WHERE expected.row_id IS NULL LIMIT 1").fetchone()
                if mismatch or extra:
                    raise CostError("capture_inventory_mismatch", tuple(mismatch or extra))
            self._inventory_checked = True
            return {"compared_rows": count, "inventory_matches_retained_rows": True,
                    "inventory_authenticity_verified_by_component": False}
        except self._sqlite3.IntegrityError as exc:
            self._failed = True
            raise CostError("duplicate_capture_inventory_entry") from exc
        except self._sqlite3.Error as exc:
            self._failed = True
            raise CostInfrastructureError("capture_inventory_storage_failure", detail=type(exc).__name__) from exc
        except BaseException:
            self._failed = True
            raise

    def close(self) -> None:
        if not self._closed:
            self._db.close()
            self._closed = True

    def __enter__(self) -> "CostLedger":
        return self

    def __exit__(self, typ: Any, value: Any, tb: Any) -> bool:
        try:
            self.close()
        except Exception as cleanup:
            self.cleanup_errors.append({"type": type(cleanup).__name__, "detail": str(cleanup)})
            if value is None:
                raise CostInfrastructureError("ledger_close_failed") from cleanup
            try:
                value.add_note("CM ledger close failure retained separately: " + type(cleanup).__name__)
            except Exception:
                pass
        return False


def actual_campaign_accounting(ledger: CostLedger) -> dict[str, Any]:
    """Sum observed physical leaves once, preserving unavailable resources."""
    known = {"CPU_nanoseconds": 0, "wall_nanoseconds": 0}
    missing = {key: 0 for key in known}
    peak = None
    partial_rows = 0
    missing_rss = 0
    missing_operations = 0
    leaves = 0
    for row in ledger.iter_rows():
        if row["charge_kind"] != "exclusive_leaf":
            continue
        leaves += 1
        if row["status"] in ("partial", "failed"):
            partial_rows += 1
        for field in known:
            if row[field] is None:
                missing[field] += 1
            else:
                known[field] += row[field]
        rss = row["process_group_peak_RSS_bytes"]
        if rss is None:
            missing_rss += 1
        if rss is not None:
            peak = rss if peak is None else max(peak, rss)
        if row["operation_counts"] is None:
            missing_operations += 1
    return {"exclusive_leaf_count": leaves,
            "CPU_nanoseconds": None if missing["CPU_nanoseconds"] else known["CPU_nanoseconds"],
            "wall_nanoseconds": None if missing["wall_nanoseconds"] else known["wall_nanoseconds"],
            "known_CPU_lower_bound": known["CPU_nanoseconds"],
            "known_wall_lower_bound": known["wall_nanoseconds"],
            "unavailable_row_counts": missing, "partial_or_failed_row_count": partial_rows,
            "detail_access": "iter_accounting_anomalies over the retained ledger index",
            "peak_observed_RSS_bytes": peak,
            "RSS_unavailable_row_count": missing_rss,
            "peak_RSS_observation_complete": leaves > 0 and missing_rss == 0,
            "operation_counts_unavailable_row_count": missing_operations,
            "operation_count_detail_access": "iter_operation_totals",
            "complete_scientific_campaign_asserted": False}


def iter_operation_totals(ledger: CostLedger) -> Iterator[dict[str, Any]]:
    """Stream exact totals by observed operation name through the owned index.

    Missing a name in one leaf does not mean that leaf performed zero such
    operations. Report a known lower bound and the missing-name row count.
    Arbitrary operation names and integers are allowed by the frozen schema,
    so neither a global Python dictionary nor SQLite's fixed-width SUM is used.
    """
    import uuid
    ledger._require_open()
    if not ledger._finished:
        raise CostError("ledger_not_finalized")
    table = "operation_totals_" + uuid.uuid4().hex
    leaves = 0
    primary = None
    created = False
    output_cursor = None
    try:
        ledger._db.execute(f"CREATE TEMP TABLE {table} (name TEXT PRIMARY KEY, total TEXT NOT NULL, observed_rows INTEGER NOT NULL)")
        created = True
        with ledger._db:
            for row in ledger.iter_rows():
                if row["charge_kind"] != "exclusive_leaf":
                    continue
                leaves += 1
                counts = row["operation_counts"]
                if counts is None:
                    continue
                for name, value in counts.items():
                    previous = ledger._db.execute(f"SELECT total,observed_rows FROM {table} WHERE name=?", (name,)).fetchone()
                    total = value + (_decimal_integer(previous[0]) if previous is not None else 0)
                    observed = previous[1] + 1 if previous is not None else 1
                    ledger._db.execute(f"INSERT INTO {table} VALUES (?,?,?) ON CONFLICT(name) DO UPDATE SET total=excluded.total, observed_rows=excluded.observed_rows", (name, _integer_token(total), observed))
        output_cursor = ledger._db.execute(f"SELECT name,total,observed_rows FROM {table} ORDER BY name")
        for name, token, observed in output_cursor:
            known = _decimal_integer(token)
            yield {"operation": name, "known_lower_bound": known,
                   "total": known if observed == leaves else None,
                   "observed_row_count": observed, "unavailable_or_omitted_row_count": leaves - observed,
                   "whole_campaign_operation_coverage_asserted": False}
    except ledger._sqlite3.Error as exc:
        primary = CostInfrastructureError("operation_accounting_storage_failure", detail=type(exc).__name__)
        raise primary from exc
    except BaseException as exc:
        primary = exc
        raise
    finally:
        cleanup_failures = []
        if output_cursor is not None:
            try:
                output_cursor.close()
            except Exception as cleanup:
                cleanup_failures.append(cleanup)
                ledger.cleanup_errors.append({"phase": "operation_accounting_cursor_close", "type": type(cleanup).__name__, "detail": str(cleanup)})
        if created:
            try:
                ledger._db.execute(f"DROP TABLE {table}")
            except Exception as cleanup:
                cleanup_failures.append(cleanup)
                ledger.cleanup_errors.append({"phase": "operation_accounting_cleanup", "type": type(cleanup).__name__, "detail": str(cleanup)})
        if primary is None and cleanup_failures:
            raise CostInfrastructureError("operation_accounting_cleanup_failed") from cleanup_failures[0]


def iter_accounting_anomalies(ledger: CostLedger) -> Iterator[dict[str, Any]]:
    """Expose retained uncertainty without an unbounded in-memory ID list."""
    for row in ledger.iter_rows():
        if row["charge_kind"] != "exclusive_leaf":
            continue
        missing = [key for key, _ in RESOURCE_REASON_FIELDS if row[key] is None]
        if missing or row["status"] in ("partial", "failed"):
            yield {"raw_cost_row_id": row["raw_cost_row_id"], "status": row["status"], "unavailable_fields": missing}


def pinned_dependency_projection(runtime_bytes: bytes, public_key_bytes: bytes) -> dict[str, Any]:
    """A fixed metadata projection; no installed binary or signature is run.

    Dependency keys are explicit version fields and exact pinned file paths.
    A version-only entry does not pretend to hash a binary; a file-only entry
    does not invent an independent version for that file.
    """
    if type(runtime_bytes) is not bytes or hashlib.sha256(runtime_bytes).hexdigest() != RUNTIME_BINDING_SHA256:
        raise CostError("runtime_binding_bytes_mismatch")
    if type(public_key_bytes) is not bytes or hashlib.sha256(public_key_bytes).hexdigest() != PUBLIC_KEY_SHA256:
        raise CostError("public_trust_bytes_mismatch")
    # This hash-pinned historical metadata includes display floats. It is not
    # a cost-record carrier and must not be parsed as an all-integer workload.
    binding = json.loads(runtime_bytes.decode("utf-8"))
    runtime = binding["runtime"]
    dependencies = {}
    for name in ("python", "sage_launcher_version", "cypari2", "pari",
                 "pari_build_receipt_sage_version", "compiler", "kernel", "thread_engine"):
        dependencies["runtime_version:" + name] = {
            "version": runtime[name], "sha256": None,
            "unavailable_reason": "version_metadata_only; file hashes are separate entries"}
    for entry in runtime["file_bindings"]:
        key = "file:" + entry["path"]
        if key in dependencies:
            raise CostError("duplicate_pinned_dependency_path")
        dependencies[key] = {"version": None, "sha256": entry["sha256"],
                             "unavailable_reason": "no per-file version declared in binding"}
    dependencies["public_key:" + binding["trust_root"]["public_key_path"]] = {
        "version": None, "sha256": PUBLIC_KEY_SHA256,
        "unavailable_reason": "public key bytes have no software version"}
    return dependencies


def compare_manifest_bindings(contract: CostContract, manifest: Any, *,
                              runtime_bytes: bytes, public_key_bytes: bytes,
                              expected_admission: Any, expected_code: Any) -> dict[str, Any]:
    """Compare metadata to independent inputs without authenticating them.

    expected_admission and expected_code must come from the trusted invoking
    layer, never from the manifest being checked. Equality does not verify a
    signature, nonce, Git ancestry, review, source file, or installed runtime.
    """
    checked = contract.validate_manifest_local_relations(manifest)
    run = checked["run"]
    for name, value in (("admission", expected_admission), ("code", expected_code)):
        _check_json_tree(value)
        fragment = contract.schema["$defs"]["manifest"]["properties"]["run"]["properties"][name]
        validator = jsonschema.Draft202012Validator({"$defs": contract.schema["$defs"], **fragment})
        try:
            error = next(validator.iter_errors(value), None)
        except (ValueError, TypeError, RecursionError) as exc:
            raise CostError("independent_binding_validation_failed", (name,), type(exc).__name__) from exc
        if error is not None:
            raise CostError("independent_binding_schema_error", (name, *error.absolute_path), str(error.validator))
        if canonical_json(run[name]) != canonical_json(value):
            raise CostError("manifest_independent_binding_mismatch", (name,))
    admission = run["admission"]
    if admission["effective_contract_sha256"] != CONTRACT_SHA256 or admission["schema_sha256"] != SCHEMA_SHA256:
        raise CostError("manifest_fixed_contract_binding_mismatch")
    if run["inputs"]["parameters"]["effective_contract_sha256"] != CONTRACT_SHA256:
        raise CostError("manifest_parameter_contract_binding_mismatch")
    dependencies = pinned_dependency_projection(runtime_bytes, public_key_bytes)
    environment = run["environment"]
    if canonical_json(environment["dependencies"]) != canonical_json(dependencies):
        raise CostError("manifest_pinned_dependency_projection_mismatch")
    binding = json.loads(runtime_bytes.decode("utf-8"))
    runtime = binding["runtime"]
    if environment["python_version"] != runtime["python"] or environment["sage_version"] != runtime["sage_launcher_version"]:
        raise CostError("manifest_runtime_version_metadata_mismatch")
    if environment["operating_system"] != "Darwin" or environment["architecture"] != "arm64":
        raise CostError("manifest_runtime_platform_metadata_mismatch")
    return {"metadata_bindings_match": True, "dependency_entries_compared": len(dependencies),
            "installed_runtime_verified": False, "source_bytes_verified": False,
            "authorization_authenticated": False, "scientific_admission": False}


def compare_companion_bytes(contract: CostContract, manifest: Any,
                            companions: Iterable[tuple[str, Iterable[bytes]]], *,
                            checkpoint: CostCheckpoint | None = None) -> dict[str, Any]:
    """Hash actual supplied streams; never open paths taken from a manifest.

    Stream custody, artifact parsing and semantic validation are external
    obligations. This verifies exact bytes and declared set membership only.
    """
    checked = contract.validate_manifest_local_relations(manifest)
    declared = checked["run"]["artifacts"]
    allowed = set(contract.schema["$defs"]["manifest"]["properties"]["run"]["properties"]["artifacts"]["properties"])
    seen = set()
    total_bytes = 0
    for pair in companions:
        checkpoint_boundary(checkpoint, "companion_stream")
        if type(pair) is not tuple or len(pair) != 2:
            raise CostError("companion_stream_pair")
        name, chunks = pair
        if type(name) is not str or name not in allowed or name not in declared:
            raise CostError("undeclared_or_noncompanion_stream")
        if name in seen:
            raise CostError("duplicate_companion_stream", (name,))
        seen.add(name)
        digest = hashlib.sha256()
        size = 0
        for chunk in chunks:
            checkpoint_boundary(checkpoint, "companion_chunk")
            if type(chunk) is not bytes:
                raise CostError("companion_chunk_requires_bytes", (name,))
            digest.update(chunk)
            size += len(chunk)
        if declared[name] != {"sha256": digest.hexdigest(), "bytes": size}:
            raise CostError("companion_observed_bytes_mismatch", (name,))
        if checked["run"]["status"] == "completed_valid" and size == 0:
            raise CostError("completed_companion_is_empty", (name,))
        total_bytes += size
    if seen != set(declared):
        raise CostError("declared_companion_stream_missing")
    if checked["run"]["status"] == "completed_valid" and seen != allowed:
        raise CostError("completed_companion_set_incomplete")
    return {"companion_streams_compared": len(seen), "observed_bytes": total_bytes,
            "artifact_semantics_validated": False, "custody_authenticated": False,
            "scientific_admission": False}
