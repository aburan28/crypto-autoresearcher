#!/usr/bin/env python3
"""Machine-check every DISCHARGED formal target, and refuse to pass vacuously.

This is the CI gate for the formal research lane.  It is deliberately thin over
`autoresearch formal verify`, which is where the gate actually lives: forbidden
construct scan, `lake build`, project-wide `AxiomAudit.lean`, and then a
per-theorem audit that confirms the REQUESTED theorem was in what got audited.
Re-implementing any of that here would give the lane two definitions of
"verified" that could drift apart.

WHY THIS EXISTS.  `lean-verification.yml` built `formal/smoke` -- a pinned,
dependency-free control project -- and never the `formal/` workspace where
theorem files live.  So the job was green whether or not any proof compiled,
and the first real theorem landed on `main` with no CI having built it.

A TARGET WITH NO THEOREM FILE IS NOT A FAILURE.  The lane freezes a target spec
before anyone proves it; seven of the eight committed targets are in exactly
that state.  Work not yet done is reported as undischarged and does not fail
the gate -- otherwise staging a target would break the build for everyone.

BUT AN EMPTY RUN IS A FAILURE.  If nothing is verified, this gate is a no-op
that passes, which is the failure mode it was written to remove.  So it asserts
a FLOOR on the number of targets verified, per the corpus-count discipline in
CLAUDE.md: a floor, never an exact count, because discharged targets only
accumulate.  Raise `--min-verified` when the lane has reviewed proofs to spare;
never lower it to turn this green.

INFRASTRUCTURE FAILURE IS NOT NEGATIVE EVIDENCE.  AGENTS.md rule 3 is explicit,
and the verifier already separates the two: exit 1 is a mathematical verdict
(build failed, audit failed, forbidden construct), exit 3 is the toolchain
falling over.  Both leave CI red -- neither is a verified proof -- but they are
reported separately and this script exits 3 for the latter so a lake or network
failure is never read as a proof that did not check out.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration.formal.cli import main as formal_main
from orchestration.formal.targets import load_spec, task_from_spec

REPO_ROOT = Path(__file__).resolve().parents[1]

VERIFIED, NOT_VERIFIED, INFRASTRUCTURE = "verified", "NOT VERIFIED", "INFRASTRUCTURE FAILURE"
UNDISCHARGED = "undischarged (no theorem file yet)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--targets-dir", default="formal/targets")
    parser.add_argument("--artifact-dir", default="formal-receipts",
                        help="where the immutable verification receipts are written")
    parser.add_argument("--min-verified", type=int, default=1,
                        help="floor on verified targets; a run that verifies fewer fails")
    parser.add_argument("--build-timeout", type=int, default=900)
    args = parser.parse_args(argv)

    targets = sorted((REPO_ROOT / args.targets_dir).glob("*.yaml"))
    if not targets:
        print(f"error: no target specs under {args.targets_dir}", file=sys.stderr)
        return 2

    artifact_dir = Path(args.artifact_dir).resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)

    outcomes: list[tuple[str, str, str]] = []
    for spec_path in targets:
        name = spec_path.stem
        try:
            task = task_from_spec(load_spec(spec_path))
        except Exception as exc:  # a malformed spec is this gate's business
            outcomes.append((name, NOT_VERIFIED, f"unreadable spec: {exc}"))
            continue

        theorem = REPO_ROOT / task.workspace / task.theorem_file
        if not theorem.is_file():
            outcomes.append((name, UNDISCHARGED, task.theorem_file))
            continue

        receipt = artifact_dir / f"{name}.json"
        print(f"\n=== verifying {name} ({task.theorem_name}) ===", flush=True)
        code = formal_main(["verify", "--task-file", str(spec_path),
                            "--artifact-out", str(receipt),
                            "--build-timeout", str(args.build_timeout)])
        if code == 0:
            outcomes.append((name, VERIFIED, task.theorem_name))
        elif code == 3:
            outcomes.append((name, INFRASTRUCTURE, "toolchain failed; no mathematical conclusion"))
        else:
            outcomes.append((name, NOT_VERIFIED, f"verifier exit {code}"))

    verified = [o for o in outcomes if o[1] == VERIFIED]
    failed = [o for o in outcomes if o[1] == NOT_VERIFIED]
    infra = [o for o in outcomes if o[1] == INFRASTRUCTURE]

    print("\n" + "=" * 72)
    for name, status, detail in outcomes:
        print(f"  {status:<38} {name}  ({detail})")
    print("=" * 72)
    print(f"{len(verified)} verified, {len(failed)} not verified, {len(infra)} "
          f"infrastructure, {len(outcomes) - len(verified) - len(failed) - len(infra)} undischarged")
    print(f"receipts: {artifact_dir}")

    if failed:
        print("\nFAILED: a committed theorem file did not machine-check.", file=sys.stderr)
        return 1
    if infra:
        print("\nINFRASTRUCTURE FAILURE: verification could not run to a conclusion. "
              "This is NOT evidence against any claim (AGENTS.md rule 3).", file=sys.stderr)
        return 3
    if len(verified) < args.min_verified:
        print(f"\nFAILED: {len(verified)} target(s) verified, floor is {args.min_verified}. "
              "A gate that verifies nothing is a no-op that passes; if a proof was "
              "removed on purpose, lower the floor deliberately and say why.",
              file=sys.stderr)
        return 1
    print(f"\nOK: {len(verified)} target(s) machine-verified "
          "(independent semantic-fidelity review still required).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
