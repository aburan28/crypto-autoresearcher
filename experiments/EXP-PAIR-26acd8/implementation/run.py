"""Enumerate the product image on two curves over F_17.

The enumeration is the experiment. This module does not decide a
hypothesis status. A caller that passes --run-dir writes the three
artifacts and returns. Importing the module does not enumerate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

P = 17
A_E = (-1) % P
A_E0 = 1
T = (1, 0)
T0 = (0, 0)


def inv(a):
    a %= P
    if a == 0:
        raise ZeroDivisionError("division by zero in F_17")
    return pow(a, P - 2, P)


def add(p1, p2, a_coeff):
    """Chord-and-tangent sum. None is the point at infinity."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        if y1 % P == 0:
            return None
        lam = ((3 * x1 * x1 + a_coeff) * inv(2 * y1)) % P
    else:
        lam = ((y2 - y1) * inv(x2 - x1)) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def rhs(x, a_coeff):
    return (x * x * x + a_coeff * x) % P


def affine(a_coeff):
    points = []
    for x in range(P):
        right = rhs(x, a_coeff)
        for y in range(P):
            if (y * y) % P == right:
                points.append((x, y))
    return points


def measure(a_coeff, torsion):
    points = affine(a_coeff)
    on_curve = torsion in points
    order_two = on_curve and add(torsion, torsion, a_coeff) is None
    domain = [pt for pt in points if pt != torsion]
    images_ell = set()
    images_shift = set()
    images_base = set()
    by_base = {}
    zero_base = 0
    zero_ell = 0
    zero_shift = 0
    infinity = 0
    generic = set()
    for index, first in enumerate(domain):
        image_point = add(first, torsion, a_coeff)
        label = ((index % P) + 1) % P
        for second in points:
            xq = second[0]
            generic.add((label * xq) % P)
            if image_point is None:
                infinity += 1
                continue
            base = (first[0] * xq) % P
            ell = (image_point[0] * xq) % P
            shift = (((first[0] + 1) % P) * xq) % P
            images_base.add(base)
            images_ell.add(ell)
            images_shift.add(shift)
            by_base.setdefault(base, set()).add(ell)
            if base == 0:
                zero_base += 1
            if ell == 0:
                zero_ell += 1
            if shift == 0:
                zero_shift += 1
    n_s = len(domain) * len(points)
    branching = max((len(values) for values in by_base.values()), default=None)
    loss_record = {"n_S": n_s, "n_distinct_products": len(images_base)}
    gap = None
    if infinity == 0:
        gap = len(images_shift) - len(images_ell)
    return {
        "A": a_coeff,
        "I_base": len(images_base),
        "I_ell": len(images_ell),
        "I_generic": len(generic),
        "I_shift": len(images_shift),
        "L_integers": loss_record,
        "T": list(torsion),
        "b": branching,
        "gap": gap,
        "infinity_translations": infinity,
        "n_affine": len(points),
        "n_domain": len(domain),
        "on_curve": on_curve,
        "order_two": order_two,
        "zero_base": zero_base,
        "zero_ell": zero_ell,
        "zero_shift": zero_shift,
    }


def checks_pass(arm, arm0):
    return bool(
        P % 2 == 1
        and A_E % P != 0
        and A_E0 % P != 0
        and arm["on_curve"]
        and arm0["on_curve"]
        and arm["order_two"]
        and arm0["order_two"]
        and arm["infinity_translations"] == 0
        and arm0["infinity_translations"] == 0
        and arm["b"] is not None
        and arm["gap"] is not None
        and arm0["gap"] is not None
    )


def reading_row(ok, gap, branching, gap0):
    if not ok:
        return "instrument_failure"
    if gap >= 2 and branching >= 2 and gap0 <= 1:
        return "claim_holds"
    return "claim_fails"


def build_report():
    arm = measure(A_E, T)
    arm0 = measure(A_E0, T0)
    ok = checks_pass(arm, arm0)
    gap = arm["gap"]
    branching = arm["b"]
    gap0 = arm0["gap"]
    if ok:
        row = reading_row(True, gap, branching, gap0)
    else:
        row = "instrument_failure"
    return {
        "attack_claimed": False,
        "b": branching,
        "checks_pass": ok,
        "curve": "y^2 = x^3 - x",
        "curve_0": "y^2 = x^3 + x",
        "experiment_id": "EXP-PAIR-26acd8",
        "gap": gap,
        "gap0": gap0,
        "p": P,
        "reading_row": row,
        "run_id": "RUN-PAIR-20f63c",
        "source_idea": "IDEA-20261006-2cd127",
        "arm": arm,
        "arm0": arm0,
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
        "checks_pass: {ok}\n"
        "gap: {gap}\n"
        "b: {branch}\n"
        "gap0: {gap0}\n"
        "attack_claimed: false\n"
    ).format(
        row=report["reading_row"],
        ok="true" if report["checks_pass"] else "false",
        gap=report["gap"],
        branch=report["b"],
        gap0=report["gap0"],
    )
    reading_path.write_text(reading, encoding="utf-8")
    manifest = (
        "run:\n"
        "  id: RUN-PAIR-20f63c\n"
        "  experiment_id: EXP-PAIR-26acd8\n"
        "  status: completed\n"
        "  reading_row: {row}\n"
        "  note: >-\n"
        "    Observation only. This manifest does not change a hypothesis\n"
        "    status. A timeout is failed_infrastructure and is not this file.\n"
    ).format(row=report["reading_row"])
    manifest_path.write_text(manifest, encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    write_run(Path(args.run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
