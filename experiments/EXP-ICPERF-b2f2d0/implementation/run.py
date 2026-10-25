#!/usr/bin/env python3
"""Stage-0 instrument for EXP-ICPERF-b2f2d0.

Sixty-four geometric draws at success probability 1/50. Writes observations only.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

SEED = 20261017
P_DEN = 50
N_TARGETS = 64


def draw(state: int, p_den: int) -> tuple[int, int]:
    x = state & 0xFFFFFFFF
    k = 1
    while True:
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17)
        x ^= (x << 5) & 0xFFFFFFFF
        x &= 0xFFFFFFFF
        if x % p_den == 0:
            return k, x
        k += 1


def sample(seed: int) -> list[int]:
    state = seed
    draws = []
    for _ in range(N_TARGETS):
        k, state = draw(state, P_DEN)
        draws.append(k)
    return draws


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, required=True)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.stage != 0:
        raise SystemExit("this runner implements stage 0 only")
    if args.trial_id != "geometric-probe-sample":
        raise SystemExit("trial id is not the preregistered cell")
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    draws = sample(SEED)
    ordered = sorted(draws)
    sample_sum = sum(draws)
    sum_squares = sum(value * value for value in draws)
    median = ordered[31]
    if ordered[32] != median:
        raise RuntimeError("the two central order statistics differ")
    numer = N_TARGETS * sum_squares - sample_sum * sample_sum
    denom = sample_sum * sample_sum
    cv_in_band = numer * 100 >= denom * 81 and numer * 100 <= denom * 121
    median_ratio_in_band = (
        median * N_TARGETS * 5 >= sample_sum * 3
        and median * N_TARGETS * 5 <= sample_sum * 4
    )
    elapsed = time.perf_counter() - started
    payload = {
        "schema": "crypto.autoresearch.exp-icperf-b2f2d0.stage0.v1",
        "experiment_id": "EXP-ICPERF-b2f2d0",
        "hypothesis_id": "H-ICPERF-5adc9b",
        "trial_id": args.trial_id,
        "run_id": "RUN-ICPERF-b09be8",
        "stage": 0,
        "seed": SEED,
        "p_den": P_DEN,
        "n_targets": N_TARGETS,
        "sample_sum": sample_sum,
        "sum_squares": sum_squares,
        "median": median,
        "cv_in_band": cv_in_band,
        "median_ratio_in_band": median_ratio_in_band,
        "elapsed_seconds": elapsed,
        "claim_boundary": (
            "one seeded geometric sample at p = 1/50; not a host latency "
            "measurement and not a statement about any deployed curve"
        ),
    }
    (run_dir / "raw-result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = "\n".join(
        [
            "run:",
            "  id: RUN-ICPERF-b09be8",
            "  experiment_id: EXP-ICPERF-b2f2d0",
            "  status: observation",
            "  stage: 0",
            f"  sample_sum: {sample_sum}",
            f"  median: {median}",
            f"  cv_in_band: {str(cv_in_band).lower()}",
            f"  median_ratio_in_band: {str(median_ratio_in_band).lower()}",
            "",
        ]
    )
    (run_dir / "manifest.yaml").write_text(manifest, encoding="utf-8")
    text = "\n".join(
        [
            "# EXP-ICPERF-b2f2d0 stage 0 observations",
            "",
            "This file records one seeded sample. It does not measure host latency.",
            "",
            f"- seed {SEED}, p = 1/{P_DEN}, n = {N_TARGETS}",
            f"- sample_sum: {sample_sum}",
            f"- sum_squares: {sum_squares}",
            f"- median: {median}",
            f"- cv_in_band: {cv_in_band}",
            f"- median_ratio_in_band: {median_ratio_in_band}",
            f"- elapsed_seconds: {elapsed}",
            "",
        ]
    )
    (run_dir / "RESULTS.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
