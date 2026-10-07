"""Frozen slope-image comparison for EXP-FROB-ad6a6d.

Writes manifest.yaml, raw-result.json, and reading.yaml. Does not
interpret the row as a discrete logarithm. The design session does
not call this module.
"""

from __future__ import annotations

import argparse
import json
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
A_COEFF = (1, 0, 0)
B_COEFF = (1, 0, 0)


def _git(args: list[str]) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=Path(__file__).resolve().parents[3], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def rhs(x: tuple[int, int, int], constant: tuple[int, int, int]) -> tuple[int, int, int]:
    return field.add(field.add(field.pow_elem(x, 3), x), constant)


def points_on(constant: tuple[int, int, int]) -> list[tuple[tuple[int, int, int], tuple[int, int, int]]]:
    found = []
    for x_int in range(field.ORDER):
        x = field.decode(x_int)
        target = rhs(x, constant)
        for y_int in range(field.ORDER):
            y = field.decode(y_int)
            if field.mul(y, y) == target:
                found.append((x, y))
    return found


def slope(p1, p2, inverse) -> tuple[int, int, int]:
    y_diff = field.sub(p2[1], p1[1])
    x_diff = field.sub(p2[0], p1[0])
    if x_diff == ZERO:
        raise ZeroDivisionError("vertical chord")
    return field.mul(y_diff, inverse(x_diff))


def frobenius(point):
    return (field.pow_elem(point[0], field.P), field.pow_elem(point[1], field.P))


def tangent_slope(point, inverse):
    # (3x^2 + A) / (2y) with A = 1.
    x, y = point
    numer = field.add(field.mul((3, 0, 0), field.mul(x, x)), ONE)
    denom = field.mul((2, 0, 0), y)
    if denom == ZERO:
        return None
    return field.mul(numer, inverse(denom))


def image_size(values: list[tuple[int, int, int]]) -> int:
    return len({field.encode(value) for value in values})


def reading_row(checks: dict[str, bool], lossy: bool, exceeds: bool) -> str:
    if not all(checks.values()):
        return "instrument_failure"
    if not lossy:
        return "not_lossy"
    if exceeds:
        return "image_exceeds_half"
    return "image_at_most_half"


def build_report() -> dict:
    disc = (4 * 1 + 27 * 1) % field.P  # 31 mod 7
    prime_poly_roots = [t for t in range(field.P) if field.poly_cube_plus_linear_plus_one(t) == 0]
    z_cube = field.pow_elem(ALPHA, 3)
    modulus_ok = field.add(field.add(z_cube, ALPHA), ONE) == ZERO
    base_points = points_on(B_COEFF)
    subset = [point for point in base_points if not field.is_base_field(point[0])]
    frobenius_slopes = []
    frobenius_vertical = 0
    for point in subset:
        image = frobenius(point)
        if field.sub(image[0], point[0]) == ZERO:
            frobenius_vertical += 1
            continue
        frobenius_slopes.append(slope(point, image, field.inv_fermat))
    i_frob = image_size(frobenius_slopes)
    sample_size = len(subset)

    random_slopes = []
    random_skipped = 0
    examined = 0
    for left in base_points:
        for right in base_points:
            if left == right:
                continue
            examined += 1
            if left[0] == right[0]:
                random_skipped += 1
                continue
            random_slopes.append(slope(left, right, field.inv_fermat))
            if len(random_slopes) == sample_size:
                break
        if len(random_slopes) == sample_size:
            break
    i_rand = image_size(random_slopes) if random_slopes else 0

    reversed_slopes = []
    for left in base_points:
        for right in base_points:
            if left == right:
                continue
            if right[0] == left[0]:
                continue
            reversed_slopes.append(slope(right, left, field.inv_fermat))
            if len(reversed_slopes) == sample_size:
                break
        if len(reversed_slopes) == sample_size:
            break
    i_rev = image_size(reversed_slopes) if reversed_slopes else 0

    tangent_values = []
    tangent_dropped = 0
    for point in subset:
        value = tangent_slope(point, field.inv_fermat)
        if value is None:
            tangent_dropped += 1
        else:
            tangent_values.append(value)
    i_tan = image_size(tangent_values) if tangent_values else 0

    check_count = min(20, len(subset))
    frobenius_ok = 0
    dual_ok = 0
    for point in subset[:check_count]:
        image = frobenius(point)
        image2 = frobenius(image)
        try:
            lam = slope(point, image, field.inv_fermat)
            lam_shift = slope(image, image2, field.inv_fermat)
            lam_other = slope(point, image, field.inv_egcd)
        except ZeroDivisionError:
            continue
        if lam_shift == field.pow_elem(lam, field.P):
            frobenius_ok += 1
        if lam_other == lam:
            dual_ok += 1

    null_points = points_on(ALPHA)
    null_fixed = 0
    for point in null_points:
        image = frobenius(point)
        if field.mul(image[1], image[1]) == rhs(image[0], ALPHA):
            null_fixed += 1

    drop_fraction_over_tenth = (
        examined > 0 and random_skipped * 10 > examined
    )
    lossy = i_frob > 0 and sample_size >= 2 * i_frob
    exceeds = i_frob > (i_rand // 2)
    checks = {
        "discriminant_nonzero": disc != 0,
        "modulus_relation": modulus_ok,
        "prime_polynomial_has_no_root": prime_poly_roots == [],
        "subset_at_least_20": sample_size >= 20,
        "random_sample_complete": len(random_slopes) == sample_size and sample_size > 0,
        "vertical_drop_at_most_one_tenth": not drop_fraction_over_tenth,
        "i_rand_at_least_2": i_rand >= 2,
        "frobenius_chords_nonvertical": frobenius_vertical == 0,
        "twenty_frobenius_identities": check_count == 20 and frobenius_ok == 20,
        "twenty_dual_slopes_agree": check_count == 20 and dual_ok == 20,
        "null_affine_frobenius_count_zero": null_fixed == 0,
        "i_frob_positive": i_frob > 0,
    }
    row = reading_row(checks, lossy, exceeds)
    h1_within_factor_two = (
        i_rand > 0
        and i_rev > 0
        and max(i_rand, i_rev) <= 2 * min(i_rand, i_rev)
    )
    return {
        "attack_claimed": False,
        "checks": checks,
        "experiment_id": "EXP-FROB-ad6a6d",
        "i_frob": i_frob,
        "i_rand": i_rand,
        "i_rev": i_rev,
        "i_tan": i_tan,
        "l_at_least_one": lossy,
        "l_denominator": i_frob,
        "l_numerator": len(frobenius_slopes),
        "null_affine_fixed_count": null_fixed,
        "reading_row": row,
        "sample_size": sample_size,
        "secondary_does_not_choose_row": True,
        "tangent_dropped": tangent_dropped,
        "threshold": i_rand // 2,
        "h1_within_factor_two": h1_within_factor_two,
        "vertical_skipped": random_skipped,
        "vertical_examined": examined,
        "frobenius_vertical": frobenius_vertical,
        "empty_bin_frob": field.ORDER - i_frob,
        "empty_bin_rand": field.ORDER - i_rand,
        "predicted_empty_numerator": str(field.ORDER * (field.ORDER - 1) ** sample_size),
        "predicted_empty_denominator": str(field.ORDER ** sample_size),
    }


def write_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=False)
    report = build_report()
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reading = {
        "attack_claimed": False,
        "i_frob": report["i_frob"],
        "i_rand": report["i_rand"],
        "reading_row": report["reading_row"],
        "threshold": report["threshold"],
        "l_at_least_one": report["l_at_least_one"],
    }
    (run_dir / "reading.yaml").write_text(
        yaml.safe_dump(reading, sort_keys=True), encoding="utf-8"
    )
    manifest = {
        "command": "python3 experiments/EXP-FROB-ad6a6d/implementation/run.py --run-dir " + str(run_dir),
        "experiment_id": "EXP-FROB-ad6a6d",
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
