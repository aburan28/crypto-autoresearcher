"""`autoresearch formal` — drive one formalization attempt from the shell.

Deliberately thin.  It runs a single bounded task and prints an inspectable
proof artifact; it does not queue work, write the ledger, or transition
anything.  Promotion of a verified proof into claim state stays a Coordinator
decision made against the artifact this prints.

    autoresearch formal doctor
    autoresearch formal formalize --task-file formal/targets/ncp-affine-normal-form.yaml
    autoresearch formal formalize --task-id TASK-... --claim-id CL-... \\
        --claim-file claim.txt --theorem-name Foo.bar --theorem-file Foo/Bar.lean

Prefer --task-file: a frozen spec is what the Coordinator queued, and a
hand-typed claim on the command line is a different claim nobody approved.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .lean_worker import LeanWorker
from .mathcode import MathCodeConfig, MathCodeFormalizer
from .models import FormalProofTask, FormalTaskKind

REPO_ROOT = Path(__file__).resolve().parents[2]


def _repo_commit(repo_root: Path) -> str | None:
    """The commit the artifact was produced against, or None if unknowable."""

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def cmd_doctor(args: argparse.Namespace) -> int:
    """Report what is installed, without pretending anything about what is not."""

    repo_root = Path(args.repo_root).resolve()
    config = MathCodeConfig.from_env()
    formalizer = MathCodeFormalizer(repo_root, config=config)

    binary = formalizer.resolve_binary()
    print(f"repository   {repo_root}")
    print(f"engine       {config.binary}")
    if binary is None:
        print("             NOT FOUND on PATH — see docs/mathcode-integration.md")
    else:
        print(f"             {binary}")
        print(f"             version {formalizer.engine_version() or 'not reported'}")
    print(f"effort       {config.effort}")
    print(f"timeout      {config.timeout_seconds}s")
    print(f"attempt root {config.attempt_root}")
    for key in sorted(config.engine_env):
        print(f"  {key}={config.engine_env[key]}")

    workspace = repo_root / args.workspace
    print(f"\nworkspace    {workspace}")
    for name in ("lean-toolchain", "lakefile.toml", "lakefile.lean",
                 "lake-manifest.json", "AxiomAudit.lean", "CryptoResearch.lean"):
        marker = "present" if (workspace / name).is_file() else "missing"
        print(f"  {name:<20} {marker}")

    import shutil

    lake = shutil.which("lake")
    print(f"\nlake         {lake or 'NOT FOUND on PATH — verification cannot run'}")

    ready = binary is not None and lake is not None and (workspace / "lean-toolchain").is_file()
    print(f"\n{'ready' if ready else 'not ready'}: "
          f"{'formalize and verify can both run' if ready else 'see the missing items above'}")
    return 0 if ready else 1


def _task_from_args(args: argparse.Namespace) -> FormalProofTask:
    """Build the task from a frozen spec file, or from explicit flags."""

    if args.task_file:
        from .targets import load_spec, task_from_spec

        conflicting = [
            name
            for name in ("task_id", "claim_id", "claim", "claim_file",
                         "theorem_name", "theorem_file")
            if getattr(args, name)
        ]
        if conflicting:
            # Silently letting a flag win would run something other than the
            # spec that was reviewed and queued.
            raise ValueError(
                "--task-file is the frozen spec; it cannot be combined with "
                + ", ".join(f"--{name.replace('_', '-')}" for name in conflicting)
            )
        return task_from_spec(load_spec(args.task_file))

    missing = [
        name
        for name in ("task_id", "claim_id", "theorem_name", "theorem_file")
        if not getattr(args, name)
    ]
    if missing:
        raise ValueError(
            "without --task-file these are required: "
            + ", ".join(f"--{name.replace('_', '-')}" for name in missing)
        )

    if args.claim_file:
        claim = Path(args.claim_file).read_text(encoding="utf-8").strip()
    elif args.claim:
        claim = args.claim.strip()
    else:
        claim = sys.stdin.read().strip()
    if not claim:
        raise ValueError("empty claim")

    return FormalProofTask(
        task_id=args.task_id,
        kind=FormalTaskKind(args.kind),
        claim_id=args.claim_id,
        claim=claim,
        theorem_name=args.theorem_name,
        theorem_file=args.theorem_file,
        workspace=args.workspace,
        hypothesis_ids=tuple(args.hypothesis or ()),
    )


def cmd_formalize(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    task = _task_from_args(args)

    config = MathCodeConfig.from_env()
    if args.effort:
        config = MathCodeConfig(
            binary=config.binary,
            effort=args.effort,
            timeout_seconds=args.timeout or config.timeout_seconds,
            attempt_root=config.attempt_root,
            engine_env=config.engine_env,
        )
    elif args.timeout:
        config = MathCodeConfig(
            binary=config.binary,
            effort=config.effort,
            timeout_seconds=args.timeout,
            attempt_root=config.attempt_root,
            engine_env=config.engine_env,
        )

    formalizer = MathCodeFormalizer(repo_root, config=config)

    if args.print_prompt:
        print(formalizer.build_prompt(task))
        return 0

    from .pipeline import formalize_and_verify

    record = formalize_and_verify(
        task,
        formalizer=formalizer,
        worker=LeanWorker(repo_root, timeout_seconds=args.build_timeout),
    )
    artifact = record.as_proof_artifact(
        args.proof_id or f"FP-{task.task_id}",
        source_commit=_repo_commit(repo_root),
        workspace_root=repo_root / task.workspace,
    )

    text = json.dumps(artifact, indent=2, sort_keys=False)
    if args.artifact_out:
        out = Path(args.artifact_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"artifact written to {out}", file=sys.stderr)
    if args.json or not args.artifact_out:
        print(text)

    _summarize(record)

    if record.infrastructure_failure:
        return 3          # engine failure: not a result about the claim
    return 0 if record.machine_verified else 1


def _summarize(record) -> None:  # noqa: ANN001 - FormalRunRecord, imported lazily
    attempt = record.attempt
    lines = [f"\ntask       {record.task.task_id}",
             f"engine     {attempt.engine} {attempt.engine_version or '(version not reported)'}",
             f"attempt    {attempt.attempt_dir}"]
    if record.result is None:
        lines.append(f"outcome    INFRASTRUCTURE FAILURE ({attempt.failure.value})")
        lines.append(f"           {attempt.blocking_reason}")
        lines.append("           this is not evidence about the claim")
    else:
        lines.append(f"outcome    {record.result.status.value}")
        if record.result.blocking_reason:
            lines.append(f"           {record.result.blocking_reason}")
        if record.machine_verified:
            lines.append("           machine-verified — PENDING independent "
                         "semantic-fidelity review; not yet a research claim")
    print("\n".join(lines), file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autoresearch formal",
        description="Formalize a claim with MathCode and verify it with Lean.",
        epilog="Start with `autoresearch formal doctor`.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_doctor = sub.add_parser("doctor", help="is the engine and toolchain installed")
    p_doctor.add_argument("--workspace", default="formal")
    p_doctor.set_defaults(func=cmd_doctor)

    p_run = sub.add_parser("formalize", help="run one formalize-then-verify task")
    p_run.add_argument("--task-file",
                       help="a frozen crypto.autoresearch.formal_task.v1 spec "
                            "(formal/targets/*.yaml) -- preferred over the flags below")
    p_run.add_argument("--task-id")
    p_run.add_argument("--claim-id")
    p_run.add_argument("--claim", help="the claim text; or use --claim-file, or stdin")
    p_run.add_argument("--claim-file")
    p_run.add_argument("--theorem-name",
                       help="fully qualified Lean name, e.g. CryptoResearch.ECDLP.bound")
    p_run.add_argument("--theorem-file",
                       help="path inside the workspace, e.g. CryptoResearch/ECDLP/Bound.lean")
    p_run.add_argument("--kind", default=FormalTaskKind.FORMALIZE_CLAIM.value,
                       choices=[k.value for k in FormalTaskKind])
    p_run.add_argument("--workspace", default="formal")
    p_run.add_argument("--hypothesis", action="append", metavar="H-...")
    p_run.add_argument("--proof-id")
    p_run.add_argument("--effort", choices=["low", "medium", "high", "max"])
    p_run.add_argument("--timeout", type=int, help="engine budget in seconds")
    p_run.add_argument("--build-timeout", type=int, default=900,
                       help="lake build/audit budget in seconds")
    p_run.add_argument("--artifact-out", help="write the proof artifact here")
    p_run.add_argument("--json", action="store_true",
                       help="print the artifact even when also writing it")
    p_run.add_argument("--print-prompt", action="store_true",
                       help="show the exact engine prompt and exit without running it")
    p_run.set_defaults(func=cmd_formalize)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
