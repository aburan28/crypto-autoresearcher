#!/usr/bin/env python3
"""Opt-in, read-only presentation checks; never an experiment admission gate."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/experiment-observation.schema.json"


class PresentationLoader(yaml.SafeLoader):
    """Refuse silent duplicate-key replacement and YAML merge keys."""

    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise ValueError("YAML merge keys are not supported")
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise ValueError("mapping keys must be strings")
            if key in result:
                raise ValueError(f"duplicate YAML key: {key}")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def load(path):
    data = yaml.load(Path(path).read_text(), Loader=PresentationLoader)
    # Refuse implicit YAML dates, NaN/Infinity and recursive aliases.
    json.dumps(data, allow_nan=False)
    return data


def check(data, artifact_root=None):
    json.dumps(data, allow_nan=False)
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(data)
    ids = {}
    for group in ("observations", "controls", "patterns", "artifacts"):
        names = [item["id"] for item in data[group]]
        if len(names) != len(set(names)):
            raise ValueError(f"duplicate ID in {group}")
        ids[group] = set(names)
    if ids["observations"] & ids["controls"]:
        raise ValueError("observation and control IDs must be distinct")
    for group in ("controls", "patterns"):
        for item in data[group]:
            if set(item["observation_ids"]) - ids["observations"]:
                raise ValueError(f"{item['id']}: unknown observation reference")
            if set(item.get("reference_ids", [])) - (ids["observations"] | ids["controls"]):
                raise ValueError(f"{item['id']}: unknown pattern reference")
    for item in data["runs"] + data["observations"]:
        for evidence in item["evidence"]:
            if evidence["artifact"] not in ids["artifacts"]:
                raise ValueError(f"unknown evidence artifact: {evidence['artifact']}")
    missing = {item["field"] for item in data["missing"]}
    nulls = set()

    def visit(value, pointer=""):
        if value is None:
            nulls.add(pointer)
        elif isinstance(value, dict):
            for key, child in value.items():
                escaped = key.replace("~", "~0").replace("/", "~1")
                visit(child, pointer + "/" + escaped)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, pointer + "/" + str(index))

    visit(data)
    if nulls - missing:
        raise ValueError(f"null values need missing reasons: {sorted(nulls - missing)}")
    if missing - nulls:
        raise ValueError(f"missing entries must name null fields: {sorted(missing - nulls)}")
    for artifact in data["artifacts"]:
        path = Path(artifact["path"])
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("artifact paths must be repository-relative without '..'")
        if artifact_root is not None:
            root = Path(artifact_root).resolve()
            local = (root / path).resolve()
            if not local.is_relative_to(root):
                raise ValueError("artifact symlink escapes artifact root")
            if not local.is_file():
                raise ValueError(f"artifact unavailable locally: {path}")
            if hashlib.sha256(local.read_bytes()).hexdigest() != artifact["sha256"]:
                raise ValueError(f"artifact hash mismatch: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--check-artifacts", action="store_true")
    args = parser.parse_args()
    try:
        check(load(args.path), ROOT if args.check_artifacts else None)
    except (OSError, ValueError, TypeError, RecursionError, yaml.YAMLError,
            jsonschema.ValidationError) as exc:
        print(f"Presentation check failed: {exc}", file=sys.stderr)
        return 1
    print("Presentation structure/references passed" +
          ("; local artifact hashes matched" if args.check_artifacts else "") +
          ". Scientific validity was not assessed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
