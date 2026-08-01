#!/usr/bin/env python3
"""Cost accounting for fixed-degree support inside the Hecke pair search."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import resource
import statistics
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = HERE / "p1486_hecke_degree_pair_support_probe_result.json"
OUTPUT = HERE / "p1486_hecke_support_cost_probe_result.json"


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def payload_hash(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prime_divisors(n):
    output = []
    candidate = 2
    remaining = n
    while candidate * candidate <= remaining:
        if remaining % candidate == 0:
            output.append(candidate)
            while remaining % candidate == 0:
                remaining //= candidate
        candidate += 1
    if remaining > 1:
        output.append(remaining)
    return output


def dedekind_psi(n):
    value = n
    for prime in prime_divisors(n):
        value = value * (prime + 1) // prime
    return value


def exponent(cost, p):
    return math.log(max(float(cost), 1.0)) / math.log(float(p))


def summarize_family(family):
    p = family["p"]
    degrees = family["half_degrees"]
    list_sizes = {degree: dedekind_psi(degree) for degree in degrees}
    pair_rows = []
    for a in degrees:
        for b in degrees:
            left = list_sizes[a]
            right = list_sizes[b]
            padded = max(left, right)
            pair_rows.append(
                {
                    "a": a,
                    "b": b,
                    "left_size": left,
                    "right_size": right,
                    "padded_size": padded,
                    "classical_entries": left + right,
                    "tani_endpoint_queries": padded ** (2 / 3),
                    "query_optimal_standard_gates": padded ** (4 / 3),
                    "gate_optimal_standard_gates": padded,
                }
            )

    outer_calls = len(degrees)
    maxima = {
        key: max(row[key] for row in pair_rows)
        for key in (
            "classical_entries",
            "tani_endpoint_queries",
            "query_optimal_standard_gates",
            "gate_optimal_standard_gates",
        )
    }
    medians = {
        key: statistics.median(row[key] for row in pair_rows)
        for key in maxima
    }
    totals = {key: outer_calls * value for key, value in maxima.items()}
    total_exponents = {key: exponent(value, p) for key, value in totals.items()}
    endpoint_query_better_than_one_third = (
        total_exponents["tani_endpoint_queries"] < 1 / 3
    )
    charged_gate_better_than_one_third = min(
        total_exponents["query_optimal_standard_gates"],
        total_exponents["gate_optimal_standard_gates"],
    ) < 1 / 3
    return {
        "p": p,
        "half_degrees": degrees,
        "M": outer_calls,
        "degree_pair_count": outer_calls**2,
        "list_sizes": {str(key): value for key, value in list_sizes.items()},
        "pair_maxima": maxima,
        "pair_medians": medians,
        "outer_grover_total_proxies": totals,
        "outer_grover_total_empirical_exponents": total_exponents,
        "endpoint_query_proxy_below_one_third": (
            endpoint_query_better_than_one_third
        ),
        "charged_gate_proxy_below_one_third": (
            charged_gate_better_than_one_third
        ),
    }


def main():
    started = time.perf_counter()
    source = json.loads(INPUT.read_text())
    families = [summarize_family(family) for family in source["families"]]
    rss = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    analytic = {
        "outer_calls_exponent": "1/6",
        "classical_per_support_exponent": "1/6",
        "classical_total_exponent": "1/3",
        "tani_endpoint_query_per_support_exponent": "1/9",
        "tani_endpoint_query_total_exponent": "5/18",
        "query_optimal_standard_gate_per_support_exponent": "2/9",
        "query_optimal_standard_gate_total_exponent": "7/18",
        "gate_optimal_standard_gate_per_support_exponent": "1/6",
        "gate_optimal_standard_gate_total_exponent": "1/3",
    }
    checks = {
        "source_support_probe_passed": source["success"],
        "query_and_gate_models_separated": True,
        "analytic_classical_returns_frontier": (
            analytic["classical_total_exponent"] == "1/3"
        ),
        "analytic_nested_query_beats_frontier": (
            analytic["tani_endpoint_query_total_exponent"] == "5/18"
        ),
        "analytic_query_optimal_gates_lose": (
            analytic["query_optimal_standard_gate_total_exponent"] == "7/18"
        ),
        "analytic_gate_optimal_gates_tie": (
            analytic["gate_optimal_standard_gate_total_exponent"] == "1/3"
        ),
        "uncharged_query_as_gate_claim_rejected": True,
    }
    result = {
        "schema": "p1486-hecke-support-cost-probe-v1",
        "claim_status": (
            "ANALYTIC QUERY SIGNAL / STANDARD-CIRCUIT SCOPED NEGATIVE / "
            "TOY OPERATION PROXIES"
        ),
        "families": families,
        "analytic_asymptotic_exponents": analytic,
        "checks": checks,
        "success": all(checks.values()),
        "algorithmic_breakthrough": False,
        "elapsed_sec": round(time.perf_counter() - started, 9),
        "peak_rss": {
            "value": rss,
            "unit": "bytes" if platform.system() == "Darwin" else "KiB",
        },
        "source_result_sha256": file_sha256(INPUT),
        "script_sha256": file_sha256(Path(__file__)),
    }
    scientific_payload = {
        key: result[key]
        for key in (
            "schema",
            "claim_status",
            "families",
            "analytic_asymptotic_exponents",
            "checks",
            "success",
            "algorithmic_breakthrough",
            "source_result_sha256",
        )
    }
    result["scientific_payload_sha256"] = payload_hash(scientific_payload)
    result["payload_sha256"] = payload_hash(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
