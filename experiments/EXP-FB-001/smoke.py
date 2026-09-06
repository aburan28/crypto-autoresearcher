#!/usr/bin/env python3
"""Small executable smoke campaign for EXP-FB-001.

This runner is intentionally conservative: by default it exercises 8/10/12-bit
curves and exact m=2 ground truth.  The frozen 20/24/28/32-bit evidence campaign
is a separate, budgeted run.  Pass --groebner to compare a bounded number of
same-target Semaev solves against the independent oracle.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from harness.factor_base_lab import FactorBaseSpec, compare_with_matched_random
from harness.toycurve import generate_instance


DEFAULT_FAMILIES = [
    "interval",
    "qr_window",
    "multiplicative_coset",
    "sparse_polynomial_predicate",
]


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_strs(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bits", default="8,10,12", help="comma-separated toy field sizes")
    ap.add_argument("--seeds", default="1,2,3", help="comma-separated deterministic curve seeds")
    ap.add_argument("--sizes", default="4,6,8", help="comma-separated requested factor-base sizes")
    ap.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    ap.add_argument("--targets", type=int, default=24)
    ap.add_argument("--scope", choices=["full_curve", "target_subgroup"], default="full_curve")
    ap.add_argument("--groebner", action="store_true")
    ap.add_argument("--groebner-target-limit", type=int, default=2)
    ap.add_argument("--output", default="-", help="JSON output path or - for stdout")
    args = ap.parse_args()

    rows: list[dict] = []
    failures: list[dict] = []
    for bits in parse_csv_ints(args.bits):
        for seed in parse_csv_ints(args.seeds):
            inst = generate_instance(seed=seed, field_bits=bits)
            for size in parse_csv_ints(args.sizes):
                for family in parse_csv_strs(args.families):
                    spec = FactorBaseSpec(
                        family=family,
                        requested_size=size,
                        seed=seed * 1009 + size,
                        scope=args.scope,
                    )
                    try:
                        comparison = compare_with_matched_random(
                            inst,
                            spec,
                            control_seed=seed * 7919 + size,
                            target_count=args.targets,
                            target_seed=seed * 104729 + size,
                            run_groebner=args.groebner,
                            groebner_target_limit=args.groebner_target_limit,
                        )
                    except ValueError as exc:
                        failures.append({
                            "bits": bits,
                            "seed": seed,
                            "size": size,
                            "family": family,
                            "scope": args.scope,
                            "error": str(exc),
                        })
                        continue

                    row = {
                        "bits": bits,
                        "seed": seed,
                        "p": inst.p,
                        "n": inst.n,
                        "size": size,
                        "family": family,
                        "scope": args.scope,
                        "structured": dataclasses.asdict(comparison.structured),
                        "random_control": dataclasses.asdict(comparison.random_control),
                        "yield_ratio": comparison.yield_ratio,
                    }
                    rows.append(row)
                    print(
                        f"bits={bits} seed={seed} size={size} family={family} "
                        f"Y={comparison.structured.decomposition_yield:.3f} "
                        f"Yrand={comparison.random_control.decomposition_yield:.3f} "
                        f"rank={comparison.structured.relation_rank}",
                        file=sys.stderr,
                        flush=True,
                    )

    payload = {
        "experiment_id": "EXP-FB-001",
        "claim_tier": "toy",
        "mode": "m2_matched_control_smoke",
        "groebner_enabled": bool(args.groebner),
        "rows": rows,
        "construction_failures": failures,
        "non_claims": [
            "not an asymptotic ECDLP result",
            "full_curve rows are geometry/solver measurements, not automatically logarithm systems",
            "m=3 frozen-contract lane is not implemented by this Python smoke runner",
        ],
    }
    text = json.dumps(payload, sort_keys=True, indent=2)
    if args.output == "-":
        print(text)
    else:
        path = pathlib.Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
