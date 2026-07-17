from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


SCHEMA_BY_KEY = {
    "research_question": "research-question.schema.json",
    "hypothesis": "hypothesis.schema.json",
    "experiment": "experiment.schema.json",
    "evidence": "evidence.schema.json",
    "coordinator_decision": "coordinator-decision.schema.json",
    "handoff": "handoff.schema.json",
    "run": "run-manifest.schema.json",
}


class RecordValidationError(ValueError):
    pass


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecordValidationError(f"{path}: invalid JSON: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def find_repo_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / "schemas").is_dir() and (candidate / "AGENTS.md").is_file():
            return candidate
    raise RecordValidationError(f"cannot locate repository root from {start}")


def _is_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise RecordValidationError(f"unsupported schema type: {expected}")


def validate_instance(value: Any, schema: dict[str, Any], location: str = "$") -> None:
    expected = schema.get("type")
    if expected is not None:
        expected_types = [expected] if isinstance(expected, str) else expected
        if not any(_is_type(value, item) for item in expected_types):
            raise RecordValidationError(
                f"{location}: expected {' or '.join(expected_types)}, "
                f"got {type(value).__name__}"
            )

    if "enum" in schema and value not in schema["enum"]:
        raise RecordValidationError(
            f"{location}: {value!r} is not one of {schema['enum']!r}"
        )
    if "const" in schema and value != schema["const"]:
        raise RecordValidationError(
            f"{location}: expected constant {schema['const']!r}, got {value!r}"
        )
    if isinstance(value, str) and "pattern" in schema:
        if re.fullmatch(schema["pattern"], value) is None:
            raise RecordValidationError(
                f"{location}: {value!r} does not match {schema['pattern']!r}"
            )
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise RecordValidationError(
                f"{location}: {value!r} is below minimum {schema['minimum']!r}"
            )
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise RecordValidationError(
                f"{location}: expected at least {schema['minItems']} items"
            )
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                validate_instance(item, item_schema, f"{location}[{index}]")
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise RecordValidationError(f"{location}: missing required key {key!r}")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                validate_instance(item, properties[key], f"{location}.{key}")
            elif schema.get("additionalProperties") is False:
                raise RecordValidationError(f"{location}: unexpected key {key!r}")


def validate_record(path: Path, repo_root: Path | None = None) -> str:
    value = read_json(path)
    if not isinstance(value, dict) or len(value) != 1:
        raise RecordValidationError(
            f"{path}: a research record must contain exactly one top-level object"
        )
    key = next(iter(value))
    if key not in SCHEMA_BY_KEY:
        raise RecordValidationError(f"{path}: unknown record type {key!r}")
    root = repo_root or find_repo_root(path.parent)
    schema = read_json(root / "schemas" / SCHEMA_BY_KEY[key])
    validate_instance(value, schema)
    return key


def iter_record_paths(paths: Iterable[Path]) -> Iterable[Path]:
    record_names = {
        "research-question.json",
        "hypothesis.json",
        "specification.json",
        "evidence.json",
        "decision.json",
        "handoff.json",
        "manifest.json",
    }
    for path in paths:
        if path.is_file():
            yield path
            continue
        if not path.is_dir():
            raise RecordValidationError(f"record path does not exist: {path}")
        for candidate in sorted(path.rglob("*.json")):
            if (
                candidate.name in record_names
                or candidate.name.startswith("evidence-")
                or candidate.name.startswith("decision-")
                or candidate.name.startswith("handoff-")
            ):
                yield candidate


def next_id(repo_root: Path, kind: str, area: str) -> str:
    kind = kind.upper()
    area = area.upper()
    if re.fullmatch(r"[A-Z][A-Z0-9-]*", kind) is None:
        raise RecordValidationError(f"invalid ID kind: {kind!r}")
    if re.fullmatch(r"[A-Z0-9][A-Z0-9-]*", area) is None:
        raise RecordValidationError(f"invalid ID area: {area!r}")
    prefix = f"{kind}-{area}-"
    pattern = re.compile(rf"\b{re.escape(prefix)}(\d{{3,}})\b")
    maximum = 0
    for path in repo_root.rglob("*.json"):
        if any(part.startswith(".") for part in path.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in pattern.finditer(content):
            maximum = max(maximum, int(match.group(1)))
    return f"{prefix}{maximum + 1:03d}"


def build_ledger_index(repo_root: Path) -> dict[str, Any]:
    experiments_root = repo_root / "experiments"
    experiments: list[dict[str, Any]] = []
    if experiments_root.is_dir():
        for directory in sorted(path for path in experiments_root.iterdir() if path.is_dir()):
            specification_path = directory / "specification.json"
            if not specification_path.is_file():
                continue
            validate_record(specification_path, repo_root)
            experiment = read_json(specification_path)["experiment"]
            runs: list[dict[str, Any]] = []
            for manifest_path in sorted((directory / "runs").glob("*/manifest.json")):
                validate_record(manifest_path, repo_root)
                manifest = read_json(manifest_path)["run"]
                runs.append(
                    {
                        "id": manifest["id"],
                        "status": manifest["status"],
                        "commit": manifest["code"]["commit"],
                        "seed": manifest["inputs"]["seed"],
                        "manifest": str(manifest_path.relative_to(repo_root)),
                    }
                )
            experiments.append(
                {
                    "id": experiment["id"],
                    "hypothesis_id": experiment["hypothesis_id"],
                    "status": experiment["status"],
                    "version": experiment["version"],
                    "path": str(directory.relative_to(repo_root)),
                    "runs": runs,
                }
            )
    return {"ledger": {"format_version": 1, "experiments": experiments}}
