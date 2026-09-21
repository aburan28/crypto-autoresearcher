"""`autoresearch` — one entry point for running this locally.

The pieces each have their own CLI (`orchestration.adapter`,
`orchestration.agent`, `orchestration.eval`). This wraps them so there is a
single command to learn, plus the two things that were missing entirely:

    autoresearch doctor    is this machine actually ready, and what is missing
    autoresearch loop      measure -> compare to baseline -> verdict, in one go

`doctor` is the one to run first. It costs nothing and tells you exactly which
step is blocking, rather than letting you discover a missing key after spending
tokens on half a suite.
"""
from __future__ import annotations

import argparse
import importlib
import sys
from datetime import datetime, timezone
from pathlib import Path

from .adapter import config as config_module

REPO = config_module.REPO_ROOT
SUITES = REPO / "evals" / "suites"
BASELINES = REPO / "evals" / "baselines"
RESULTS = REPO / "evals" / "results"


def load_dotenv(path: Path | None = None, env: dict[str, str] | None = None) -> list[str]:
    """Load `.env` if present. Never overrides what is already in the shell.

    Wiring up credentials is the step people bounce off, and `.env` is the
    lowest-friction way to do it locally. Parsing is deliberately dumb --
    KEY=VALUE, `#` comments, optional surrounding quotes -- so there is no
    interpolation surprise and no dependency.
    """
    import os
    target = Path(path) if path else REPO / ".env"
    env = os.environ if env is None else env
    if not target.is_file():
        return []
    loaded = []
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip().removeprefix("export ").strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and value and key not in env:
            env[key] = value
            loaded.append(key)
    return loaded


# --------------------------------------------------------------------------
def _has(module: str) -> bool:
    try:
        importlib.import_module(module)
        return True
    except ImportError:
        return False


def cmd_doctor(args: argparse.Namespace) -> int:
    """Everything that must be true before a run, checked without spending money."""
    problems: list[str] = []
    notes: list[str] = []

    def ok(message: str) -> None:
        print(f"  OK    {message}")

    def warn(message: str, fix: str | None = None) -> None:
        print(f"  WARN  {message}")
        if fix:
            notes.append(fix)

    def fail(message: str, fix: str | None = None) -> None:
        print(f"  FAIL  {message}")
        problems.append(message)
        if fix:
            notes.append(fix)

    print("environment")
    version = sys.version_info
    if version >= (3, 11):
        ok(f"python {version.major}.{version.minor}.{version.micro}")
    else:
        fail(f"python {version.major}.{version.minor} (3.11+ required)")

    # Data files live at the repository root, so this only works from a
    # checkout -- an editable install, not a wheel in site-packages.
    if (REPO / "AGENTS.md").is_file() and (REPO / "agents").is_dir():
        ok(f"repository root {REPO}")
    else:
        fail(f"repository root not found at {REPO}",
             "install from a checkout: pip install -e .")

    print("\ndependencies")
    for module, label in (("yaml", "PyYAML"), ("sympy", "sympy")):
        ok(f"{label}") if _has(module) else fail(
            f"{label} missing", "pip install -r requirements-dev.txt")
    agent_ready = _has("langgraph") and _has("langchain_core")
    if agent_ready:
        ok("langgraph + langchain-core (api_direct runtime available)")
    else:
        warn("langgraph not installed — api_direct runtime and evals disabled",
             "pip install -r requirements-agent.txt")

    print("\nconfiguration")
    try:
        cfg = config_module.load()
        ok(f"policies, providers, bindings load ({cfg.digest})")
    except config_module.ConfigError as exc:
        fail(f"configuration invalid: {exc}")
        return _finish(problems, notes)

    print("\nbackends")
    from .adapter import resolver as resolver_module
    usable = []
    import os
    for name in sorted(cfg.backend_table):
        backend = cfg.backend(name)
        key_env = backend["api_key_env"]
        has_key = bool(os.environ.get(key_env)) or backend.get("api_key_optional")
        servable = sum(
            1 for policy in cfg.policy_table
            if not resolver_module._binding_blockers(
                cfg, policy, name, cfg.binding(name, policy)))
        url = cfg.base_url(name)
        if not has_key:
            warn(f"{name}: ${key_env} unset  ({servable}/{len(cfg.policy_table)} "
                 f"policies bound)  {url}",
                 f"set {key_env} in .env (see .env.example) to use {name}")
        elif servable == 0:
            warn(f"{name}: credentials present but no policy is bound",
                 f"fill model ids for {name} in orchestration/model-bindings.yaml")
        else:
            ok(f"{name}: ready ({servable}/{len(cfg.policy_table)} policies)  {url}")
            usable.append(name)
    if not usable:
        fail("no backend is usable",
             "set one API key and re-run: autoresearch doctor")
    else:
        notes.append(f"verify the configured model ids are real: "
                     f"autoresearch adapter doctor --probe")

    print("\nrole bindings")
    try:
        from .role_registry import check, load_policies, load_roles
        drift = check(load_roles(), load_policies())
        ok("role definitions match roles.yaml") if not drift else fail(
            f"{len(drift)} runtime-binding problem(s)",
            "python3 tools/check_runtime_bindings.py")
    except Exception as exc:
        fail(f"role registry unreadable: {exc}")

    print("\neval suites")
    if not agent_ready:
        warn("skipped — needs the api_direct runtime")
    else:
        from .eval.tasks import load_suite
        for path in sorted(p for p in SUITES.glob("*.yaml") if not p.name.startswith("._")):
            try:
                suite = load_suite(path)
                dev = len(suite.filter(splits=["dev"]).tasks)
                held = len(suite.filter(splits=["held_out"]).tasks)
                ok(f"{path.name}: {dev} dev + {held} held-out task(s)")
            except Exception as exc:
                fail(f"{path.name}: {exc}")
        baselines = sorted(BASELINES.glob("*.json"))
        if baselines:
            ok(f"baselines: {', '.join(p.stem for p in baselines)}")
        else:
            warn("no pinned baseline — the first loop run has nothing to "
                 "compare against",
                 "after a first run: autoresearch eval baseline "
                 "--source evals/results/<name> --out evals/baselines/<suite>.json")

    return _finish(problems, notes)


def _finish(problems: list[str], notes: list[str]) -> int:
    print()
    if problems:
        print(f"{len(problems)} blocking problem(s).")
    else:
        print("Ready.")
    for note in dict.fromkeys(notes):
        print(f"  next: {note}")
    return 1 if problems else 0


# --------------------------------------------------------------------------
def cmd_loop(args: argparse.Namespace) -> int:
    """Run the dev suites, compare against pinned baselines, report a verdict.

    This is the tuning loop in one command: change something, run this, and
    find out whether it helped, hurt, or landed in the noise.
    """
    from .eval import fingerprint as fingerprint_module
    from .eval import report as report_module
    from .eval import runner as runner_module
    from .eval.tasks import load_suite

    # `._*` are macOS AppleDouble siblings, not suites. They are gitignored, so
    # they never appear in review, but they sit next to every real suite on a
    # Mac and the glob would hand their binary contents to the YAML loader.
    suites = ([Path(p) for p in args.suites.split(",")] if args.suites
              else sorted(p for p in SUITES.glob("*.yaml")
                          if not p.name.startswith("._")))
    if not suites:
        raise SystemExit(f"no suites found in {SUITES}")

    cfg = config_module.load()
    backend = args.backend or cfg.default_backend()
    splits = None if args.split == "all" else [args.split]
    loaded = [(path, load_suite(path).filter(splits=splits)) for path in suites]
    total_trials = sum(len(s.tasks) * args.trials for _, s in loaded)

    print(f"backend  {backend}")
    print(f"split    {args.split}")
    print(f"trials   {args.trials} per task")
    print(f"total    {total_trials} model-driven runs")
    for path, suite in loaded:
        print(f"  {path.name}: {len(suite.tasks)} task(s)")
    if args.dry_run:
        print("\n--dry-run: nothing executed")
        return 0
    print()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    exit_code = 0
    for path, suite in loaded:
        if not suite.tasks:
            continue
        print(f"=== {suite.name} ===")
        summary, trials = runner_module.run_suite(
            suite, config=cfg, backend=backend, trials=args.trials,
            seed_offset=args.seed_offset,
            progress=None if args.quiet else _progress)
        print(report_module.render(summary))

        baseline_path = Path(args.baseline_dir) / f"{suite.name}.json"
        if baseline_path.is_file():
            import json
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            changed = fingerprint_module.changed_between(
                baseline.get("fingerprint") or {},
                fingerprint_module.harness_fingerprint(
                    suite_path=str(path), config_digest=cfg.digest))
            result = report_module.regression(baseline, summary)
            print()
            print(report_module.render_regression(result, changed_inputs=changed))
            if not result["safe_to_keep"]:
                exit_code = 1
        else:
            print(f"\nno baseline at {baseline_path} — nothing to compare against yet")

        if not args.no_record:
            out = Path(args.results_dir) / stamp / suite.name
            for label, written in runner_module.write_results(
                    summary, trials, out, suite_path=str(path), config=cfg).items():
                print(f"# {label}: {written}", file=sys.stderr)
        print()
    return exit_code


def _progress(result) -> None:
    mark = "pass" if result.passed else "FAIL"
    detail = "" if result.passed else "  " + "; ".join(
        f"{v.grader}: {v.detail}" for v in result.verdicts if not v.passed)[:140]
    print(f"  [{mark}] {result.task_id} trial {result.trial}{detail}",
          file=sys.stderr)


# --------------------------------------------------------------------------
def _delegate(module_path: str, argv: list[str]) -> int:
    module = importlib.import_module(module_path)
    return int(module.main(argv))


def cmd_adapter(args: argparse.Namespace) -> int:
    return _delegate("orchestration.adapter.cli", args.rest)


def cmd_agent(args: argparse.Namespace) -> int:
    return _delegate("orchestration.agent.cli", args.rest)


def cmd_eval(args: argparse.Namespace) -> int:
    return _delegate("orchestration.eval.cli", args.rest)


def cmd_campaign(args: argparse.Namespace) -> int:
    """Read-only campaign observations and the local peer-MCP daemon."""
    return _delegate("orchestration.campaign.cli", args.rest)


def cmd_formal(args: argparse.Namespace) -> int:
    """Formalize a claim with MathCode and verify it with Lean."""
    return _delegate("orchestration.formal.cli", args.rest)


def cmd_status(args: argparse.Namespace) -> int:
    """Where things stand, without running anything."""
    cfg = config_module.load()
    print(f"repository  {REPO}")
    print(f"backend     {cfg.default_backend()} (AUTORESEARCH_BACKEND overrides)")
    print(f"config      {cfg.digest}")
    from .eval import fingerprint as fingerprint_module
    print(f"harness     {fingerprint_module.describe(fingerprint_module.harness_fingerprint())}")
    results = sorted(RESULTS.glob("*")) if RESULTS.is_dir() else []
    print(f"results     {len(results)} recorded run(s)"
          + (f", latest {results[-1].name}" if results else ""))
    baselines = sorted(BASELINES.glob("*.json")) if BASELINES.is_dir() else []
    print(f"baselines   {', '.join(p.stem for p in baselines) or 'none pinned'}")
    return 0


def cmd_backends(args: argparse.Namespace) -> int:
    """Endpoints, credentials, and what each backend can actually serve."""
    import os
    from .adapter import resolver as resolver_module
    cfg = config_module.load()
    default = cfg.default_backend()

    for name in sorted(cfg.backend_table):
        backend = cfg.backend(name)
        key_env = backend["api_key_env"]
        key_set = bool(os.environ.get(key_env))
        optional = bool(backend.get("api_key_optional"))
        bound = [p for p in cfg.policy_table
                 if not resolver_module._binding_blockers(
                     cfg, p, name, cfg.binding(name, p))]
        marker = " (default)" if name == default else ""
        state = ("ready" if (key_set or optional) and bound else
                 "no credentials" if not (key_set or optional) else
                 "unbound — no model ids configured")
        print(f"\n{name}{marker}    {state}")
        print(f"  wire        {backend['wire']}")
        print(f"  url         {cfg.base_url(name)}")
        if backend.get("base_url_env"):
            print(f"  url override ${backend['base_url_env']}")
        print(f"  api key     ${key_env}"
              f"{'  [set]' if key_set else '  [optional]' if optional else '  [NOT SET]'}")
        print(f"  serves      {len(bound)}/{len(cfg.policy_table)} policies"
              + (f": {', '.join(bound)}" if bound and args.verbose else ""))
        if backend.get("notes") and args.verbose:
            print(f"  notes       {' '.join(str(backend['notes']).split())}")

    print(f"\nSelect one with AUTORESEARCH_BACKEND=<name>, or --backend on any "
          f"command.\nCopy .env.example to .env to set keys and URLs; "
          f"`autoresearch doctor` checks them.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autoresearch",
        description="Local entry point for the ECDLP autoresearch harness.",
        epilog="Start with `autoresearch doctor`.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_doctor = sub.add_parser("doctor", help="check this machine is ready to run")
    p_doctor.set_defaults(func=cmd_doctor)

    p_status = sub.add_parser("status", help="what is configured and recorded")
    p_status.set_defaults(func=cmd_status)

    p_backends = sub.add_parser(
        "backends", help="endpoints, API key variables, and what each can serve")
    p_backends.add_argument("--verbose", "-v", action="store_true")
    p_backends.set_defaults(func=cmd_backends)

    p_loop = sub.add_parser(
        "loop", help="run the eval suites and compare against pinned baselines")
    p_loop.add_argument("--backend")
    p_loop.add_argument("--trials", type=int, default=5)
    p_loop.add_argument("--split", choices=["dev", "held_out", "all"], default="dev")
    p_loop.add_argument("--suites", help="comma-separated suite paths")
    p_loop.add_argument("--seed-offset", type=int, default=0)
    p_loop.add_argument("--baseline-dir", default=str(BASELINES))
    p_loop.add_argument("--results-dir", default=str(RESULTS))
    p_loop.add_argument("--no-record", action="store_true")
    p_loop.add_argument("--dry-run", action="store_true",
                        help="show what would run, and how many model calls")
    p_loop.add_argument("--quiet", action="store_true")
    p_loop.set_defaults(func=cmd_loop)

    for name, handler, help_text in (
            ("adapter", cmd_adapter, "resolve policies, inspect backends"),
            ("agent", cmd_agent, "plan or run a single dispatched task"),
            ("eval", cmd_eval, "evaluation suites, baselines, comparisons"),
            ("campaign", cmd_campaign, "read-only campaign observations and peer coordination"),
            ("formal", cmd_formal, "formalize a claim in Lean and machine-check it")):
        p = sub.add_parser(name, help=help_text,
                           add_help=False)   # pass --help through to the sub-CLI
        p.add_argument("rest", nargs=argparse.REMAINDER)
        p.set_defaults(func=handler)
    return parser


def main(argv: list[str] | None = None) -> int:
    loaded = load_dotenv()
    args = build_parser().parse_args(argv)
    if loaded and args.command in ("doctor", "backends", "status"):
        print(f"loaded .env: {', '.join(loaded)}\n")
    try:
        return int(args.func(args))
    except config_module.ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130
