#!/usr/bin/env python3
"""Read-only skill routing and catalog validation. Never executes listed tools."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys
import tomllib

import yaml


DEFAULT_ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError(f"duplicate JSON key: {key}")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"missing frontmatter: {path}")
    _, head, body = text.split("---", 2)
    metadata = yaml.safe_load(head)
    if not isinstance(metadata, dict) or not isinstance(metadata.get("name"), str) or not isinstance(metadata.get("description"), str):
        raise ValueError(f"invalid skill metadata: {path}")
    return metadata, body


def safe_path(root, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(f"unsafe repository path: {relative!r}")
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes repository: {relative}")
    return path


def load_catalog(root):
    catalog = read_json(root / "docs/skill-catalog.json")
    if catalog.get("schema") != "skill-catalog/v1":
        raise ValueError("unsupported skill catalog")
    return catalog


def route(catalog, intent, topic):
    if intent not in catalog["primary_intents"] or topic not in catalog["topics"]:
        raise ValueError("unknown intent or topic")
    profile = catalog["topics"][topic]
    primary = catalog["primary_intents"][intent] or profile
    names = {row["name"] for row in catalog["skills"]}
    if primary not in names or profile not in names:
        raise ValueError("route names a missing skill")
    support = [] if profile == primary or topic == "all" else [profile]
    return {"intent": intent, "topic": topic, "primary_skill": primary,
            "supporting_profiles": support,
            "selection_only": True,
            "execution": "existing run skill; no assessment preflight" if intent == "run" else "none",
            "canonical": next(row["canonical"] for row in catalog["skills"] if row["name"] == primary)}


def check(root, catalog, snapshot_only=False):
    errors = []
    names = set()
    for skill in catalog["skills"]:
        name = skill["name"]
        if name in names or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", name):
            errors.append(f"invalid or duplicate skill name: {name}")
        names.add(name)
        try:
            canonical = safe_path(root, skill["canonical"])
            adapter = safe_path(root, skill["adapter"])
            meta, _ = frontmatter(canonical)
            adapter_meta, body = frontmatter(adapter)
            if meta["name"] != name or adapter_meta["name"] != name:
                errors.append(f"name mismatch: {name}")
            if meta["description"] != skill["description"]:
                errors.append(f"stale catalog description: {name}")
            if skill["canonical"] not in body and name != "run":
                errors.append(f"adapter does not point to canonical skill: {name}")
            interface = canonical.parent / "agents/openai.yaml"
            if skill["action"] == "new":
                ui = yaml.safe_load(interface.read_text())["interface"]
                if not 25 <= len(ui["short_description"]) <= 64 or "$"+name not in ui["default_prompt"]:
                    errors.append(f"invalid skill UI metadata: {name}")
        except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
            errors.append(f"{name}: {exc}")
    discovered = {path.parent.name for path in (root / ".claude/skills").glob("*/SKILL.md")}
    if discovered != names:
        errors.append(f"uncataloged/missing skills: {sorted(discovered ^ names)}")
    for topic in catalog["topics"]:
        for intent in catalog["primary_intents"]:
            try:
                route(catalog, intent, topic)
            except ValueError as exc:
                errors.append(str(exc))
    inventory = read_json(safe_path(root, catalog["inventory"]))
    if inventory.get("schema") != "skill-tool-inventory/v1":
        errors.append("unsupported tool inventory")
    seen = set()
    for entry in inventory["entries"]:
        path = entry["path"]
        if path in seen:
            errors.append(f"duplicate tool inventory path: {path}")
        seen.add(path)
        try:
            local = safe_path(root, path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if entry["owner_skill"] not in names:
            errors.append(f"unknown tool owner: {path}")
        if not snapshot_only and entry.get("availability") != "pending-pr" and not local.is_file():
            errors.append(f"tracked source missing from checkout: {path}")
    for script in catalog["console_scripts"]:
        path = safe_path(root, script["project"])
        if path.exists():
            declared = tomllib.loads(path.read_text()).get("project", {}).get("scripts", {})
            if declared.get(script["name"]) != script["callable"]:
                errors.append(f"stale console entry point: {script['name']}")
        elif not snapshot_only:
            errors.append(f"missing console project: {path}")
    return {"ok": not errors, "errors": errors, "skills": len(names),
            "tools": len(inventory["entries"]),
            "verification_scope": "catalog/adapters and audited snapshot metadata" if snapshot_only else "catalog/adapters and current source-path presence",
            "runtime_verified": False}


def drift(root, inventory):
    """Report new CLI source surfaces; do not import or execute them."""
    known = {row["path"] for row in inventory["entries"]}
    rows = []
    failures = []
    for directory in ("tools", "src", "orchestration", "harness", "scripts", "groebner_compare", "kb/src", "ui", "formal"):
        for path in sorted((root / directory).rglob("*")):
            if not path.is_file() or any(part.startswith("test") for part in path.relative_to(root).parts) or "/fixtures/" in str(path):
                continue
            relative = path.relative_to(root).as_posix()
            if relative in known or not path.suffix in {".py", ".sh"}:
                continue
            if path.suffix == ".sh":
                rows.append(relative)
                continue
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source)
                has_cli = path.name == "__main__.py" or "__main__" in source or any(
                    isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main" for node in tree.body)
                if has_cli:
                    rows.append(relative)
            except (OSError, UnicodeError, SyntaxError) as exc:
                failures.append({"path": relative, "error": str(exc)})
    return {"uncataloged_entrypoints": sorted(set(rows)), "inspection_failures": failures,
            "coverage": "Python/sh CLI markers in maintained roots; not all executable semantics",
            "execution": "none"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=DEFAULT_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    pick = sub.add_parser("route")
    pick.add_argument("--intent", required=True)
    pick.add_argument("--topic", default="all")
    verify = sub.add_parser("check")
    verify.add_argument("--snapshot-only", action="store_true",
                        help="validate catalog against the audited inventory without claiming local source presence")
    sub.add_parser("drift")
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(args.repo)
        if args.command == "route":
            result = route(catalog, args.intent, args.topic)
        elif args.command == "list":
            result = {"skills": catalog["skills"], "intents": catalog["primary_intents"], "topics": catalog["topics"],
                      "console_scripts": catalog["console_scripts"]}
        elif args.command == "check":
            result = check(args.repo, catalog, args.snapshot_only)
        else:
            result = drift(args.repo, read_json(safe_path(args.repo, catalog["inventory"])))
        print(json.dumps(result, indent=2))
        return 1 if result.get("ok") is False else 0
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
