"""Frozen finite-field group-invariant census; run only from its trial plan."""

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

EXPERIMENT_ID = "EXP-ECTD-07b200"
RUN_ID = "RUN-ECTD-e5714e"
O = None


def primes():
    return [p for p in range(3, 65, 2)
            if all(p % d for d in range(2, math.isqrt(p) + 1))]


def character_table(p):
    table = [-1] * p
    table[0] = 0
    for y in range(1, p):
        table[y * y % p] = 1
    return table


def equation(x, p, a2, a4, a6):
    return (x**3 + a2 * x * x + a4 * x + a6) % p


def order_by_character(p, a2, a4, a6, chars):
    return 1 + sum(1 + chars[equation(x, p, a2, a4, a6)] for x in range(p))


def point_rows(p, a2, a4, a6):
    roots = [[] for _ in range(p)]
    for y in range(p):
        roots[y * y % p].append(y)
    return [{"x": x, "y": roots[equation(x, p, a2, a4, a6)]} for x in range(p)]


def j_and_delta(p, a2, a4, a6):
    b2, b4, b6 = 4 * a2, 2 * a4, 4 * a6
    b8 = 4 * a2 * a6 - a4 * a4
    c4 = (b2 * b2 - 24 * b4) % p
    delta = (-b2 * b2 * b8 - 8 * b4**3 - 27 * b6**2 + 9 * b2 * b4 * b6) % p
    return (c4**3 * pow(delta, -1, p)) % p if delta else None, delta


def quotient(p, a, b, r):
    if equation(r, p, 0, a, b) != 0:
        raise ValueError("kernel point is not rational 2-torsion")
    A = 3 * r % p
    B = (3 * r * r + a) % p
    c2, c4 = (-2 * A) % p, (A * A - 4 * B) % p
    if p == 3:
        if c2 != 0:
            raise ValueError("characteristic-3 quotient is not short")
        shift, short_a, short_b = 0, c4, 0
    else:
        inv3, inv27 = pow(3, -1, p), pow(27, -1, p)
        shift = c2 * inv3 % p  # w=u+c2/3
        short_a = (c4 - c2 * c2 * inv3) % p
        short_b = (-c2 * c4 * inv3 + 2 * c2**3 * inv27) % p
    return {"source_shift": r, "A": A, "B": B, "generalized_codomain": [c2, c4, 0],
            "short_codomain": [short_a, short_b], "codomain_shift": shift,
            "degree": 2, "kernel": [["O"], [r, 0]],
            "map": "X=x-r; u=X+A+B/X; v=y*(1-B/X^2); w=u+c2/3 (p>3); O,T->O"}


def is_squarefree(n):
    return all(n % (q * q) for q in range(2, math.isqrt(n) + 1))


def prime_square_witness(n):
    for q in range(2, math.isqrt(n) + 1):
        if n % (q * q) == 0 and all(q % d for d in range(2, math.isqrt(q) + 1)):
            return q
    return None


def select_instance():
    trace = []
    for p in primes():
        chars = character_table(p)
        for a in range(p):
            for b in range(p):
                source_j, source_delta = j_and_delta(p, 0, a, b)
                row = {"p": p, "a": a, "b": b, "source_delta": source_delta,
                       "source_j": source_j, "roots": [], "root_trials": []}
                if source_delta == 0:
                    row["rejection"] = "singular_source"
                    trace.append(row)
                    continue
                N = order_by_character(p, 0, a, b, chars)
                source_t = p + 1 - N
                row.update({"source_order": N, "source_trace": source_t,
                            "source_ordinary": source_t % p != 0})
                if source_t % p == 0:
                    row["rejection"] = "supersingular_source"
                    trace.append(row)
                    continue
                roots = [r for r in range(p) if equation(r, p, 0, a, b) == 0]
                row["roots"] = roots
                if not roots:
                    row["rejection"] = "no_rational_two_torsion"
                    trace.append(row)
                    continue
                for r in roots:
                    q = quotient(p, a, b, r)
                    qa, qb = q["short_codomain"]
                    codomain_j, codomain_delta = j_and_delta(p, 0, qa, qb)
                    attempt = {"r": r, "codomain_delta": codomain_delta,
                               "codomain_j": codomain_j}
                    if codomain_delta == 0:
                        attempt["rejection"] = "singular_codomain"
                    else:
                        N2 = order_by_character(p, 0, qa, qb, chars)
                        t2 = p + 1 - N2
                        attempt.update({"codomain_order": N2, "codomain_trace": t2,
                                        "codomain_ordinary": t2 % p != 0})
                        if N2 != N or t2 != source_t:
                            attempt["rejection"] = "trace_or_order_mismatch"
                        elif t2 % p == 0:
                            attempt["rejection"] = "supersingular_codomain"
                        elif codomain_j == source_j:
                            attempt["rejection"] = "same_j"
                        elif is_squarefree(N):
                            attempt["rejection"] = "squarefree_order"
                        else:
                            attempt["accepted"] = True
                    row["root_trials"].append(attempt)
                    if attempt.get("accepted"):
                        trace.append(row)
                        return {"p": p, "a": a, "b": b, "r": r, "quotient": q}, trace
                row["rejection"] = "all_roots_rejected"
                trace.append(row)
    return None, trace


def affine_points(rows):
    return [(row["x"], y) for row in rows for y in row["y"]]


def add(P, Q, p, a2, a4):
    if P is O:
        return Q
    if Q is O:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return O
    if P == Q:
        slope = (3 * x1 * x1 + 2 * a2 * x1 + a4) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - a2 - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def point_order(P, N, p, a2, a4):
    Q = O
    for k in range(1, N + 1):
        Q = add(Q, P, p, a2, a4)
        if Q is O:
            if N % k:
                raise ValueError("point order does not divide group order")
            return k
    raise ValueError("group law did not close within declared order")


def group_invariants(p, a2, a4, a6, rows):
    points = affine_points(rows)
    N = len(points) + 1
    exponent = 1
    orders = []
    for P in points:
        k = point_order(P, N, p, a2, a4)
        orders.append({"point": list(P), "order": k})
        exponent = math.lcm(exponent, k)
    factors = [exponent, N // exponent]
    valid = (N % exponent == 0 and factors[0] % factors[1] == 0
             and (p - 1) % factors[1] == 0)
    return {"order": N, "exponent": exponent, "factors": factors,
            "point_orders": orders, "invariant_laws_pass": valid}


def map_control(selected, source_rows, codomain_rows):
    p, r, q = selected["p"], selected["r"], selected["quotient"]
    A, B, shift = q["A"], q["B"], q["codomain_shift"]
    image = {O}
    kernel = []
    codomain = set(affine_points(codomain_rows))
    for x, y in affine_points(source_rows):
        X = (x - r) % p
        if X == 0:
            kernel.append((x, y))
            continue
        inv = pow(X, -1, p)
        w = (X + A + B * inv + shift) % p
        v = y * (1 - B * inv * inv) % p
        if (w, v) not in codomain:
            return {"pass": False, "kernel_affine": [list(P) for P in kernel]}
        image.add((w, v))
    return {"pass": kernel == [(r, 0)] and len(image) * 2 == len(affine_points(source_rows)) + 1,
            "kernel_affine": [list(P) for P in kernel], "image_size": len(image)}


def build_report():
    selected, trace = select_instance()
    report = {"schema": "crypto.autoresearch.ectd_group_invariants.v1",
              "experiment_id": EXPERIMENT_ID, "run_id": RUN_ID,
              "source_idea": "IDEA-20261005-1b41d9", "selection_trace": trace,
              "selected": selected}
    if selected is None:
        report.update({"valid": True, "reading_row": "negative_no_eligible_edge"})
        return report
    p, a, b = selected["p"], selected["a"], selected["b"]
    qa, qb = selected["quotient"]["short_codomain"]
    source_rows = point_rows(p, 0, a, b)
    codomain_rows = point_rows(p, 0, qa, qb)
    source = group_invariants(p, 0, a, b, source_rows)
    codomain = group_invariants(p, 0, qa, qb, codomain_rows)
    scaled_a, scaled_b = 16 * a % p, 64 * b % p
    scaled_rows = point_rows(p, 0, scaled_a, scaled_b)
    scaled = group_invariants(p, 0, scaled_a, scaled_b, scaled_rows)
    map_result = map_control(selected, source_rows, codomain_rows)
    source_points = affine_points(source_rows)
    scaled_points = set(affine_points(scaled_rows))
    scaled_image = {(4 * x % p, 8 * y % p) for x, y in source_points}
    scaling_bijection = (len(scaled_image) == len(source_points)
                         and scaled_image == scaled_points)
    source_j, source_delta = j_and_delta(p, 0, a, b)
    codomain_j, codomain_delta = j_and_delta(p, 0, qa, qb)
    generalized = selected["quotient"]["generalized_codomain"]
    generalized_j, _ = j_and_delta(p, *generalized)
    controls = {"selected_first_eligible": bool(trace[-1]["root_trials"][-1].get("accepted")),
                "source_ordinary": (p + 1 - source["order"]) % p != 0,
                "codomain_ordinary": (p + 1 - codomain["order"]) % p != 0,
                "same_trace_and_order": source["order"] == codomain["order"],
                "different_j": source_j != codomain_j,
                "nonsquarefree_order": not is_squarefree(source["order"]),
                "quotient_j_normalization": generalized_j == codomain_j,
                "kernel_and_map": map_result["pass"],
                "source_invariant_laws": source["invariant_laws_pass"],
                "codomain_invariant_laws": codomain["invariant_laws_pass"],
                "scaling_bijection": scaling_bijection,
                "scaling_invariant_pair": scaled["factors"] == source["factors"]}
    valid = all(controls.values()) and source_delta != 0 and codomain_delta != 0
    reading = "instrument_failure" if not valid else (
        "positive" if source["factors"] != codomain["factors"] else "negative_same_factors")
    report.update({"source": source, "codomain": codomain, "scaled_source": scaled,
                   "source_point_rows": source_rows, "codomain_point_rows": codomain_rows,
                   "scaled_point_rows": scaled_rows, "source_j": source_j,
                   "codomain_j": codomain_j, "source_delta": source_delta,
                   "codomain_delta": codomain_delta, "map_control": map_result,
                   "prime_square_witness": prime_square_witness(source["order"]),
                   "difference_coordinates": sum(x != y for x, y in zip(source["factors"], codomain["factors"])),
                   "controls": controls, "valid": valid, "reading_row": reading})
    return report


def write_run(run_dir):
    started = datetime.now(timezone.utc).isoformat()
    wall, cpu = time.perf_counter(), time.process_time()
    report = build_report()
    wall, cpu = time.perf_counter() - wall, time.process_time() - cpu
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_max
    if sys.platform != "darwin":
        peak *= 1024
    report["resources"] = {"wall_clock_seconds": wall, "cpu_seconds": cpu,
                           "peak_rss_bytes": peak}
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True).strip())
    digest = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest = {"run": {"id": RUN_ID, "experiment_id": EXPERIMENT_ID,
                        "hypothesis_id": "H-ECTD-2c0a3d", "goal_id": "GOAL-ECTD-001",
                        "task_id": "TASK-20261010-61e6fb", "status": "completed_unreviewed",
                        "recorded_at": started,
                        "code": {"commit": commit, "dirty": dirty,
                                 "command": "python3 experiments/EXP-ECTD-07b200/implementation/run.py --run-dir <run_dir>",
                                 "source_path": "experiments/EXP-ECTD-07b200/implementation/run.py",
                                 "source_sha256": digest},
                        "environment": {"python": platform.python_version(), "platform": platform.platform()},
                        "inputs": {"parameters": {"odd_prime_max": 64,
                                                  "curve_scan": "lex(p,a,b,r)",
                                                  "isogeny_degree": 2},
                                   "seeds": {"declared": []}},
                        "timing": {"wall_clock_seconds": wall, "cpu_seconds": cpu},
                        "resources": {"peak_rss_bytes": peak},
                        "result": {"validity_status": "pending_checker",
                                   "certificate": {"kind": "none", "verified": False},
                                   "metrics": {"selected": {k: report["selected"][k] for k in ("p", "a", "b", "r")}
                                               if report["selected"] else None,
                                               "source_factors": report.get("source", {}).get("factors"),
                                               "codomain_factors": report.get("codomain", {}).get("factors"),
                                               "reading_row": report["reading_row"]}},
                        "artifacts": {"raw_result": "raw-result.json", "stdout": "stdout.log",
                                      "stderr": "stderr.log", "environment": "environment.json",
                                      "command": "command.txt"}}}
    (run_dir / "manifest.yaml").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    write_run(Path(parser.parse_args().run_dir))


if __name__ == "__main__":
    main()
