"""Enumerate the frozen geometric SSIQ kernel census when dispatched.

This file defines the measurement. Importing it does not enumerate either
frozen curve. The Executor supplies --run-dir through the hash-bound plan.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from sage.all import EllipticCurve, GF, classical_modular_polynomial
from sage.version import version as sage_version

EXPERIMENT_ID = "EXP-SSIQ-dcb6d6"
RUN_ID = "RUN-SSIQ-9fe433"
PRIMES = (3, 5, 7)
ARMS = (("target", 1, 6, 22), ("null", 2, 3, 10))


def encode_element(value):
    """Preserve exact closure text and its finite-field embedding receipt."""
    field, element, embedding = value.as_finite_field_element()
    degree = int(field.degree())
    return {
        "closure_text": str(value),
        "minimal_polynomial": str(value.minpoly()),
        "finite_subfield_degree": degree,
        "finite_subfield_modulus": str(field.modulus()) if degree > 1 else None,
        "finite_subfield_element": str(element),
        "generator_image_in_closure": str(embedding(field.gen())),
    }


def enumerate_arm(closure, name, a, b, expected_discriminant):
    discriminant = (4 * a**3 + 27 * b**2) % 53
    curve = EllipticCurve(closure, [a, b])
    source_j = curve.j_invariant()
    rows = []
    exact_j = []
    checks = {"nonsingular": discriminant == expected_discriminant and discriminant != 0}
    counts = {}
    for ell in PRIMES:
        modular_polynomial = classical_modular_polynomial(ell)
        isogenies = list(curve.isogenies_prime_degree(ell))
        kernels = []
        for isogeny in isogenies:
            polynomial = isogeny.kernel_polynomial().monic()
            codomain_j = isogeny.codomain().j_invariant()
            relation_ok = modular_polynomial(source_j, codomain_j) == 0
            row = {
                "arm": name,
                "ell": ell,
                "isogeny_degree": int(isogeny.degree()),
                "kernel_polynomial": str(polynomial),
                "kernel_coefficients": [encode_element(c) for c in polynomial.list()],
                "kernel_degree": int(polynomial.degree()),
                "kernel_monic": polynomial.leading_coefficient() == 1,
                "codomain_j": encode_element(codomain_j),
                "modular_relation_zero": bool(relation_ok),
            }
            rows.append(row)
            kernels.append(polynomial)
            exact_j.append(codomain_j)
        counts[str(ell)] = len(isogenies)
        checks[f"ell_{ell}_complete"] = (
            len(isogenies) == ell + 1 and len(set(kernels)) == ell + 1
        )
        checks[f"ell_{ell}_kernel_degree"] = all(
            row["kernel_degree"] == (ell - 1) // 2
            and row["isogeny_degree"] == ell and row["kernel_monic"]
            for row in rows if row["ell"] == ell
        )
        checks[f"ell_{ell}_codomain_relation"] = all(
            row["modular_relation_zero"] for row in rows if row["ell"] == ell
        )
    j_text = [row["codomain_j"]["closure_text"] for row in rows]
    checks["j_text_injective_on_values"] = len(set(j_text)) == len(set(exact_j))
    kernel_text = [(row["ell"], row["kernel_polynomial"]) for row in rows]
    checks["kernel_text_injective_on_values"] = len(set(kernel_text)) == len(rows)
    groups = defaultdict(list)
    for row in rows:
        groups[row["codomain_j"]["closure_text"]].append(
            {"ell": row["ell"], "kernel_polynomial": row["kernel_polynomial"]}
        )
    return {
        "arm": name,
        "equation": f"y^2 = x^3 + {a}x + {b}",
        "discriminant_factor_mod_53": discriminant,
        "source_j": encode_element(source_j),
        "counts_by_degree": counts,
        "S": sum(row["kernel_degree"] for row in rows),
        "J": len(set(exact_j)),
        "checks": checks,
        "rows": rows,
        "codomain_collision_classes": dict(sorted(groups.items())),
    }


def build_report():
    closure = GF(53).algebraic_closure()
    arms = {}
    for name, a, b, expected_discriminant in ARMS:
        arms[name] = enumerate_arm(closure, name, a, b, expected_discriminant)
    all_checks_pass = all(value for arm in arms.values() for value in arm["checks"].values())
    target = arms["target"]
    threshold_base = max(1, target["J"])
    if not all_checks_pass:
        reading = "instrument_failure"
    elif target["S"] >= 4 * threshold_base:
        reading = "positive"
    elif target["S"] <= 3 * threshold_base:
        reading = "negative"
    else:
        reading = "inconclusive"
    return {
        "schema": "crypto.autoresearch.ssiq_kernel_storage.v1",
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "source_idea": "IDEA-20261007-20ae4e",
        "field": {
            "base": "GF(53)",
            "geometric": "Sage GF(53).algebraic_closure()",
            "construction": str(closure),
            "sage_version": sage_version,
            "element_receipts": "Each coefficient and j carries its finite subfield modulus and generator embedding.",
        },
        "degrees": list(PRIMES),
        "arms": arms,
        "all_checks_pass": all_checks_pass,
        "target_threshold_base": threshold_base,
        "reading_row": reading,
    }


def write_run(run_dir: Path):
    started_at = datetime.now(timezone.utc).isoformat()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    report = build_report()
    wall_seconds = time.perf_counter() - wall_start
    cpu_seconds = time.process_time() - cpu_start
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform != "darwin":
        peak_rss *= 1024
    report["resources"] = {
        "wall_clock_seconds": wall_seconds,
        "cpu_seconds": cpu_seconds,
        "peak_rss_bytes": peak_rss,
        "hostname": platform.node(),
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], text=True
    ).strip())
    # The supervisor adds command.txt, environment.json, stdout.log and stderr.log.
    # This envelope records producer provenance and observations, not a review.
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  id: {RUN_ID}\n"
        f"  experiment_id: {EXPERIMENT_ID}\n"
        "  hypothesis_id: H-SSIQ-4baf2b\n"
        "  goal_id: GOAL-SSIQ-001\n"
        "  task_id: TASK-20261010-626b30\n"
        "  status: completed_unreviewed\n"
        f"  recorded_at: {json.dumps(started_at)}\n"
        "  code:\n"
        f"    commit: {commit}\n"
        f"    dirty: {str(dirty).lower()}\n"
        "    command: sage -python experiments/EXP-SSIQ-dcb6d6/implementation/run.py --run-dir <run_dir>\n"
        "    source_path: experiments/EXP-SSIQ-dcb6d6/implementation/run.py\n"
        f"    source_sha256: {source_sha256}\n"
        "  environment:\n"
        f"    sage: {json.dumps(sage_version)}\n"
        f"    python: {json.dumps(platform.python_version())}\n"
        f"    platform: {json.dumps(platform.platform())}\n"
        "  inputs:\n"
        "    parameters: {characteristic: 53, prime_degrees: [3, 5, 7], kernel_scope: geometric}\n"
        "    seeds: {declared: []}\n"
        "  timing:\n"
        f"    wall_clock_seconds: {wall_seconds:.9f}\n"
        f"    cpu_seconds: {cpu_seconds:.9f}\n"
        "  resources:\n"
        f"    peak_rss_bytes: {peak_rss}\n"
        "  result:\n"
        "    validity_status: pending_checker\n"
        "    certificate: {kind: none, verified: false}\n"
        "    metrics:\n"
        f"      target_S: {report['arms']['target']['S']}\n"
        f"      target_J: {report['arms']['target']['J']}\n"
        f"      null_S: {report['arms']['null']['S']}\n"
        f"      null_J: {report['arms']['null']['J']}\n"
        f"      all_checks_pass: {str(report['all_checks_pass']).lower()}\n"
        f"      reading_row: {report['reading_row']}\n"
        "  artifacts:\n"
        "    raw_result: raw-result.json\n"
        "    stdout: stdout.log\n"
        "    stderr: stderr.log\n"
        "    environment: environment.json\n"
        "    command: command.txt\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    write_run(Path(args.run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
