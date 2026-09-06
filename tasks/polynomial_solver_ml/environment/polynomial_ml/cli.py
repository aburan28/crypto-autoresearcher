from __future__ import annotations

import argparse
import json
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bounded synthetic polynomial-solver ML benchmark")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="generate, measure, train and evaluate into a NEW directory")
    run.add_argument("--output", required=True)
    run.add_argument("--profile", choices=("quick", "standard"), default="quick")
    run.add_argument("--seed", type=int, default=20260904)
    run.add_argument("--fit-seed", type=int, default=0)
    run.add_argument("--steps", type=int, default=1200)
    run.add_argument("--action-timeout", type=float, default=5.0)
    run.add_argument("--budget-seconds", type=float, default=600.0)
    verify = sub.add_parser("verify", help="read-only check of a run, including deterministic training replay")
    verify.add_argument("output")
    sub.add_parser("worker", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.command == "worker":
            from .solver import solve_case
            payload = json.load(sys.stdin)
            print(json.dumps(solve_case(**payload), allow_nan=False))
        elif args.command == "verify":
            from .verify import verify_run
            print(json.dumps(verify_run(args.output), indent=2, allow_nan=False))
        else:
            from .pipeline import run, write_json
            path = run(args.output, args.profile, args.seed, args.fit_seed,
                       args.action_timeout, args.budget_seconds, args.steps)
            from .verify import verify_run
            result = verify_run(path)
            receipt = path.with_name(path.name + ".verification.json")
            write_json(receipt, result)
            print(json.dumps({"output": str(path), "verification_receipt": str(receipt), **result}, indent=2))
        return 0
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
