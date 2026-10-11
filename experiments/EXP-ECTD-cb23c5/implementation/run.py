"""Frozen one-edge rational 2-isogeny census; executed only by the run skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

EXPERIMENT_ID = "EXP-ECTD-cb23c5"
RUN_ID = "RUN-ECTD-f96d04"


def is_prime(n):
    if n < 2:
        return False
    return all(n % d for d in range(2, math.isqrt(n) + 1))


def f(x, p):
    return (x**3 - 2 * x + 1) % p


def select_prime():
    trace = []
    for p in range(7, 256):
        if not is_prime(p):
            continue
        discriminant_factor = (4 * (-2) ** 3 + 27) % p
        roots = [x for x in range(p) if f(x, p) == 0]
        eligible = discriminant_factor != 0 and len(roots) == 1
        trace.append({"p": p, "prime": True, "discriminant_factor": discriminant_factor,
                      "roots": roots, "eligible": eligible})
        if eligible:
            return p, roots[0], trace
    return None, None, trace


def points_by_square_table(p, a2, a4, a6):
    squares = [[] for _ in range(p)]
    for y in range(p):
        squares[y * y % p].append(y)
    rows = []
    for x in range(p):
        rhs = (x**3 + a2 * x * x + a4 * x + a6) % p
        rows.append({"x": x, "y": squares[rhs]})
    return rows


def count_by_character_sum(p, a2, a4, a6):
    rows = []
    total = 1
    for x in range(p):
        rhs = (x**3 + a2 * x * x + a4 * x + a6) % p
        legendre = 0 if rhs == 0 else (1 if pow(rhs, (p - 1) // 2, p) == 1 else -1)
        total += 1 + legendre
        rows.append({"x": x, "rhs": rhs, "character": legendre, "fiber_size": 1 + legendre})
    return total, rows


def j_from_invariants(p, a2, a4, a6):
    b2 = 4 * a2
    b4 = 2 * a4
    b6 = 4 * a6
    b8 = 4 * a2 * a6 - a4 * a4
    c4 = (b2 * b2 - 24 * b4) % p
    delta = (-b2 * b2 * b8 - 8 * b4**3 - 27 * b6**2 + 9 * b2 * b4 * b6) % p
    if delta == 0:
        raise ValueError("singular curve")
    return (c4**3 * pow(delta, -1, p)) % p, delta


def quotient_from_kernel(p, r, y=0):
    if y % p != 0 or f(r, p) != 0:
        raise ValueError("kernel point must be rational 2-torsion")
    # With X=x-r, E is y^2=X(X^2+A X+B).  This is its degree-2
    # Vélu quotient, with map u=X+A+B/X, v=y(1-B/X^2).
    A = 3 * r % p
    B = (3 * r * r - 2) % p
    return {"translated_source": [A, B, 0], "source_shift": r,
            "kernel": [["O"], [r, 0]], "degree": 2,
            "codomain": [(-2 * A) % p, (A * A - 4 * B) % p, 0],
            "map": "u=X+A+B/X; v=y*(1-B/X^2); X=x-r; O,T -> O"}


def map_checks(p, r, A, B, codomain, source_points):
    a2, a4, a6 = codomain
    checked = 0
    image = {"O"}
    kernel_affine = []
    for row in source_points:
        x = row["x"]
        X = (x - r) % p
        for y in row["y"]:
            if X == 0:
                if y != 0:
                    return False, checked, 0, kernel_affine
                kernel_affine.append((x, y))
                continue
            u = (X + A + B * pow(X, -1, p)) % p
            v = (y * (1 - B * pow(X * X % p, -1, p))) % p
            if v * v % p != (u**3 + a2 * u * u + a4 * u + a6) % p:
                return False, checked, 0, kernel_affine
            checked += 1
            image.add((u, v))
    return True, checked, len(image), kernel_affine


def rational_map_identity(p, A, B, codomain):
    a2, a4, a6 = codomain
    for X in range(1, p):
        inverse = pow(X, -1, p)
        u = (X + A + B * inverse) % p
        source_rhs = (X**3 + A * X * X + B * X) % p
        lhs = source_rhs * (1 - B * inverse * inverse) ** 2 % p
        rhs = (u**3 + a2 * u * u + a4 * u + a6) % p
        if lhs != rhs:
            return False
    return True


def build_report():
    p, r, selection = select_prime()
    three_root_control = next(
        ({"p": q, "roots": roots, "rejected": len(roots) != 1}
         for q in range(7, 256) if is_prime(q)
         for roots in [[x for x in range(q) if f(x, q) == 0]]
         if len(roots) == 3), None
    )
    report = {"schema": "crypto.autoresearch.ectd_velu_control.v1",
              "experiment_id": EXPERIMENT_ID, "run_id": RUN_ID,
              "source_idea": "IDEA-20261006-783062", "selection_trace": selection,
              "selected_p": p, "kernel_root": r,
              "three_root_rejection_control": three_root_control}
    if p is None:
        report.update({"valid": True, "reading_row": "negative_no_eligible_prime",
                       "controls": {"exhaustive_selection": len(selection) > 0}})
        return report
    q = quotient_from_kernel(p, r)
    A, B, _ = q["translated_source"]
    a2, a4, a6 = q["codomain"]
    source_points = points_by_square_table(p, 0, -2, 1)
    source_order, source_character_rows = count_by_character_sum(p, 0, -2, 1)
    translated_points = points_by_square_table(p, A, B, 0)
    translated_order = 1 + sum(len(row["y"]) for row in translated_points)
    codomain_points = points_by_square_table(p, a2, a4, a6)
    codomain_order = 1 + sum(len(row["y"]) for row in codomain_points)
    source_j, source_delta = j_from_invariants(p, 0, -2, 1)
    translated_j, translated_delta = j_from_invariants(p, A, B, 0)
    codomain_j, codomain_delta = j_from_invariants(p, a2, a4, a6)
    mapping_ok, mapped_affine, image_size, kernel_affine = map_checks(
        p, r, A, B, q["codomain"], source_points
    )
    non_torsion = next(((row["x"], y) for row in source_points for y in row["y"] if y != 0), None)
    invalid_kernel_rejected = False
    if non_torsion is not None:
        try:
            quotient_from_kernel(p, *non_torsion)
        except ValueError:
            invalid_kernel_rejected = True
    controls = {
        "least_eligible_prime": selection[-1]["p"] == p and all(not row["eligible"] for row in selection[:-1]),
        "unique_rational_kernel": len(selection[-1]["roots"]) == 1 and r == selection[-1]["roots"][0],
        "three_root_candidate_rejected": three_root_control is not None and three_root_control["rejected"],
        "kernel_order_two": f(r, p) == 0 and (r, 0) in [(row["x"], y) for row in source_points for y in row["y"]]
        and p > 2,
        "degree_two": q["degree"] == 2 and B != 0 and kernel_affine == [(r, 0)]
        and source_order == 2 * image_size,
        "invalid_kernel_rejected": invalid_kernel_rejected,
        "source_count_crosscheck": source_order == 1 + sum(len(row["y"]) for row in source_points),
        "translated_model_null": translated_order == source_order and translated_j == source_j,
        "source_nonsingular": source_delta != 0,
        "translated_nonsingular": translated_delta != 0,
        "codomain_nonsingular": codomain_delta != 0,
        "map_equation_on_all_affine_points": mapping_ok,
        "map_rational_identity_all_nonzero_x": rational_map_identity(p, A, B, q["codomain"]),
        "map_separable": p > 2 and B != 0,
    }
    valid = all(controls.values())
    if not valid:
        reading = "instrument_failure"
    elif source_order != codomain_order:
        reading = "order_contradiction_requires_review"
    elif source_j == codomain_j:
        reading = "negative_same_j"
    else:
        reading = "positive"
    report.update({"valid": valid, "reading_row": reading, "kernel": [r, 0],
                   "quotient": q, "double_T": "O", "source_order": source_order,
                   "codomain_order": codomain_order, "source_j": source_j,
                   "translated_order": translated_order, "translated_j": translated_j,
                   "codomain_j": codomain_j, "source_discriminant": source_delta,
                   "translated_discriminant": translated_delta,
                   "codomain_discriminant": codomain_delta,
                   "orders_equal": source_order == codomain_order,
                   "j_different": source_j != codomain_j,
                   "source_character_rows": source_character_rows,
                   "source_point_rows": source_points,
                   "translated_point_rows": translated_points,
                   "codomain_point_rows": codomain_points,
                   "mapped_affine_points": mapped_affine,
                   "map_image_size": image_size, "kernel_affine": kernel_affine,
                   "controls": controls})
    return report


def write_run(run_dir):
    started_at = datetime.now(timezone.utc).isoformat()
    wall_start, cpu_start = time.perf_counter(), time.process_time()
    report = build_report()
    wall_seconds, cpu_seconds = time.perf_counter() - wall_start, time.process_time() - cpu_start
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_max
    if sys.platform != "darwin":
        peak_rss *= 1024
    report["resources"] = {"wall_clock_seconds": wall_seconds,
                           "cpu_seconds": cpu_seconds, "peak_rss_bytes": peak_rss}
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True).strip())
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest = {"run": {"id": RUN_ID, "experiment_id": EXPERIMENT_ID,
                        "hypothesis_id": "H-ECTD-e58462", "goal_id": "GOAL-ECTD-001",
                        "task_id": "TASK-20261010-7c2c5b", "status": "completed_unreviewed",
                        "recorded_at": started_at,
                        "code": {"commit": commit, "dirty": dirty,
                                 "command": "python3 experiments/EXP-ECTD-cb23c5/implementation/run.py --run-dir <run_dir>",
                                 "source_path": "experiments/EXP-ECTD-cb23c5/implementation/run.py",
                                 "source_sha256": source_hash},
                        "environment": {"python": platform.python_version(), "platform": platform.platform()},
                        "inputs": {"parameters": {"prime_min": 7, "prime_max_exclusive": 256,
                                                  "curve": [0, -2, 1], "kernel_degree": 2},
                                   "seeds": {"declared": []}},
                        "timing": {"wall_clock_seconds": wall_seconds, "cpu_seconds": cpu_seconds},
                        "resources": {"peak_rss_bytes": peak_rss},
                        "result": {"validity_status": "pending_checker",
                                   "certificate": {"kind": "none", "verified": False},
                                   "metrics": {"selected_p": report["selected_p"],
                                               "source_order": report.get("source_order"),
                                               "codomain_order": report.get("codomain_order"),
                                               "source_j": report.get("source_j"),
                                               "codomain_j": report.get("codomain_j"),
                                               "reading_row": report["reading_row"]}},
                        "artifacts": {"raw_result": "raw-result.json", "stdout": "stdout.log",
                                      "stderr": "stderr.log", "environment": "environment.json",
                                      "command": "command.txt"}}}
    # JSON is a YAML subset and avoids adding an execution-time YAML dependency.
    (run_dir / "manifest.yaml").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    write_run(Path(parser.parse_args().run_dir))


if __name__ == "__main__":
    main()
