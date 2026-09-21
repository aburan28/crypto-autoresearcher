"""Command line for the evaluation harness.

    python -m orchestration.eval validate --suite evals/suites/capability.yaml
    python -m orchestration.eval run      --suite ... --backend zai --trials 5
    python -m orchestration.eval compare  --suite ... --backends anthropic,zai

`validate` and `list` touch no network. `run` and `compare` spend real tokens:
trials x tasks x backends model-driven runs, so the trial count is always
explicit and never defaulted to something expensive.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..adapter import config as config_module
from ..adapter import resolver as resolver_module
from . import fingerprint as fingerprint_module
from . import report as report_module
from . import runner as runner_module
from .tasks import build_sandbox, load_suite


def _suite(args: argparse.Namespace):
    suite = load_suite(args.suite)
    kinds = args.kinds.split(",") if getattr(args, "kinds", None) else None
    ids = args.tasks.split(",") if getattr(args, "tasks", None) else None
    splits = (None if getattr(args, "split", None) in (None, "all")
              else [args.split])
    filtered = suite.filter(kinds, ids, splits)
    if not filtered.tasks:
        raise SystemExit("no tasks selected")
    return filtered


def cmd_list(args: argparse.Namespace) -> int:
    suite = _suite(args)
    print(f"{suite.name}: {len(suite.tasks)} task(s)\n")
    for task in suite.tasks:
        print(f"  {task.id:<28}{task.kind:<12}{task.role:<16}{task.policy}")
        print(f"      {task.summary}")
        print(f"      graders: {', '.join(g['type'] for g in task.graders)}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Offline: the suite parses, graders exist, fixtures build, policies resolve."""
    import tempfile
    suite = _suite(args)
    cfg = config_module.load()
    problems: list[str] = []
    for task in suite.tasks:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                build_sandbox(task, Path(tmp) / "sandbox")
        except Exception as exc:
            problems.append(f"{task.id}: fixture build failed: {exc}")
        if not task.policy:
            problems.append(f"{task.id}: handoff names no inference policy")
            continue
        try:
            resolver_module.resolve(
                cfg, task.policy, backend=args.backend,
                fallback_allowed=bool((task.handoff.get("inference") or {})
                                      .get("fallback_allowed")),
                independent_session=True)
        except (config_module.ConfigError, resolver_module.ResolutionError) as exc:
            problems.append(f"{task.id}: {exc}")
    if problems:
        print(f"{len(problems)} problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"OK: {len(suite.tasks)} task(s) valid, fixtures build, policies resolve"
          f"{' on ' + args.backend if args.backend else ''}")
    return 0


def _progress(result) -> None:
    mark = "pass" if result.passed else "FAIL"
    detail = "" if result.passed else "  " + "; ".join(
        f"{v.grader}: {v.detail}" for v in result.verdicts if not v.passed)[:160]
    if result.error:
        detail = "  " + result.error.splitlines()[0]
    print(f"  [{mark}] {result.task_id} trial {result.trial} "
          f"({result.stop_reason}, {result.steps} steps){detail}", file=sys.stderr)


def cmd_run(args: argparse.Namespace) -> int:
    suite = _suite(args)
    cfg = config_module.load()
    summary, trials = runner_module.run_suite(
        suite, config=cfg, backend=args.backend, trials=args.trials,
        keep_sandbox=Path(args.keep_sandboxes) if args.keep_sandboxes else None,
        seed_offset=args.seed_offset,
        progress=None if args.quiet else _progress)
    print(report_module.render(summary))

    if args.baseline:
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        current = fingerprint_module.harness_fingerprint(
            suite_path=str(args.suite), config_digest=cfg.digest)
        changed = fingerprint_module.changed_between(
            baseline.get("fingerprint") or {}, current)
        result = report_module.regression(baseline, summary)
        print()
        print(report_module.render_regression(result, changed_inputs=changed))
        if not result["safe_to_keep"]:
            return 1
    if args.out:
        for label, path in runner_module.write_results(
                summary, trials, args.out, suite_path=str(args.suite),
                config=cfg).items():
            print(f"# {label}: {path}", file=sys.stderr)
    passes, total, _ = summary.rate()
    return 0 if passes == total else 1


def cmd_baseline(args: argparse.Namespace) -> int:
    """Pin an existing result as the baseline future runs are measured against."""
    source = Path(args.source) / "summary.json" if Path(args.source).is_dir() \
        else Path(args.source)
    record = json.loads(source.read_text(encoding="utf-8"))
    target = Path(args.out)
    if target.exists() and not args.replace:
        raise SystemExit(
            f"{target} already exists; pass --replace to move the baseline "
            f"deliberately (a baseline that drifts silently measures nothing)")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"baseline: {target}")
    print(f"  from    {source}")
    print(f"  harness {fingerprint_module.describe(record.get('fingerprint') or {})}")
    overall = record.get("overall") or {}
    print(f"  overall {overall.get('passes')}/{overall.get('trials')} "
          f"{overall.get('interval')}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    suite = _suite(args)
    cfg = config_module.load()
    backends = [b.strip() for b in args.backends.split(",") if b.strip()]
    if len(backends) != 2:
        raise SystemExit("--backends takes exactly two, comma separated")

    summaries = []
    for backend in backends:
        print(f"\n=== {backend} ===", file=sys.stderr)
        summary, trials = runner_module.run_suite(
            suite, config=cfg, backend=backend, trials=args.trials,
            seed_offset=args.seed_offset,
            progress=None if args.quiet else _progress)
        summaries.append((summary, trials))
        print(report_module.render(summary))
        print()
        if args.out:
            runner_module.write_results(summary, trials,
                                        Path(args.out) / backend,
                                        suite_path=str(args.suite), config=cfg)

    left, right = summaries[0][0], summaries[1][0]
    comparisons = [report_module.compare(left, right, kind)
                   for kind in (None, "capability", "protocol", "discipline")
                   if left.rate(kind)[1]]
    print(report_module.render_comparison(comparisons))
    if args.out:
        path = Path(args.out) / "comparison.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise FileExistsError(f"{path} already exists; eval records are immutable")
        path.write_text(json.dumps(comparisons, indent=2) + "\n", encoding="utf-8")
        print(f"# comparison: {path}", file=sys.stderr)
    return 0


def cmd_harbor_probe(args: argparse.Namespace) -> int:
    """Offline. Says what is installed; never installs and never guesses."""
    from . import harbor as harbor_module

    detected = harbor_module.probe()
    if args.json:
        print(json.dumps(detected.to_dict(), indent=2))
    else:
        print(f"frontier: {detected.frontier or 'NOT FOUND'}")
        print(f"harbor:   {detected.harbor or 'NOT FOUND'}")
        print(f"docker:   {detected.docker or 'NOT FOUND'}")
        for note in detected.notes:
            print(f"note:     {note}")
        if detected.available:
            print("\nFrontier-CS/Harbor is runnable.")
        else:
            print(f"\nNOT runnable; missing: {', '.join(detected.missing)}")
            print("Install per https://github.com/FrontierCS/Frontier-CS "
                  "(Python 3.11+, Docker 24+, `uv sync`).")
    # Absence is a fact to report, not a failure of this command.
    return 0


def cmd_harbor_run(args: argparse.Namespace) -> int:
    from . import harbor as harbor_module

    suite = harbor_module.load_suite(args.suite)
    ids = args.tasks.split(",") if args.tasks else None
    tracks = args.tracks.split(",") if args.tracks else None
    splits = None if args.split == "all" else [args.split]
    selected = suite.filter(ids=ids, tracks=tracks, splits=splits)
    if not selected.tasks:
        raise SystemExit("no tasks selected")

    detected = harbor_module.probe()
    if not detected.available:
        # Refuse loudly rather than emit a record full of zeros. A missing
        # benchmark and a failed benchmark are different facts.
        print(f"error: Frontier-CS/Harbor unavailable; missing: "
              f"{', '.join(detected.missing)}", file=sys.stderr)
        print("No result record was written. Run `harbor-probe` for detail.",
              file=sys.stderr)
        return 3

    def progress(result) -> None:
        if not args.quiet:
            mark = "pass" if result.passed else "FAIL"
            print(f"  [{mark}] {result.task_id} trial {result.trial} "
                  f"score={result.score:.3f} ({result.stop_reason})",
                  file=sys.stderr)

    summary, trials = harbor_module.run_suite(
        selected, trials=args.trials, probe_result=detected, progress=progress)
    print(report_module.render(summary))

    if args.out:
        written = runner_module.write_results(
            summary, trials, args.out, suite_path=args.suite)
        for name, path in written.items():
            print(f"# {name}: {path}", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m orchestration.eval",
        description="Measure whether the harness solves problems, and whether "
                    "it refuses to overclaim.")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser, default_split: str = "all") -> None:
        p.add_argument("--suite", required=True)
        p.add_argument("--kinds", help="capability,protocol,discipline")
        p.add_argument("--tasks", help="comma-separated task ids")
        p.add_argument("--split", choices=["dev", "held_out", "all"],
                       default=default_split,
                       help="tune against dev; spend held_out sparingly")

    p_list = sub.add_parser("list", help="show the tasks in a suite")
    common(p_list)
    p_list.set_defaults(func=cmd_list)

    p_validate = sub.add_parser("validate", help="offline suite and policy check")
    common(p_validate)
    p_validate.add_argument("--backend")
    p_validate.set_defaults(func=cmd_validate)

    p_run = sub.add_parser("run", help="run the suite against one backend")
    common(p_run, default_split="dev")
    p_run.add_argument("--backend")
    p_run.add_argument("--trials", type=int, default=3,
                       help="repeats per task; one trial is an anecdote")
    p_run.add_argument("--out", help="directory for the immutable result record")
    p_run.add_argument("--keep-sandboxes", help="keep trial sandboxes here")
    p_run.add_argument("--baseline", help="compare against a pinned baseline record")
    p_run.add_argument("--seed-offset", type=int, default=0,
                       help="rotate generated fixtures so a suite cannot be memorised")
    p_run.add_argument("--quiet", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_baseline = sub.add_parser("baseline", help="pin a result as the baseline")
    p_baseline.add_argument("--source", required=True,
                            help="an evals/results/<name> directory or summary.json")
    p_baseline.add_argument("--out", required=True)
    p_baseline.add_argument("--replace", action="store_true")
    p_baseline.set_defaults(func=cmd_baseline)

    p_compare = sub.add_parser("compare", help="run two backends and compare honestly")
    common(p_compare, default_split="dev")
    p_compare.add_argument("--backends", required=True)
    p_compare.add_argument("--trials", type=int, default=5)
    p_compare.add_argument("--out")
    p_compare.add_argument("--seed-offset", type=int, default=0)
    p_compare.add_argument("--quiet", action="store_true")
    p_compare.set_defaults(func=cmd_compare)

    p_probe = sub.add_parser(
        "harbor-probe",
        help="report whether Frontier-CS/Harbor can run here (offline, no cost)")
    p_probe.add_argument("--json", action="store_true")
    p_probe.set_defaults(func=cmd_harbor_probe)

    p_harbor = sub.add_parser(
        "harbor-run",
        help="run an external Frontier-CS suite through Harbor")
    p_harbor.add_argument("--suite", required=True)
    p_harbor.add_argument("--tasks", help="comma-separated task ids")
    p_harbor.add_argument("--tracks", help="algorithmic,research,2.0")
    p_harbor.add_argument("--split", choices=["dev", "held_out", "all"],
                          default="dev")
    p_harbor.add_argument("--trials", type=int, default=1,
                          help="repeats per problem; Frontier-CS trials are "
                               "expensive, so this defaults to 1 rather than 3")
    p_harbor.add_argument("--out", help="directory for the immutable record")
    p_harbor.add_argument("--quiet", action="store_true")
    p_harbor.set_defaults(func=cmd_harbor_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (config_module.ConfigError, resolver_module.ResolutionError,
            FileNotFoundError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
