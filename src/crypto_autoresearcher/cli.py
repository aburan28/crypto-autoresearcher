from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from .records import (
    RecordValidationError,
    build_ledger_index,
    find_repo_root,
    iter_record_paths,
    loads_json_strict,
    next_id,
    validate_record,
    write_json,
)
from .runner import run_experiment


def _json_value(value: str) -> Any:
    try:
        return loads_json_strict(value, "CLI parameter")
    except RecordValidationError:
        if (
            value in {"NaN", "Infinity", "-Infinity"}
            or value.lstrip().startswith(("{", "["))
            or re.fullmatch(
                r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?",
                value,
            )
        ):
            raise
        return value


def _parameters(values: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in values:
        if "=" not in item:
            raise RecordValidationError(f"parameter must be KEY=VALUE: {item!r}")
        key, value = item.split("=", 1)
        if not key or key in result:
            raise RecordValidationError(f"invalid or duplicate parameter: {key!r}")
        result[key] = _json_value(value)
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="crypto-autoresearcher")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    validate = subparsers.add_parser("validate", help="validate research records")
    validate.add_argument("paths", nargs="+", type=Path)

    new_id = subparsers.add_parser("new-id", help="allocate the next stable ID")
    new_id.add_argument("kind")
    new_id.add_argument("area")

    index = subparsers.add_parser("index", help="build the experiment ledger index")
    index.add_argument("--output", type=Path, default=Path("ledger.json"))

    run = subparsers.add_parser(
        "run", help="execute a draft development run or approved locked run"
    )
    run.add_argument("--experiment-dir", type=Path, required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument("--seed", type=int, required=True)
    run.add_argument("--curve-id")
    run.add_argument("--parameter", action="append", default=[])
    run.add_argument("--timeout", type=float)
    run.add_argument("--cwd", type=Path)
    run.add_argument("--allow-dirty", action="store_true")
    run.add_argument("--approval-lock", type=Path)
    run.add_argument("--approval-lock-sha256")
    run.add_argument("command", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        repo_root = find_repo_root(args.repo)
        if args.subcommand == "validate":
            count = 0
            for path in iter_record_paths(args.paths):
                kind = validate_record(path, repo_root)
                print(f"VALID {kind} {path}")
                count += 1
            print(f"validated {count} record(s)")
            return 0
        if args.subcommand == "new-id":
            print(next_id(repo_root, args.kind, args.area))
            return 0
        if args.subcommand == "index":
            output = args.output if args.output.is_absolute() else repo_root / args.output
            write_json(output, build_ledger_index(repo_root))
            print(output)
            return 0
        if args.subcommand == "run":
            command = args.command[1:] if args.command[:1] == ["--"] else args.command
            experiment_dir = (
                args.experiment_dir
                if args.experiment_dir.is_absolute()
                else repo_root / args.experiment_dir
            )
            run_path = run_experiment(
                repo_root=repo_root,
                experiment_dir=experiment_dir,
                run_id=args.run_id,
                command=command,
                seed=args.seed,
                curve_id=args.curve_id,
                parameters=_parameters(args.parameter),
                timeout_seconds=args.timeout,
                allow_dirty=args.allow_dirty,
                cwd=(
                    args.cwd
                    if args.cwd is None or args.cwd.is_absolute()
                    else repo_root / args.cwd
                ),
                approval_lock_path=(
                    args.approval_lock
                    if args.approval_lock is None or args.approval_lock.is_absolute()
                    else repo_root / args.approval_lock
                ),
                approval_lock_sha256=args.approval_lock_sha256,
            )
            manifest = json.loads((run_path / "manifest.json").read_text(encoding="utf-8"))
            print(json.dumps({"run_path": str(run_path), **manifest["run"]}, indent=2))
            return 0 if manifest["run"]["status"] == "completed_valid" else 1
    except RecordValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
