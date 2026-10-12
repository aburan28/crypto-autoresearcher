#!/usr/bin/env python3
"""Stage-0 joint-versus-separate step ratio for EXP-ECDLP-6f869c.

Four planted coefficients in Z/503Z. Not a curve walk and not an exponent claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


N = 503
R = 16
CAP = 2000
SEED_COUNT = 16
TARGET_COUNT = 4
MIN_FINISH = 12
LABEL = "IDEA-20261006-6374b1"
EXPERIMENT_ID = "EXP-ECDLP-6f869c"
RUN_ID = "RUN-ECDLP-3d61b8"


class Stream:
    def __init__(self, label: str) -> None:
        self.seed = hashlib.sha256(label.encode("utf-8")).digest()
        self.counter = 0
        self.buffer = b""

    def _byte(self) -> int:
        if not self.buffer:
            self.buffer = hashlib.sha256(self.seed + self.counter.to_bytes(8, "big")).digest()
            self.counter += 1
        value = self.buffer[0]
        self.buffer = self.buffer[1:]
        return value

    def below(self, bound: int) -> int:
        if bound <= 1:
            return 0
        limit = (1 << 32) // bound * bound
        while True:
            drawn = 0
            for _ in range(4):
                drawn = (drawn << 8) | self._byte()
            if drawn < limit:
                return drawn % bound


def nonzero(stream: Stream) -> int:
    return 1 + stream.below(N - 1)


def permutation() -> list[int]:
    items = list(range(N))
    stream = Stream(f"{LABEL}|pi")
    for index in range(N - 1, 0, -1):
        swap = stream.below(index + 1)
        items[index], items[swap] = items[swap], items[index]
    return items


def logs_for(seed: int) -> list[int]:
    stream = Stream(f"{LABEL}|{seed}|logs")
    drawn: list[int] = []
    while len(drawn) < TARGET_COUNT:
        value = nonzero(stream)
        if value not in drawn:
            drawn.append(value)
    return drawn


def jumps_for(seed: int) -> list[int]:
    stream = Stream(f"{LABEL}|{seed}|partition")
    return [nonzero(stream) for _ in range(R)]


def start_for(seed: int) -> int:
    return nonzero(Stream(f"{LABEL}|{seed}|gstart"))


def points_for(start: int, jumps: list[int]) -> list[int]:
    points = [start]
    current = start
    for _ in range(CAP):
        current = (current + jumps[current % R]) % N
        points.append(current)
    return points


def points_while(start: int, jumps: list[int]) -> list[int]:
    points = [start]
    current = start
    taken = 0
    while taken < CAP:
        current = (current + jumps[current % R]) % N
        points.append(current)
        taken += 1
    return points


def dp_map(points: list[int], distinguished) -> dict[int, int]:
    found: dict[int, int] = {}
    for step, point in enumerate(points):
        if distinguished(point) and point not in found:
            found[point] = step
    return found


def first_hit(target: int, jumps: list[int], stored: dict[int, int]) -> tuple[int, int, int] | None:
    current = target
    coefficient = 0
    for steps in range(CAP + 1):
        if current in stored:
            recovered = (current - coefficient) % N
            return steps, stored[current], recovered
        if steps == CAP:
            break
        jump = jumps[current % R]
        current = (current + jump) % N
        coefficient = (coefficient + jump) % N
    return None


def arm(logs: list[int], jumps: list[int], start: int, distinguished, point_fn) -> tuple[int, int] | None:
    stored = dp_map(point_fn(start, jumps), distinguished)
    pairs: list[tuple[int, int]] = []
    for target in logs:
        hit = first_hit(target, jumps, stored)
        if hit is None:
            return None
        target_steps, generator_steps, recovered = hit
        if recovered != target:
            return None
        pairs.append((generator_steps, target_steps))
    generator_cost = max(step for step, _ in pairs)
    separate = sum(generator + target for generator, target in pairs)
    joint = generator_cost + sum(target for _, target in pairs)
    return joint, separate


def h1_holds(start: int, jumps: list[int], steps: int, distinguished) -> bool | None:
    if steps <= 0:
        return None
    points = points_for(start, jumps)
    hits = sum(1 for point in points[1 : steps + 1] if distinguished(point))
    return 25 * abs(16 * hits - steps) <= 8 * steps


def labeling(distinguished, point_fn) -> dict:
    joint_steps: list[int] = []
    separate_steps: list[int] = []
    finished_seeds: list[int] = []
    first_h1 = None
    for seed in range(SEED_COUNT):
        scored = arm(logs_for(seed), jumps_for(seed), start_for(seed), distinguished, point_fn)
        if scored is None:
            continue
        joint, separate = scored
        if joint <= 0:
            continue
        finished_seeds.append(seed)
        joint_steps.append(joint)
        separate_steps.append(separate)
        if first_h1 is None:
            first_h1 = h1_holds(start_for(seed), jumps_for(seed), joint, distinguished)
    scored_ok = len(joint_steps) >= MIN_FINISH
    joint_median = separate_median = None
    at_least = below = False
    if scored_ok:
        joint_median = sorted(joint_steps)[(len(joint_steps) - 1) // 2]
        separate_median = sorted(separate_steps)[(len(separate_steps) - 1) // 2]
        at_least = 5 * separate_median >= 7 * joint_median
        below = 5 * separate_median < 7 * joint_median
    return {
        "finished": len(joint_steps),
        "finished_seeds": finished_seeds,
        "joint_steps": joint_steps,
        "separate_steps": separate_steps,
        "joint_median": joint_median,
        "separate_median": separate_median,
        "at_least_7_5": at_least,
        "strictly_below_7_5": below,
        "h1": first_h1,
    }


def census() -> dict:
    order = permutation()
    identity = labeling(lambda point: point % R == 0, points_for)
    permuted = labeling(lambda point: order[point] % R == 0, points_for)
    agree = True
    if identity["finished_seeds"]:
        seed = identity["finished_seeds"][0]
        left = arm(logs_for(seed), jumps_for(seed), start_for(seed), lambda point: point % R == 0, points_for)
        right = arm(logs_for(seed), jumps_for(seed), start_for(seed), lambda point: point % R == 0, points_while)
        agree = left == right and left is not None
    scored = bool(
        identity["finished"] >= MIN_FINISH
        and permuted["finished"] >= MIN_FINISH
        and identity["joint_median"] not in (None, 0)
        and permuted["joint_median"] not in (None, 0)
    )
    planted_ok = bool(agree and scored)
    matrix_holds = planted_ok and identity["at_least_7_5"] and not permuted["strictly_below_7_5"]
    return {
        "attack_claimed": False,
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "prime": N,
        "generator": 1,
        "targets": TARGET_COUNT,
        "seeds": SEED_COUNT,
        "cap": CAP,
        "branches": R,
        "minimum_finished": MIN_FINISH,
        "threshold_numerator": 7,
        "threshold_denominator": 5,
        "seed_label": LABEL,
        "identity": identity,
        "permuted": permuted,
        "implementations_agree": agree,
        "scanner_ok": agree,
        "scored": scored,
        "planted_ok": planted_ok,
        "matrix_holds": matrix_holds,
        "beyond_matrix": planted_ok and not matrix_holds,
    }


def write_outputs(run_dir: Path, result: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  experiment_id: {EXPERIMENT_ID}\n"
        f"  run_id: {RUN_ID}\n"
        "  attack_claimed: false\n"
        "  metrics:\n"
        f"    scanner_ok: {str(result['scanner_ok']).lower()}\n"
        f"    scored: {str(result['scored']).lower()}\n"
        f"    planted_ok: {str(result['planted_ok']).lower()}\n"
        f"    matrix_holds: {str(result['matrix_holds']).lower()}\n"
        f"    beyond_matrix: {str(result['beyond_matrix']).lower()}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    write_outputs(Path(args.run_dir), census())


if __name__ == "__main__":
    main()
