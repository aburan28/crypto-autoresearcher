"""Independent 2E-membership validation for EXP-ICPERF-42ef30 AP-3.

For #E = 2r with r odd, P lies in 2E exactly when rP is the identity.
This group-order test does not call the x-trace predicate. The trace predicate
is evaluated in a separate function solely for the prescribed cross-check.

The quadratic-twist control is excluded from this validation by frozen AR-3;
the exact conflict is recorded in
../../../problems/binary-twist-cofactor-stage1-conflict.md.
This module does not launch the experiment or measure a factor-base gain.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from sage.all import EllipticCurve, GF, factor
from sage.version import version as sage_version


def in_double_image_by_order(point, group_order: int) -> bool:
    """Test P in 2E without evaluating any x-coordinate trace."""
    if group_order % 4 != 2:
        raise ValueError("order test requires #E = 2r with r odd")
    return bool((group_order // 2) * point == point.curve()(0))


def in_double_image_by_trace(point, a2) -> bool:
    """Reference criterion for y^2+xy=x^3+a2*x^2+b over GF(2^n)."""
    if point == point.curve()(0):
        return True
    return int((point[0] + a2).trace()) == 0


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*arguments: str) -> str | None:
    process = subprocess.run(["git", *arguments], capture_output=True, text=True)
    return process.stdout.strip() if process.returncode == 0 else None


def _write_new(path: Path, value: dict):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def _draw_additional_b(n: int, seed: int, field, count: int = 1):
    generator = random.Random(seed + 1009 * n)
    selected = []
    draws = []
    while len(selected) < count and len(draws) < 32:
        encoded = generator.randrange(2, 1 << n)
        curve = EllipticCurve(field, [1, 1, 0, 0, field.from_integer(encoded)])
        order = int(curve.cardinality())
        accepted = order % 4 == 2 and encoded not in selected
        draws.append({"b": encoded, "group_order": order,
                      "accepted": accepted,
                      "reason": None if accepted else "AR-3 or duplicate"})
        if accepted:
            selected.append(encoded)
    if len(selected) < count:
        raise RuntimeError("seeded curve selection did not find enough AR-3 curves")
    return selected, draws


def validate_curve(n: int, a2_encoded: int, b_encoded: int, sample_count: int):
    field = GF(2**n, name="a")
    a2 = field.from_integer(a2_encoded)
    b = field.from_integer(b_encoded)
    if b == 0:
        raise ValueError("singular curve: b = 0")
    curve = EllipticCurve(field, [1, a2, 0, 0, b])
    order = int(curve.cardinality())
    if order % 4 != 2:
        raise ValueError(f"AR-3 refusal: #E={order} is not 2 mod 4")

    started = datetime.now(timezone.utc).isoformat()
    start_wall = time.monotonic()
    start_usage = resource.getrusage(resource.RUSAGE_SELF)
    loadavg_start = os.getloadavg()
    width = (n + 7) // 8
    digest = hashlib.sha256()
    disagreements = []
    checked = 0
    x_scanned = 0
    inside_by_order = 0
    for x_encoded in range(1 << n):
        points = sorted(curve.lift_x(field.from_integer(x_encoded), all=True),
                        key=lambda point: int(point[1].to_integer()))
        x_scanned += 1
        for point in points:
            y_encoded = int(point[1].to_integer())
            group_member = in_double_image_by_order(point, order)
            trace_member = in_double_image_by_trace(point, a2)
            digest.update(x_encoded.to_bytes(width, "little"))
            digest.update(y_encoded.to_bytes(width, "little"))
            digest.update(bytes((int(group_member), int(trace_member))))
            checked += 1
            inside_by_order += int(group_member)
            if group_member != trace_member:
                disagreements.append({"x": x_encoded, "y": y_encoded,
                                      "order_member": group_member,
                                      "trace_member": trace_member})
            if checked == sample_count:
                break
        if checked == sample_count:
            break
    if checked != sample_count:
        raise RuntimeError(f"only {checked} distinct affine points found")
    end_usage = resource.getrusage(resource.RUSAGE_SELF)
    rss_scale = 1 if sys.platform == "darwin" else 1024
    return {
        "n": n, "a2": a2_encoded, "b": b_encoded,
        "field_modulus": sum(int(coefficient) << i for i, coefficient in
                             enumerate(field.modulus().coefficients(sparse=False))),
        "group_order": order, "group_order_factorization": str(factor(order)),
        "odd_order": order // 2, "samples_requested": sample_count,
        "samples_checked": checked, "x_coordinates_scanned": x_scanned,
        "inside_by_order": inside_by_order,
        "disagreement_count": len(disagreements),
        "disagreements": disagreements,
        "point_and_predicate_sha256": digest.hexdigest(),
        "sampling_rule": "ascending polynomial-basis x; ascending encoded y for each lifted point; first N affine points",
        "started_utc": started,
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "wall_seconds": time.monotonic() - start_wall,
        "cpu_user_seconds": end_usage.ru_utime - start_usage.ru_utime,
        "cpu_system_seconds": end_usage.ru_stime - start_usage.ru_stime,
        "process_peak_rss_bytes": end_usage.ru_maxrss * rss_scale,
        "loadavg_start": list(loadavg_start),
        "loadavg_end": list(os.getloadavg()),
        "status": "agree" if not disagreements else "disagree",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples-per-curve", type=int, default=10000)
    parser.add_argument("--additional-seed", type=int, default=20260916)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    if args.samples_per_curve < 10000:
        parser.error("AP-3 requires at least 10000 points per curve")
    args.out_dir.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).resolve()
    manifest = {
        "kind": "AP-3 independent 2E-membership implementation validation",
        "experiment": "EXP-ICPERF-42ef30",
        "source_sha256": _sha256(source),
        "sage_version": sage_version,
        "python_version": platform.python_version(),
        "machine": platform.machine(),
        "platform": sys.platform,
        "exact_argv": sys.argv,
        "git_head": _git("rev-parse", "HEAD"),
        "git_status_porcelain": _git("status", "--porcelain"),
        "samples_per_curve": args.samples_per_curve,
        "additional_seed": args.additional_seed,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "curve_plan": [],
        "curve_selection_draws": {},
        "twist_order_diagnostic": [],
    }
    plan = [(n, 1, 1, "Trimoska") for n in (15, 17, 19)]
    for n in (15, 17, 19):
        field = GF(2**n, name="a")
        curve = EllipticCurve(field, [1, 1, 0, 0, 1])
        twist = EllipticCurve(field, [1, 0, 0, 0, 1])
        order = int(curve.cardinality())
        twist_order = int(twist.cardinality())
        manifest["twist_order_diagnostic"].append({
            "n": n, "curve_order": order, "curve_order_mod4": order % 4,
            "twist_order": twist_order, "twist_order_mod4": twist_order % 4,
            "sum": order + twist_order,
            "expected_sum": 2 * ((1 << n) + 1),
        })
    for n in (17, 19):
        field = GF(2**n, name="a")
        values, draws = _draw_additional_b(n, args.additional_seed, field)
        manifest["curve_selection_draws"][str(n)] = draws
        plan.append((n, 1, values[0], "seeded_additional"))
    manifest["curve_plan"] = [
        {"n": n, "a2": a2, "b": b, "family": family}
        for n, a2, b, family in plan
    ]
    _write_new(args.out_dir / "manifest.json", manifest)
    summaries = []
    for n, a2, b, family in plan:
        row = validate_curve(n, a2, b, args.samples_per_curve)
        row["family"] = family
        name = f"n{n}-a{a2}-b{b}.json"
        _write_new(args.out_dir / name, row)
        summaries.append({"file": name, "sha256": _sha256(args.out_dir / name),
                          "status": row["status"], "disagreement_count": row["disagreement_count"],
                          "samples_checked": row["samples_checked"], "wall_seconds": row["wall_seconds"]})
        print(json.dumps(summaries[-1], sort_keys=True), flush=True)
    conclusion = {
        "manifest_sha256": _sha256(args.out_dir / "manifest.json"),
        "rows": summaries,
        "total_points_checked": sum(row["samples_checked"] for row in summaries),
        "total_disagreements": sum(row["disagreement_count"] for row in summaries),
        "status": "agree" if all(row["status"] == "agree" for row in summaries) else "disagree",
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "claim_scope": "AP-3 predicate agreement on sampled admitted curves only; no relation or cost claim",
    }
    _write_new(args.out_dir / "summary.json", conclusion)
    print(json.dumps(conclusion, sort_keys=True))
    raise SystemExit(0 if conclusion["status"] == "agree" else 1)


if __name__ == "__main__":
    main()
