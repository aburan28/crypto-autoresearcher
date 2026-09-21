#!/usr/bin/env python3
"""Render a frozen formal task spec as a dispatch-queue stanza.

Formal work needs no new role and no dispatcher change: a formalization is an
`executor` task that runs a frozen command and returns artifacts, which is
exactly what the existing queue schema describes. This prints the stanza to
paste into a batch's dispatch_queue.json, so the queued text and the text the
executor runs come from one file instead of two hand-copied command lines.

    python3 tools/formal_task.py formal/targets/ncp-affine-normal-form.yaml \
        --artifact-dir coordination/goals/GOAL-X/batches/BATCH-Y/tasks

Printing a stanza queues nothing and approves nothing. Admission stays a
Coordinator decision.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration.formal.targets import TargetError, dispatch_stanza, load_spec


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("spec", nargs="+", help="formal/targets/*.yaml")
    parser.add_argument("--artifact-dir",
                        help="the batch tasks directory the artifacts belong under; "
                             "required unless --validate-only")
    parser.add_argument("--priority", type=int, default=50)
    parser.add_argument("--wall-clock-seconds", type=int, default=2400)
    parser.add_argument("--validate-only", action="store_true",
                        help="check the specs load and build a task, print nothing else")
    args = parser.parse_args(argv)
    if not args.validate_only and not args.artifact_dir:
        parser.error("--artifact-dir is required unless --validate-only")

    repo_root = Path(__file__).resolve().parents[1]
    stanzas = []
    for path in args.spec:
        # Read from wherever the caller pointed, but put the REPOSITORY-RELATIVE
        # path in the stanza: a queue entry holding a machine-local path means
        # something different on the machine that runs it.
        resolved = Path(path).resolve()
        relative = (
            str(resolved.relative_to(repo_root))
            if resolved.is_relative_to(repo_root)
            else path
        )
        try:
            spec = load_spec(resolved)
        except TargetError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.validate_only:
            print(f"OK {relative}: {spec['task_id']} {spec['kind']} -> {spec['theorem_name']}")
            continue
        stanzas.append(
            dispatch_stanza(
                spec,
                spec_path=relative,
                artifact_dir=args.artifact_dir,
                priority=args.priority,
                wall_clock_seconds=args.wall_clock_seconds,
            )
        )

    if not args.validate_only:
        print(json.dumps(stanzas, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
