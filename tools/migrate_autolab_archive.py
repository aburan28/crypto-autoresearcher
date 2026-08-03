#!/usr/bin/env python3
"""Copy Autolab task/result roots and emit a content-addressed harness receipt.

The source repository is intentionally treated as dirty historical input.  Git
provenance is recorded, but byte-level provenance comes from the manifest.
AppleDouble files, Python bytecode caches, Git internals, and api_direct
checkpoint state are excluded because they are neither task definitions nor
research results.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import yaml


REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("/Volumes/SSD990/autolab")
DEFAULT_DESTINATION = REPO / "inputs" / "refs"
DEFAULT_METADATA = REPO / "inputs" / "archive_from_autolab" / "autolab-migration-20260802-r1"
DEFAULT_ROOTS = ("tasks", "research", "experiments", "output", "research_ledger.md")
EXCLUDED_DIRS = {".git", "__pycache__", ".agent-state"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
EXCLUDED_NAMES = {".DS_Store"}
PORT_TAG = "autolab-migration-20260802-r1"
EXPERIMENT_ID = "EXP-ALMIG-001"
RUN_ID = "RUN-ALMIG-001-import-r1"


@dataclass(frozen=True)
class FileBinding:
    root: str
    relative: str
    source: Path
    destination: Path
    kind: str = "file"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(repo: Path, *args: str) -> str | None:
    proc = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=False
    )
    value = proc.stdout.strip()
    return value or None


def git_dirty(repo: Path) -> bool | None:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return bool(proc.stdout)


def excluded(path: Path, relative: Path) -> bool:
    if path.name.startswith("._") or path.name in EXCLUDED_NAMES:
        return True
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True
    return any(part in EXCLUDED_DIRS for part in relative.parts)


def enumerate_bindings(
    source: Path, destination: Path, roots: Iterable[str]
) -> tuple[list[FileBinding], Counter[str]]:
    bindings: list[FileBinding] = []
    excluded_counts: Counter[str] = Counter()
    for root in roots:
        source_root = source / root
        destination_root = destination / root
        if source_root.is_file():
            relative = Path(source_root.name)
            if excluded(source_root, relative):
                excluded_counts["excluded_file"] += 1
                continue
            bindings.append(
                FileBinding(root, source_root.name, source_root, destination_root)
            )
            continue
        if not source_root.is_dir():
            excluded_counts["missing_root"] += 1
            continue
        for dirpath, dirnames, filenames in os.walk(source_root):
            current = Path(dirpath)
            traversable_dirs = []
            for dirname in sorted(dirnames):
                path = current / dirname
                relative = path.relative_to(source_root)
                if dirname in EXCLUDED_DIRS or excluded(path, relative):
                    continue
                if path.is_symlink():
                    bindings.append(
                        FileBinding(
                            root,
                            relative.as_posix(),
                            path,
                            destination_root / relative,
                            "symlink",
                        )
                    )
                else:
                    traversable_dirs.append(dirname)
            # os.walk does not visit symlinked directories when followlinks is
            # false, so bind the link itself above and remove it from traversal.
            dirnames[:] = traversable_dirs
            for filename in sorted(filenames):
                path = current / filename
                relative = path.relative_to(source_root)
                if excluded(path, relative):
                    excluded_counts["excluded_file"] += 1
                    continue
                bindings.append(
                    FileBinding(
                        root,
                        relative.as_posix(),
                        path,
                        destination_root / relative,
                        "symlink" if path.is_symlink() else "file",
                    )
                )
    bindings.sort(key=lambda item: (item.root, item.relative))
    return bindings, excluded_counts


def copy_and_hash(binding: FileBinding, verify_only: bool) -> dict:
    source_stat = binding.source.lstat()
    if binding.kind == "symlink":
        source_link = os.readlink(binding.source)
        source_hash = hashlib.sha256(source_link.encode("utf-8")).hexdigest()
        source_size = len(source_link.encode("utf-8"))
    else:
        source_link = None
        source_hash = sha256_file(binding.source)
        source_size = source_stat.st_size
    status = "verified_existing"
    destination_hash: str | None = None

    if binding.kind == "symlink":
        if binding.destination.is_symlink():
            destination_link = os.readlink(binding.destination)
            destination_hash = hashlib.sha256(destination_link.encode("utf-8")).hexdigest()
    elif binding.destination.is_file() and binding.destination.stat().st_size == source_size:
        destination_hash = sha256_file(binding.destination)
    if destination_hash != source_hash:
        if verify_only:
            status = (
                "missing"
                if not binding.destination.exists() and not binding.destination.is_symlink()
                else "hash_mismatch"
            )
        elif binding.kind == "symlink":
            binding.destination.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = binding.destination.parent / (
                f".{binding.destination.name}.autolab-migrate-{os.getpid()}"
            )
            if temporary_path.exists() or temporary_path.is_symlink():
                temporary_path.unlink()
            os.symlink(source_link, temporary_path)
            os.replace(temporary_path, binding.destination)
            destination_link = os.readlink(binding.destination)
            destination_hash = hashlib.sha256(destination_link.encode("utf-8")).hexdigest()
            if destination_hash != source_hash:
                raise RuntimeError(f"symlink copy mismatch for {binding.source}")
            status = "copied"
        else:
            binding.destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                prefix=f".{binding.destination.name}.autolab-migrate-",
                dir=binding.destination.parent,
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
            try:
                shutil.copy2(binding.source, temporary_path)
                destination_hash = sha256_file(temporary_path)
                if destination_hash != source_hash:
                    raise RuntimeError(f"copy hash mismatch for {binding.source}")
                os.replace(temporary_path, binding.destination)
            finally:
                if temporary_path.exists():
                    temporary_path.unlink()
            status = "copied"

    task_name = None
    if binding.root == "tasks":
        task_name = binding.relative.split("/", 1)[0]
    try:
        destination_path = binding.destination.relative_to(REPO).as_posix()
    except ValueError:
        destination_path = str(binding.destination)
    return {
        "source_root": binding.root,
        "relative_path": binding.relative,
        "destination_path": destination_path,
        "kind": binding.kind,
        "task_name": task_name,
        "size_bytes": source_size,
        "sha256": source_hash,
        "status": status,
    }


def tree_hash(rows: Iterable[dict]) -> str:
    digest = hashlib.sha256()
    for row in sorted(rows, key=lambda item: (item["source_root"], item["relative_path"])):
        digest.update(
            (
                f'{row["source_root"]}\0{row["relative_path"]}\0{row["kind"]}\0'
                f'{row["size_bytes"]}\0{row["sha256"]}\n'
            ).encode("utf-8")
        )
    return digest.hexdigest()


def load_task_metadata(source: Path, task_name: str) -> dict:
    task_file = source / "tasks" / task_name / "task.toml"
    if not task_file.is_file():
        return {}
    try:
        with task_file.open("rb") as handle:
            doc = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {"task_toml_parse_error": True}
    metadata = doc.get("metadata") or {}
    optimization = doc.get("optimization") or {}
    return {
        "version": doc.get("version"),
        "author": metadata.get("author"),
        "difficulty": metadata.get("difficulty"),
        "domain": metadata.get("domain"),
        "tags": metadata.get("tags") or [],
        "metric": optimization.get("metric"),
        "direction": optimization.get("direction"),
    }


def build_task_catalog(source: Path, rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["task_name"]:
            grouped[row["task_name"]].append(row)
    catalog = []
    for task_name in sorted(grouped):
        task_rows = grouped[task_name]
        descriptors = {
            Path(row["relative_path"]).name: row["destination_path"]
            for row in task_rows
            if Path(row["relative_path"]).name in {"task.toml", "instruction.md"}
        }
        result_count = sum(
            1
            for row in task_rows
            if any(
                token in Path(row["relative_path"]).name.lower()
                for token in ("result", "receipt", "report", "review", "audit", "ledger")
            )
        )
        catalog.append(
            {
                "task_name": task_name,
                **load_task_metadata(source, task_name),
                "file_count": len(task_rows),
                "result_like_file_count": result_count,
                "total_bytes": sum(row["size_bytes"] for row in task_rows),
                "tree_sha256": tree_hash(task_rows),
                "descriptors": descriptors,
            }
        )
    return catalog


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_harness_run(summary: dict, command: str, stdout: str, stderr: str) -> None:
    run_dir = REPO / "experiments" / EXPERIMENT_ID / "runs" / RUN_ID
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "command.txt").write_text(command + "\n", encoding="utf-8")
    (run_dir / "stdout.log").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text(stderr, encoding="utf-8")
    environment = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "dependencies": {"pyyaml": yaml.__version__, "copy_engine": "python-shutil"},
    }
    write_json(run_dir / "environment.json", environment)
    write_json(run_dir / "raw-result.json", summary)
    finished_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "run": {
            "id": RUN_ID,
            "experiment_id": EXPERIMENT_ID,
            "status": "completed_valid" if summary["valid"] else "completed_invalid",
            "code": {
                "commit": git_value(REPO, "rev-parse", "HEAD"),
                "dirty": git_dirty(REPO),
                "command": command,
            },
            "inference": {
                "requested_policy": "executor-mechanical",
                "resolved_model_id": "none (deterministic migration)",
                # No inference backend participates in this deterministic copy.
                # `model_verified` therefore must not imply a successful model probe.
                "model_verified": False,
                "reasoning_effort": "low",
                "fallback_used": False,
                "degraded_requirements": [],
                "adapter_version": None,
            },
            "environment": environment,
            "inputs": {
                "curve_id": "not_applicable",
                "seed": "deterministic-path-order",
                "parameters": {
                    "source_commit": summary["source"]["commit"],
                    "source_dirty": summary["source"]["dirty"],
                    "roots": summary["roots"],
                    "file_count": summary["file_count"],
                    "port_tag": PORT_TAG,
                },
            },
            "timing": {
                "started_at": summary["started_at"],
                "finished_at": finished_at,
                "wall_seconds": summary["wall_seconds"],
            },
            "resources": {"peak_rss_bytes": None, "cpu_seconds": None},
            "result": {
                "metrics": {
                    "files_verified": summary["file_count"],
                    "bytes_verified": summary["total_bytes"],
                    "tasks_cataloged": summary["task_count"],
                    "copied_files": summary["status_counts"].get("copied", 0),
                    "mismatches": summary["mismatch_count"],
                },
                "valid": summary["valid"],
                "invalid_reason": None if summary["valid"] else "missing or hash-mismatched files",
                "certificate": {
                    "kind": "none",
                    "verified": False,
                    "verifier": "sha256 archive integrity only; no scientific claim verified",
                },
            },
            "artifacts": {
                "command": "command.txt",
                "environment": "environment.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "raw_result": "raw-result.json",
                "file_manifest": f"../../../../inputs/archive_from_autolab/{PORT_TAG}/file_manifest.jsonl",
            },
        }
    }
    run_dir.joinpath("manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def write_docs(summary: dict, catalog: list[dict]) -> None:
    destination = REPO / "docs" / "autolab-migration-20260802.md"
    lines = [
        "# Autolab task and result migration (2026-08-02)",
        "",
        f"Port tag: `{PORT_TAG}`",
        f"Source commit: `{summary['source']['commit']}` (dirty: `{str(summary['source']['dirty']).lower()}`)",
        f"Archive tree SHA-256: `{summary['tree_sha256']}`",
        "",
        "## Scope and integrity boundary",
        "",
        f"- {summary['file_count']:,} files / {summary['total_bytes']:,} bytes verified across: "
        + ", ".join(f"`{root}`" for root in summary["roots"]),
        f"- {summary['task_count']} top-level Autolab task packages cataloged.",
        "- Source dirty state is explicit. The Git commit identifies the tracked base; per-file SHA-256 values bind tracked and untracked bytes.",
        "- Excluded: AppleDouble metadata, `.DS_Store`, Python bytecode/cache directories, Git internals, and api_direct checkpoint state.",
        "- `CORR-ALMIG-001` records and repairs the first run's omission of three directory-symlink fixture aliases.",
        "- The 48 GB `inputs/refs` mirror is a local working-tree archive and is not carried in GitHub; the portable Git records are the content manifests, catalog, and harness receipts.",
        "- This is archival migration evidence only. It does not re-run tasks, validate scientific claims, or upgrade any claim tier.",
        "",
        "## Harness bindings",
        "",
        f"- Experiment: `{EXPERIMENT_ID}`",
        f"- Run: `{RUN_ID}`",
        f"- File manifest: `inputs/archive_from_autolab/{PORT_TAG}/file_manifest.jsonl`",
        f"- Task catalog: `inputs/archive_from_autolab/{PORT_TAG}/task_catalog.json`",
        f"- Summary: `inputs/archive_from_autolab/{PORT_TAG}/migration_summary.json`",
        "",
        "## Materialize the local byte mirror",
        "",
        "The source was dirty, so reproducing the exact tree requires the same source",
        "worktree, not only its recorded base commit. Populate `inputs/refs` without",
        "overwriting the immutable canonical receipt:",
        "",
        "```bash",
        "python3 tools/migrate_autolab_archive.py --source /path/to/autolab \\",
        "  --no-harness-output \\",
        f"  --metadata-dir /tmp/{PORT_TAG}-materialize",
        "```",
        "",
        "The command copies only missing or differing entries, then SHA-256 checks every",
        "selected destination entry. Compare its temporary summary and tree hash with",
        f"the canonical `{PORT_TAG}` records before relying on it.",
        "",
        "## Structured historical experiment packages",
        "",
        "The earlier structured port is retained alongside the complete raw mirror: 84",
        "historical EXP/RUN packages (32 `ALPF`, 11 `ALBIN`, 38 `ALISO`, and 3 `ALECF`)",
        "are grouped by `EV-ALPF-001`, `EV-ALBIN-001`, `EV-ALISO-001`, and",
        "`EV-ALECF-001`. See `docs/autolab-port-inventory-20260731.md`. Those records",
        "remain historical imports with their original toy/feasibility ceilings; this",
        "migration does not promote them.",
        "",
        "## Task packages",
        "",
        "| Task | Domain | Files | Result-like | Bytes | Tree SHA-256 |",
        "|---|---|---:|---:|---:|---|",
    ]
    for task in catalog:
        lines.append(
            f"| `{task['task_name']}` | {task.get('domain') or 'unknown'} | "
            f"{task['file_count']} | {task['result_like_file_count']} | "
            f"{task['total_bytes']} | `{task['tree_sha256']}` |"
        )
    lines += [
        "",
        "## Verify without mutating the canonical receipt",
        "",
        "```bash",
        "python3 tools/migrate_autolab_archive.py --verify-only --no-harness-output \\",
        "  --source /path/to/autolab \\",
        f"  --metadata-dir /tmp/{PORT_TAG}-verify",
        "python3 tools/validate_ledger.py",
        "```",
        "",
        "The canonical run is immutable. The migration tool refuses to overwrite its",
        "existing harness receipt; any successor migration must use a new experiment or",
        "run identifier.",
        "",
    ]
    destination.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--metadata-dir", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--roots", default=",".join(DEFAULT_ROOTS))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--no-harness-output", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    canonical_manifest = (
        REPO / "experiments" / EXPERIMENT_ID / "runs" / RUN_ID / "manifest.yaml"
    )
    if canonical_manifest.exists() and not args.no_harness_output:
        print(
            "canonical migration receipt already exists; preserve it and use "
            "--verify-only --no-harness-output with a separate --metadata-dir",
            file=sys.stderr,
        )
        return 2
    started = datetime.now(timezone.utc)
    roots = tuple(root.strip() for root in args.roots.split(",") if root.strip())
    bindings, excluded_counts = enumerate_bindings(args.source, args.destination, roots)
    if not bindings:
        print("no source files selected", file=sys.stderr)
        return 2

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        rows = list(pool.map(lambda item: copy_and_hash(item, args.verify_only), bindings))

    status_counts = Counter(row["status"] for row in rows)
    mismatches = status_counts["missing"] + status_counts["hash_mismatch"]
    catalog = build_task_catalog(args.source, rows)
    finished = datetime.now(timezone.utc)
    summary = {
        "schema": "autolab-harness-migration-v1",
        "port_tag": PORT_TAG,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "wall_seconds": (finished - started).total_seconds(),
        "source": {
            "path": str(args.source),
            "commit": git_value(args.source, "rev-parse", "HEAD"),
            "branch": git_value(args.source, "branch", "--show-current"),
            "dirty": git_dirty(args.source),
        },
        "destination": str(args.destination),
        "roots": list(roots),
        "file_count": len(rows),
        "total_bytes": sum(row["size_bytes"] for row in rows),
        "task_count": len(catalog),
        "tree_sha256": tree_hash(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "mismatch_count": mismatches,
        "excluded_counts": dict(sorted(excluded_counts.items())),
        "valid": mismatches == 0,
        "scientific_claims_verified": False,
    }

    write_jsonl(args.metadata_dir / "file_manifest.jsonl", rows)
    write_json(args.metadata_dir / "task_catalog.json", catalog)
    write_json(args.metadata_dir / "migration_summary.json", summary)

    stdout = (
        f"Autolab migration {PORT_TAG}\n"
        f"files={summary['file_count']} bytes={summary['total_bytes']} "
        f"tasks={summary['task_count']} mismatches={mismatches}\n"
        f"tree_sha256={summary['tree_sha256']}\n"
    )
    print(stdout, end="")
    if not args.no_harness_output:
        command = "python3 tools/migrate_autolab_archive.py"
        if args.verify_only:
            command += " --verify-only"
        write_harness_run(summary, command, stdout, "")
        write_docs(summary, catalog)
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
