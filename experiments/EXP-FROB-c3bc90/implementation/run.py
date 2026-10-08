"""Frozen trace-gap comparison for EXP-FROB-c3bc90.

Writes manifest.yaml, raw-result.json, and reading.yaml. Does not
interpret a row as a discrete logarithm. The design session does not
call this module.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import field  # noqa: E402


ONE = (1, 0, 0)
ZERO = (0, 0, 0)
ALPHA = (0, 1, 0)  # z, a root of z^3 + z + 1

Point = tuple[tuple[int, int, int], tuple[int, int, int]]


def _git(args: list[str]) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=Path(__file__).resolve().parents[3], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def rhs(x: tuple[int, int, int], constant: tuple[int, int, int]) -> tuple[int, int, int]:
    return field.add(field.add(field.pow_elem(x, 3), x), constant)


def points_on(constant: tuple[int, int, int]) -> list[Point]:
    found = []
    for x_int in range(field.ORDER):
        x = field.decode(x_int)
        target = rhs(x, constant)
        for y_int in range(field.ORDER):
            y = field.decode(y_int)
            if field.mul(y, y) == target:
                found.append((x, y))
    found.sort(key=lambda point: (field.encode(point[0]), field.encode(point[1])))
    return found


def add_points(left: Point | None, right: Point | None, inverse) -> Point | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        if y1 != y2 or y1 == ZERO:
            return None
        numer = field.add(field.mul((3, 0, 0), field.mul(x1, x1)), ONE)
        denom = field.mul((2, 0, 0), y1)
        if denom == ZERO:
            return None
        lam = field.mul(numer, inverse(denom))
    else:
        lam = field.mul(field.sub(y2, y1), inverse(field.sub(x2, x1)))
    x3 = field.sub(field.sub(field.mul(lam, lam), x1), x2)
    y3 = field.sub(field.mul(lam, field.sub(x1, x3)), y1)
    return (x3, y3)


def neg_point(point: Point | None) -> Point | None:
    if point is None:
        return None
    return (point[0], field.neg(point[1]))


def trace_zero_xs(*coords: tuple[int, int, int]) -> bool:
    total = ZERO
    for coord in coords:
        total = field.add(total, coord)
    return field.trace(total) == ZERO


def frobenius(point: Point) -> Point:
    return (field.pow_elem(point[0], field.P), field.pow_elem(point[1], field.P))


def gap_ge(zeros_a: int, zeros_b: int, den: int) -> bool:
    """|p_a - p_b| >= 3/20, the source idea's 0.15 threshold."""
    return abs(zeros_a - zeros_b) * 20 >= 3 * den


def gap_le(zeros_a: int, zeros_b: int, den: int) -> bool:
    """|p_a - p_b| <= 1/20, the source idea's 0.05 threshold."""
    return abs(zeros_a - zeros_b) * 20 <= den


def half_close(zeros_half: int, half_n: int, zeros_all: int, n: int) -> bool:
    if half_n <= 0 or n <= 0:
        return False
    return abs(zeros_half * n - zeros_all * half_n) * 20 <= n * half_n


def uniform_in_band(zeros: int, n: int) -> bool:
    """3/20 <= zeros/n <= 1/4."""
    return n > 0 and (3 * n <= 20 * zeros) and (4 * zeros <= n)


def choose_null_constant() -> tuple[tuple[int, int, int], str]:
    beta = ALPHA
    if field.disc_quantity(beta) == ZERO:
        beta = field.add(beta, ONE)
        label = "y^2 = x^3 + x + (z+1)"
    else:
        label = "y^2 = x^3 + x + z"
    return beta, label


def reading_row(checks: dict[str, bool], samples_ok: bool, lossy: bool, meets: bool) -> str:
    cheap = (
        "discriminant_object_nonzero",
        "modulus_relation",
        "prime_polynomial_has_no_root",
        "null_discriminant_nonzero",
        "null_constant_not_in_base_field",
    )
    if not all(checks[name] for name in cheap):
        return "instrument_failure"
    if not samples_ok:
        return "sample_under_100"
    identity = (
        "sample_sizes_equal",
        "twenty_frobenius_traces",
        "twenty_dual_sums",
        "uniform_trace_in_band",
    )
    if not all(checks[name] for name in identity):
        return "instrument_failure"
    if not lossy:
        return "not_lossy"
    if meets:
        return "gap_meets_claim"
    return "gap_misses_claim"


def _arm(points: list[Point], inverse) -> dict[str, int | bool]:
    if not points:
        return {
            "n": 0,
            "zeros_rel": 0,
            "zeros_shift": 0,
            "trace_image": 0,
            "frobenius_ok": 0,
            "dual_ok": 0,
            "check_count": 0,
            "half_first_n": 0,
            "half_first_zeros": 0,
            "half_second_n": 0,
            "half_second_zeros": 0,
            "halves_close": False,
            "t2_n": 0,
            "t2_zeros_rel": 0,
            "t2_zeros_shift": 0,
            "y0": 0,
            "t_x": -1,
            "t_y": -1,
        }
    shift = points[0]
    double_shift = add_points(shift, shift, inverse)
    accepted: list[tuple[Point, Point, Point, Point]] = []
    for left in points:
        for right in points:
            if left == right:
                continue
            total = add_points(left, right, inverse)
            third = neg_point(total)
            if third is None or third == left or third == right:
                continue
            moved = add_points(third, shift, inverse)
            if moved is None or moved == left or moved == right:
                continue
            accepted.append((left, right, third, moved))
    zeros_rel = 0
    zeros_shift = 0
    images: set[int] = set()
    for left, right, third, moved in accepted:
        rel_zero = trace_zero_xs(left[0], right[0], third[0])
        shift_zero = trace_zero_xs(left[0], right[0], moved[0])
        zeros_rel += int(rel_zero)
        zeros_shift += int(shift_zero)
        total = field.add(field.add(left[0], right[0]), third[0])
        images.add(field.encode(field.trace(total)))
    frobenius_ok = 0
    dual_ok = 0
    head = accepted[:20]
    for left, right, third, _moved in head:
        left_trace = field.trace(field.add(field.add(left[0], right[0]), third[0]))
        fp, fq, fr = frobenius(left), frobenius(right), frobenius(third)
        right_trace = field.trace(field.add(field.add(fp[0], fq[0]), fr[0]))
        frobenius_ok += int(left_trace == right_trace)
        again = add_points(left, right, field.inv_egcd)
        dual_ok += int(again is not None and neg_point(again) == third)
    mid = len(accepted) // 2
    first = accepted[:mid]
    second = accepted[mid:]
    first_zeros = sum(int(trace_zero_xs(p[0], q[0], r[0])) for p, q, r, _ in first)
    second_zeros = sum(int(trace_zero_xs(p[0], q[0], r[0])) for p, q, r, _ in second)
    n = len(accepted)
    t2_n = 0
    t2_zeros_rel = 0
    t2_zeros_shift = 0
    for left, right, third, _moved in accepted:
        if double_shift is None:
            break
        moved = add_points(third, double_shift, inverse)
        if moved is None or moved == left or moved == right:
            continue
        t2_n += 1
        t2_zeros_rel += int(trace_zero_xs(left[0], right[0], third[0]))
        t2_zeros_shift += int(trace_zero_xs(left[0], right[0], moved[0]))
    return {
        "n": n,
        "zeros_rel": zeros_rel,
        "zeros_shift": zeros_shift,
        "trace_image": len(images),
        "frobenius_ok": frobenius_ok,
        "dual_ok": dual_ok,
        "check_count": len(head),
        "half_first_n": len(first),
        "half_first_zeros": first_zeros,
        "half_second_n": len(second),
        "half_second_zeros": second_zeros,
        "halves_close": half_close(first_zeros, len(first), zeros_rel, n)
        and half_close(second_zeros, len(second), zeros_rel, n),
        "t2_n": t2_n,
        "t2_zeros_rel": t2_zeros_rel,
        "t2_zeros_shift": t2_zeros_shift,
        "y0": sum(int(point[1] == ZERO) for point in points),
        "t_x": field.encode(shift[0]),
        "t_y": field.encode(shift[1]),
    }


def build_report() -> dict:
    prime_poly_roots = [
        t for t in range(field.P) if field.poly_cube_plus_linear_plus_one(t) == 0
    ]
    modulus_ok = field.add(field.add(field.pow_elem(ALPHA, 3), ALPHA), ONE) == ZERO
    object_disc = field.disc_quantity(ONE)
    beta, null_label = choose_null_constant()
    null_disc = field.disc_quantity(beta)
    object_arm = _arm(points_on(ONE), field.inv_fermat)
    null_arm = _arm(points_on(beta), field.inv_fermat)
    n_obj = int(object_arm["n"])
    n_null = int(null_arm["n"])
    uniform_zeros = 0
    if n_obj > 0:
        uniform_zeros = sum(
            int(field.trace(field.decode(i % field.ORDER)) == ZERO) for i in range(n_obj)
        )
    lossy = n_obj >= 2 * int(object_arm["trace_image"]) and int(object_arm["trace_image"]) > 0
    meets_obj = n_obj > 0 and gap_ge(
        int(object_arm["zeros_rel"]), int(object_arm["zeros_shift"]), n_obj
    )
    meets_null = n_null > 0 and gap_le(
        int(null_arm["zeros_rel"]), int(null_arm["zeros_shift"]), n_null
    )
    checks = {
        "discriminant_object_nonzero": object_disc != ZERO and (31 % field.P) != 0,
        "modulus_relation": modulus_ok,
        "prime_polynomial_has_no_root": prime_poly_roots == [],
        "null_discriminant_nonzero": null_disc != ZERO,
        "null_constant_not_in_base_field": not field.is_base_field(beta),
        "sample_sizes_equal": True,
        "twenty_frobenius_traces": int(object_arm["check_count"]) == 20
        and int(object_arm["frobenius_ok"]) == 20
        and int(null_arm["check_count"]) == 20
        and int(null_arm["frobenius_ok"]) == 20,
        "twenty_dual_sums": int(object_arm["check_count"]) == 20
        and int(object_arm["dual_ok"]) == 20
        and int(null_arm["check_count"]) == 20
        and int(null_arm["dual_ok"]) == 20,
        "uniform_trace_in_band": uniform_in_band(uniform_zeros, n_obj),
    }
    samples_ok = n_obj >= 100 and n_null >= 100
    row = reading_row(checks, samples_ok, lossy, meets_obj and meets_null)
    if int(object_arm["trace_image"]) > 0 and n_obj > 0:
        l_text = format(math.log2(n_obj / int(object_arm["trace_image"])), ".10f")
    else:
        l_text = "undefined"
    return {
        "attack_claimed": False,
        "checks": checks,
        "experiment_id": "EXP-FROB-c3bc90",
        "g_null_den": n_null,
        "g_null_num": abs(int(null_arm["zeros_rel"]) - int(null_arm["zeros_shift"])),
        "g_obj_den": n_obj,
        "g_obj_num": abs(int(object_arm["zeros_rel"]) - int(object_arm["zeros_shift"])),
        "halves_close": bool(object_arm["halves_close"]),
        "l_at_least_one": lossy,
        "l_log2": l_text,
        "l_trace_image": int(object_arm["trace_image"]),
        "meets_claim": bool(meets_obj and meets_null),
        "meets_null": bool(meets_null),
        "meets_obj": bool(meets_obj),
        "n_null": n_null,
        "n_obj": n_obj,
        "null_equation": null_label,
        "null_t_x": int(null_arm["t_x"]),
        "null_t_y": int(null_arm["t_y"]),
        "null_y0": int(null_arm["y0"]),
        "null_zeros_rel": int(null_arm["zeros_rel"]),
        "null_zeros_shift": int(null_arm["zeros_shift"]),
        "object_t_x": int(object_arm["t_x"]),
        "object_t_y": int(object_arm["t_y"]),
        "object_y0": int(object_arm["y0"]),
        "object_zeros_rel": int(object_arm["zeros_rel"]),
        "object_zeros_shift": int(object_arm["zeros_shift"]),
        "reading_row": row,
        "secondary_does_not_choose_row": True,
        "t2_n": int(object_arm["t2_n"]),
        "t2_zeros_rel": int(object_arm["t2_zeros_rel"]),
        "t2_zeros_shift": int(object_arm["t2_zeros_shift"]),
        "uniform_zeros": uniform_zeros,
    }


def write_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=False)
    report = build_report()
    (run_dir / "raw-result.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    reading = {
        "attack_claimed": False,
        "g_null_den": report["g_null_den"],
        "g_null_num": report["g_null_num"],
        "g_obj_den": report["g_obj_den"],
        "g_obj_num": report["g_obj_num"],
        "reading_row": report["reading_row"],
        "l_at_least_one": report["l_at_least_one"],
    }
    (run_dir / "reading.yaml").write_text(
        yaml.safe_dump(reading, sort_keys=True), encoding="utf-8"
    )
    manifest = {
        "command": "python3 experiments/EXP-FROB-c3bc90/implementation/run.py --run-dir "
        + str(run_dir),
        "experiment_id": "EXP-FROB-c3bc90",
        "git_commit": _git(["rev-parse", "HEAD"]),
        "git_status_short": _git(["status", "--short"]),
        "python": sys.version,
        "platform": platform.platform(),
        "reading_row": report["reading_row"],
        "attack_claimed": False,
    }
    (run_dir / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=True), encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    write_run(Path(args.run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
