"""Pinned Curvesmash verification phases; no combined execute/review process.

The upstream verifier owns snapshots, Docker isolation, review and scoring.
This bridge adds repository discovery, source pins and write-once stage outputs.
Exploratory judgments never change this repository's scientific state.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys

from .adapter import config as inference_config

SOURCE = Path(__file__).resolve().parents[1] / "config" / "curvesmash"
VERIFIER_REVISION = "8c1f098875fae0750c29ecfd641f7c9fc53a0f41"
VERIFIER_SHA256 = "5cdf6081831b44811674683d56623101ec5c9d61bc7f6baf4f0c906c7e2cfa27"
INSTALL = "python3 -m pip install -e '.[verifier]'"
PHASES = (
    "preflight", "intake", "prepare-runtime", "experiments", "review-initial",
    "followup", "review-final", "finalize", "export-results", "simulate",
)
CONSUMERS = {
    "prepare-runtime", "experiments", "review-initial", "followup",
    "review-final", "finalize",
}


def source_lock(directory: Path | None = None) -> dict:
    """Verify every imported protected file against its immutable source lock."""
    directory = SOURCE if directory is None else directory
    lock = json.loads((directory / "source-lock.json").read_text(encoding="utf-8"))
    if (not isinstance(lock, dict) or lock.get("schema") != "curvesmash-source-lock/v1"
            or lock.get("verifier_revision") != VERIFIER_REVISION
            or lock.get("verifier_content_sha256") != VERIFIER_SHA256
            or not isinstance(lock.get("files"), dict)
            or not isinstance(lock.get("tracks"), list)):
        raise ValueError("Curvesmash source/verifier lock mismatch")
    for name, expected in lock["files"].items():
        if not isinstance(name, str) or not isinstance(expected, str):
            raise ValueError("Invalid Curvesmash file lock")
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != name:
            raise ValueError("Unsafe Curvesmash source path")
        target = directory / name
        if (any(p.is_symlink() for p in (target, *target.parents))
                or hashlib.sha256(target.read_bytes()).hexdigest() != expected):
            raise ValueError(f"Curvesmash protected source changed: {name}")
    return lock


def init_curvesmash(track: str, output: Path) -> None:
    """Create a fresh challenge workspace with unchanged registered definitions."""
    lock = source_lock()
    if track not in lock["tracks"]:
        raise ValueError(f"Unknown Curvesmash track: {track}")
    output.mkdir(parents=True, exist_ok=False)
    for name in (*lock["files"], "source-lock.json", "NOTICE"):
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / name, target)
    candidate = f"submissions/{track}/candidate"
    submission = output / candidate
    submission.mkdir(parents=True)
    (output / "tracks" / track / "selected-submission.txt").write_text(
        candidate + "\n", encoding="utf-8")
    (submission / "submission.json").write_text(json.dumps({
        "version": 1, "title": f"{track}: incomplete research draft",
        "claims": ["TODO: state the complete attack, success argument, total "
                   "computation, memory, assumptions and evidence; no score is claimed."],
        "experiments": [],
    }, indent=2) + "\n", encoding="utf-8")
    (output / "README.md").write_text(
        f"# {track} verification workspace\n\n"
        f"Candidate: `{candidate}`. Replace the incomplete draft with your claim "
        "and supporting evidence. The first scored claim must give an exact "
        "rational bound. The draft has no score and cannot qualify.\n\n"
        f"Protected definitions: {lock['source_repository']}/tree/{lock['source_revision']}.\n"
        f"Verifier revision: `{VERIFIER_REVISION}`.\n\n"
        "Use `autoresearch verify preflight --root . --config "
        f"tracks/{track}/verifier.json --submission {candidate}` to check packaging.\n"
        "This does not execute experiments or establish scientific validity. "
        "Keep outputs outside submissions and use a fresh output for every phase.\n",
        encoding="utf-8")


def _backend():
    try:
        cli = importlib.import_module("llm_verifier.cli")
        artifacts = importlib.import_module("llm_verifier.artifacts")
    except ModuleNotFoundError as exc:
        if exc.name and exc.name.startswith("llm_verifier"):
            raise ValueError(f"Optional verifier is not installed; run: {INSTALL}") from None
        raise
    if artifacts.implementation()["content_sha256"] != VERIFIER_SHA256:
        raise ValueError(f"Verifier source differs from {VERIFIER_REVISION}; run: {INSTALL}")
    return cli, artifacts


def _outputs(args: argparse.Namespace) -> list[Path]:
    paths = [Path(value) for name in ("out", "score", "score_dir", "dossier", "results", "receipt")
             if (value := getattr(args, name, None)) is not None]
    if getattr(args, "results", None) and not args.receipt:
        paths.append(Path(args.results).parent / "accepted-results-receipt.json")
    return paths


@contextmanager
def _fresh_outputs(paths: list[Path]):
    """Reserve outputs against concurrent bridge writers; never delete an attempt."""
    paths = sorted({path.absolute() for path in paths})
    lock_paths = {path: path.with_name("." + path.name + ".autoresearch-lock") for path in paths}
    if ({path.resolve() for path in paths}
            & {path.resolve() for path in lock_paths.values()}):
        raise ValueError("Output paths overlap reserved verification lock paths")
    locks = []
    try:
        for path in paths:
            if path.exists() or path.is_symlink():
                raise FileExistsError(f"Output already exists; use a new attempt path: {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
            lock = lock_paths[path]
            with lock.open("x", encoding="utf-8"):
                pass
            locks.append(lock)
            if path.exists() or path.is_symlink():
                raise FileExistsError(f"Output already exists; use a new attempt path: {path}")
        yield
    finally:
        for lock in reversed(locks):
            lock.unlink()


def _help() -> None:
    print("usage: autoresearch verify COMMAND [options]\n")
    print("Curvesmash's pinned verifier, with separate credential-free execution,\n"
          "credentialed review and credential-free finalization phases.\n")
    print("  tracks                      list the six imported target tracks")
    print("  init-curvesmash --track ID --out DIR\n"
          "                              create protected rules and an incomplete draft")
    print("  " + "\n  ".join(PHASES))
    print("\nUse COMMAND --help for phase arguments. Install optional phases with:\n  " + INSTALL)
    print("\nEvery consuming phase requires --expected-intake (or LLMV_EXPECTED_INTAKE).\n"
          "Use fresh output paths. Exploratory acceptance is advisory; existing\n"
          "independent review, progress-fidelity and Coordinator gates still apply.")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        _help()
        return 0
    try:
        if argv[0] == "tracks":
            parser = argparse.ArgumentParser(prog="autoresearch verify tracks")
            parser.parse_args(argv[1:])
            print("\n".join(source_lock()["tracks"]))
            return 0
        if argv[0] == "init-curvesmash":
            parser = argparse.ArgumentParser(prog="autoresearch verify init-curvesmash")
            parser.add_argument("--track", required=True)
            parser.add_argument("--out", type=Path, required=True)
            args = parser.parse_args(argv[1:])
            init_curvesmash(args.track, args.out)
            print(f"Created incomplete draft in {args.out}; no review or experiments ran.")
            return 0
        if argv[0] not in PHASES:
            raise ValueError("Unknown verification phase; use autoresearch verify --help")
        cli, artifacts = _backend()
        args = cli.parser().parse_args(argv)
        if args.command in CONSUMERS:
            if not args.expected_intake or not re.fullmatch(r"[0-9a-f]{64}", args.expected_intake):
                raise ValueError("Supply the independently retained intake digest with "
                                 "--expected-intake or LLMV_EXPECTED_INTAKE")
        if args.command in {"intake", "preflight", "simulate"}:
            root = Path(args.root)
            if (root / "source-lock.json").exists() and source_lock(root) != source_lock():
                raise ValueError("Curvesmash workspace differs from the imported protected source")
        if args.command in {"review-initial", "review-final"}:
            from llm_verifier.files import read_json
            data = artifacts.verify_intake(read_json(args.intake), args.expected_intake)
            inference_config.load().assert_inference_target_allowed(
                "openai", data["effective"]["config"]["provider"]["model"],
                context="external advisory verifier")
        with _fresh_outputs(_outputs(args)):
            return int(cli.main(argv))
    except (OSError, ValueError, inference_config.ConfigError) as exc:
        print(f"autoresearch verify: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
