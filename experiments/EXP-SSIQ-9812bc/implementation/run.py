"""Enumerate y1 fibers on two curves over F_361.

The histogram is the experiment. This module does not decide a
hypothesis status. A caller that passes --run-dir writes the three
artifacts and returns. Importing the module does not enumerate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

P = 19
Z2 = 2
Q = P * P


def fe_add(u, v):
    return ((u[0] + v[0]) % P, (u[1] + v[1]) % P)


def fe_mul(u, v):
    a, b = u
    c, d = v
    return ((a * c + Z2 * b * d) % P, (a * d + b * c) % P)


def fe_pow(u, n):
    result = (1, 0)
    base = u
    while n:
        if n & 1:
            result = fe_mul(result, base)
        base = fe_mul(base, base)
        n >>= 1
    return result


def fe_neg_coord(c):
    return (-c) % P


def is_square(u):
    if u == (0, 0):
        return True
    return fe_pow(u, (Q - 1) // 2) == (1, 0)


def rhs(x, a_coeff, b_coeff):
    x2 = fe_mul(x, x)
    x3 = fe_mul(x2, x)
    ax = fe_mul((a_coeff % P, 0), x)
    return fe_add(fe_add(x3, ax), (b_coeff % P, 0))


def all_field():
    for y0 in range(P):
        for y1 in range(P):
            yield (y0, y1)


def affine_points(a_coeff, b_coeff):
    points = []
    for x in all_field():
        right = rhs(x, a_coeff, b_coeff)
        for y in all_field():
            if fe_mul(y, y) == right:
                points.append((x, y))
    return points


def histogram_y1(points):
    counts = [0] * P
    for _x, y in points:
        counts[y[1]] += 1
    return counts


def rectangle_fibers():
    counts = [0] * P
    for y in all_field():
        counts[y[1]] += 1
    return counts


def sign_flip_fraction(points):
    if not points:
        return None
    good = 0
    for x, y in points:
        image = (fe_pow(x, P), fe_pow(y, P))
        if image[1][1] == fe_neg_coord(y[1]):
            good += 1
    return good, len(points)


def two_is_nonsquare():
    return pow(2, (P - 1) // 2, P) == P - 1


def discriminant(a_coeff, b_coeff):
    return (4 * pow(a_coeff, 3, P) + 27 * pow(b_coeff, 2, P)) % P


def reading_row(checks_pass, gap, n_a, n_n):
    if not checks_pass:
        return "instrument_failure"
    if gap <= 3:
        return "negative_gap"
    if gap < abs(n_a - n_n):
        return "sample_size_explains_gap"
    return "gap_meets_claim"


def build_report():
    disc_a = discriminant(1, 0)
    disc_n = discriminant(2, 3)
    irreducible = two_is_nonsquare()
    rect = rectangle_fibers()
    rect_ok = all(c == P for c in rect)
    points_a = affine_points(1, 0)
    points_n = affine_points(2, 3)
    hist_a = histogram_y1(points_a)
    hist_n = histogram_y1(points_n)
    m_a = max(hist_a) if hist_a else 0
    m_n = max(hist_n) if hist_n else 0
    gap = m_a - m_n
    flip_a = sign_flip_fraction(points_a)
    flip_n = sign_flip_fraction(points_n)
    flip_a_ok = flip_a is not None and flip_a[0] == flip_a[1]
    flip_n_ok = flip_n is not None and flip_n[0] == flip_n[1]
    checks_pass = (
        irreducible
        and disc_a != 0
        and disc_n != 0
        and rect_ok
        and flip_a_ok
        and flip_n_ok
    )
    row = reading_row(checks_pass, gap, len(points_a), len(points_n))
    return {
        "attack_claimed": False,
        "basis": "z^2 - 2",
        "checks_pass": checks_pass,
        "curve_a": "y^2 = x^3 + x",
        "curve_n": "y^2 = x^3 + 2x + 3",
        "discriminant_a": disc_a,
        "discriminant_n": disc_n,
        "experiment_id": "EXP-SSIQ-9812bc",
        "field": "F_361",
        "flip_a_failures": None if flip_a is None else flip_a[1] - flip_a[0],
        "flip_n_failures": None if flip_n is None else flip_n[1] - flip_n[0],
        "gap": gap,
        "histogram_a": hist_a,
        "histogram_n": hist_n,
        "irreducible": irreducible,
        "m_a": m_a,
        "m_n": m_n,
        "n_a": len(points_a),
        "n_n": len(points_n),
        "p": P,
        "reading_row": row,
        "rectangle_ok": rect_ok,
        "run_id": "RUN-SSIQ-ee5cdb",
        "source_idea": "IDEA-20261006-592877",
    }


def write_run(run_dir: Path) -> None:
    report = build_report()
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    reading_path = run_dir / "reading.yaml"
    manifest_path = run_dir / "manifest.yaml"
    raw_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reading = (
        "reading_row: {row}\n"
        "gap: {gap}\n"
        "m_a: {m_a}\n"
        "m_n: {m_n}\n"
        "n_a: {n_a}\n"
        "n_n: {n_n}\n"
        "checks_pass: {checks}\n"
        "attack_claimed: false\n"
    ).format(
        row=report["reading_row"],
        gap=report["gap"],
        m_a=report["m_a"],
        m_n=report["m_n"],
        n_a=report["n_a"],
        n_n=report["n_n"],
        checks=str(report["checks_pass"]).lower(),
    )
    reading_path.write_text(reading, encoding="utf-8")
    manifest = (
        "manifest:\n"
        "  experiment_id: EXP-SSIQ-9812bc\n"
        "  run_id: RUN-SSIQ-ee5cdb\n"
        "  command: python3 experiments/EXP-SSIQ-9812bc/implementation/run.py --run-dir {run_dir}\n"
        "  reading_row: {row}\n"
        "  attack_claimed: false\n"
    ).format(run_dir=run_dir.as_posix(), row=report["reading_row"])
    manifest_path.write_text(manifest, encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    write_run(Path(args.run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
